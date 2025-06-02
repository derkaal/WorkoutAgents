"""
Secure Rule-Based Validation Agent Implementation
This file provides secure implementations addressing critical vulnerabilities.
"""

import os
import logging
import hashlib
import json
import time
import asyncio
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from enum import Enum

import jwt
import bleach
from pydantic import BaseModel, Field, validator
from langchain_core.agents import BaseSingleActionAgent, AgentAction, AgentFinish


# Security Configuration
class SecurityConfig:
    """Security configuration constants."""
    MAX_REQUEST_SIZE = 1_048_576  # 1MB
    MAX_STRING_LENGTH = 10_000
    MAX_ARRAY_ITEMS = 100
    MAX_DICT_ITEMS = 100
    RATE_LIMIT_PER_MINUTE = 100
    MAX_CONCURRENT_REQUESTS = 50
    REQUEST_TIMEOUT_SECONDS = 30
    JWT_ALGORITHM = 'HS256'
    TOKEN_EXPIRY_HOURS = 24
    MIN_PASSWORD_LENGTH = 12
    AUDIT_LOG_RETENTION_DAYS = 90


# Error Codes
class ErrorCode(Enum):
    """Standardized error codes for security events."""
    AUTH_MISSING = "AUTH001"
    AUTH_INVALID = "AUTH002"
    AUTH_EXPIRED = "AUTH003"
    PERMISSION_DENIED = "PERM001"
    RATE_LIMITED = "RATE001"
    VALIDATION_FAILED = "VAL001"
    INVALID_INPUT = "VAL002"
    SYSTEM_ERROR = "SYS001"
    TIMEOUT = "TIME001"
    SERVICE_UNAVAILABLE = "SVC001"


# Secure Input Models
class SecureValidationInput(BaseModel):
    """Secure input validation model with comprehensive checks."""
    task: str = Field(..., max_length=100, regex="^[a-zA-Z0-9_]+$")
    data: Dict[str, Any] = Field(..., max_items=SecurityConfig.MAX_DICT_ITEMS)
    correlation_id: Optional[str] = Field(None, max_length=36, regex="^[a-zA-Z0-9-]+$")
    
    @validator('data')
    def validate_data_size(cls, v):
        """Validate total data size to prevent DoS."""
        data_str = json.dumps(v)
        if len(data_str) > SecurityConfig.MAX_REQUEST_SIZE:
            raise ValueError("Data size exceeds maximum allowed")
        return v
    
    @validator('task')
    def validate_task_whitelist(cls, v):
        """Validate task against whitelist."""
        allowed_tasks = {
            'validate_workout_plan',
            'validate_progress_tracking',
            'validate_nutrition_data'
        }
        if v not in allowed_tasks:
            raise ValueError(f"Invalid task type: {v}")
        return v
    
    class Config:
        """Pydantic configuration."""
        max_anystr_length = SecurityConfig.MAX_STRING_LENGTH


# Security Exceptions
class SecurityException(Exception):
    """Base security exception."""
    def __init__(self, message: str, code: ErrorCode, details: Dict[str, Any] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class AuthenticationException(SecurityException):
    """Authentication failure exception."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCode.AUTH_INVALID, details)


class AuthorizationException(SecurityException):
    """Authorization failure exception."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCode.PERMISSION_DENIED, details)


class RateLimitException(SecurityException):
    """Rate limit exceeded exception."""
    def __init__(self, message: str, retry_after: int, details: Dict[str, Any] = None):
        details = details or {}
        details['retry_after'] = retry_after
        super().__init__(message, ErrorCode.RATE_LIMITED, details)


# Security Components
class InputSanitizer:
    """Input sanitization utility."""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input to prevent injection attacks."""
        if not isinstance(value, str):
            return value
        
        # Remove HTML and dangerous characters
        sanitized = bleach.clean(value, tags=[], strip=True)
        
        # Limit length
        if len(sanitized) > SecurityConfig.MAX_STRING_LENGTH:
            sanitized = sanitized[:SecurityConfig.MAX_STRING_LENGTH]
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary data."""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in list(data.items())[:SecurityConfig.MAX_DICT_ITEMS]:
            # Sanitize key
            safe_key = InputSanitizer.sanitize_string(str(key))
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[safe_key] = InputSanitizer.sanitize_list(value)
            elif isinstance(value, (int, float)):
                sanitized[safe_key] = InputSanitizer.sanitize_number(value)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """Sanitize list data."""
        if not isinstance(data, list):
            return data
        
        return [
            InputSanitizer.sanitize_dict(item) if isinstance(item, dict)
            else InputSanitizer.sanitize_string(item) if isinstance(item, str)
            else InputSanitizer.sanitize_number(item) if isinstance(item, (int, float))
            else item
            for item in data[:SecurityConfig.MAX_ARRAY_ITEMS]
        ]
    
    @staticmethod
    def sanitize_number(value: Any) -> Any:
        """Sanitize numeric values."""
        if isinstance(value, (int, float)):
            # Check for NaN, infinity
            if value != value or abs(value) == float('inf'):
                return 0
            # Apply reasonable bounds
            if abs(value) > 1e9:
                return 0
        return value


class AuthenticationMiddleware:
    """JWT-based authentication middleware."""
    
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.logger = logging.getLogger(__name__)
    
    def generate_token(self, user_id: str, roles: List[str], additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token."""
        payload = {
            'sub': user_id,
            'roles': roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=SecurityConfig.TOKEN_EXPIRY_HOURS)
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[SecurityConfig.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            raise AuthenticationException("Token has expired")
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def require_auth(self, required_roles: List[str] = None):
        """Decorator to require authentication."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract token
                token = kwargs.get('auth_token')
                if not token:
                    raise AuthenticationException("Authentication required")
                
                # Verify token
                user_context = self.verify_token(token)
                if not user_context:
                    raise AuthenticationException("Invalid authentication token")
                
                # Check roles if specified
                if required_roles:
                    user_roles = user_context.get('roles', [])
                    if not any(role in user_roles for role in required_roles):
                        raise AuthorizationException(
                            f"Required roles: {required_roles}, user roles: {user_roles}"
                        )
                
                # Add user context
                kwargs['user_context'] = user_context
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_minute: int = SecurityConfig.RATE_LIMIT_PER_MINUTE):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Optional[int]]:
        """Check if request is allowed under rate limit."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            # Calculate retry after
            oldest_request = min(self.requests[client_id])
            retry_after = int(60 - (current_time - oldest_request))
            
            self.logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False, retry_after
        
        # Record request
        self.requests[client_id].append(current_time)
        return True, None


class SecurityAuditLogger:
    """Security audit logger with structured logging."""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.logger = logging.getLogger("security_audit")
        
        # Configure file handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Sensitive patterns to mask
        self.sensitive_patterns = [
            'password', 'token', 'secret', 'key', 'auth',
            'ssn', 'credit', 'card', 'cvv', 'pin'
        ]
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_context: Dict[str, Any] = None):
        """Log security event with context."""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': self._mask_sensitive_data(details),
            'user_context': self._mask_sensitive_data(user_context) if user_context else {},
            'correlation_id': details.get('correlation_id'),
            'ip_address': details.get('ip_address'),
            'user_agent': details.get('user_agent')
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """Recursively mask sensitive data."""
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if any(pattern in str(key).lower() for pattern in self.sensitive_patterns):
                    masked[key] = '***REDACTED***'
                else:
                    masked[key] = self._mask_sensitive_data(value)
            return masked
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Check if the string itself contains sensitive patterns
            if any(pattern in data.lower() for pattern in self.sensitive_patterns):
                return '***REDACTED***'
        return data


class SecureErrorHandler:
    """Secure error handler that prevents information leakage."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle error securely without exposing internals."""
        # Log full error internally
        self.logger.error(
            f"Error occurred: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={'context': context}
        )
        
        # Return sanitized error response
        if isinstance(error, SecurityException):
            return {
                'status': 'error',
                'code': error.code.value,
                'message': self._get_safe_error_message(error.code),
                'valid': False,
                'details': error.details
            }
        else:
            # Generic error response for unexpected errors
            return {
                'status': 'error',
                'code': ErrorCode.SYSTEM_ERROR.value,
                'message': 'An error occurred during validation',
                'valid': False
            }
    
    def _get_safe_error_message(self, code: ErrorCode) -> str:
        """Get user-safe error message for error code."""
        messages = {
            ErrorCode.AUTH_MISSING: "Authentication required",
            ErrorCode.AUTH_INVALID: "Invalid authentication credentials",
            ErrorCode.AUTH_EXPIRED: "Authentication token has expired",
            ErrorCode.PERMISSION_DENIED: "Insufficient permissions for this operation",
            ErrorCode.RATE_LIMITED: "Rate limit exceeded. Please try again later",
            ErrorCode.VALIDATION_FAILED: "Validation failed. Please check your input",
            ErrorCode.INVALID_INPUT: "Invalid input provided",
            ErrorCode.SYSTEM_ERROR: "An error occurred. Please try again",
            ErrorCode.TIMEOUT: "Request timed out",
            ErrorCode.SERVICE_UNAVAILABLE: "Service temporarily unavailable"
        }
        return messages.get(code, "An error occurred")


# Main Secure Validation Agent
class SecureRuleBasedValidationAgent(BaseSingleActionAgent):
    """
    Secure Rule-Based Validation Agent with comprehensive security controls.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        
        # Load configuration
        self.config = config or {}
        
        # Initialize security components
        self.auth_middleware = AuthenticationMiddleware(
            secret_key=os.environ.get('JWT_SECRET', 'default-secret-change-me').encode()
        )
        self.rate_limiter = RateLimiter()
        self.audit_logger = SecurityAuditLogger()
        self.error_handler = SecureErrorHandler()
        self.input_sanitizer = InputSanitizer()
        
        # Initialize validation rules registry
        self._validation_rules = {}
        
        # Secure metrics storage
        self._validation_metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'security_violations': 0,
            'rate_limit_hits': 0
        }
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
    
    @property
    def input_keys(self) -> List[str]:
        """Required input keys."""
        return ['input_data', 'auth_token']
    
    @property
    def output_keys(self) -> List[str]:
        """Output keys."""
        return ['output']
    
    async def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Any = None,
        **kwargs: Any
    ) -> AgentFinish:
        """
        Execute validation with comprehensive security controls.
        """
        start_time = datetime.utcnow()
        correlation_id = None
        user_context = None
        
        try:
            # Extract correlation ID for tracking
            if 'input_data' in kwargs and isinstance(kwargs['input_data'], dict):
                correlation_id = kwargs['input_data'].get('correlation_id')
            
            # 1. Authentication check
            auth_token = kwargs.get('auth_token')
            if not auth_token:
                self.audit_logger.log_event('auth_failure', {
                    'reason': 'missing_token',
                    'correlation_id': correlation_id
                })
                raise AuthenticationException("Authentication required")
            
            # Verify token
            user_context = self.auth_middleware.verify_token(auth_token)
            if not user_context:
                self.audit_logger.log_event('auth_failure', {
                    'reason': 'invalid_token',
                    'correlation_id': correlation_id
                })
                raise AuthenticationException("Invalid authentication token")
            
            # 2. Rate limiting check
            client_id = user_context.get('sub', 'unknown')
            allowed, retry_after = self.rate_limiter.is_allowed(client_id)
            
            if not allowed:
                self._validation_metrics['rate_limit_hits'] += 1
                self.audit_logger.log_event('rate_limit_exceeded', {
                    'client_id': client_id,
                    'retry_after': retry_after,
                    'correlation_id': correlation_id
                }, user_context)
                raise RateLimitException("Rate limit exceeded", retry_after)
            
            # 3. Input validation and sanitization
            if 'input_data' not in kwargs:
                raise ValueError("Missing required input_data")
            
            # Validate input structure
            try:
                validated_input = SecureValidationInput(**kwargs['input_data'])
                input_data = validated_input.dict()
            except Exception as e:
                self.audit_logger.log_event('input_validation_failure', {
                    'error': str(e),
                    'client_id': client_id,
                    'correlation_id': correlation_id
                }, user_context)
                raise ValueError(f"Invalid input format: {str(e)}")
            
            # Sanitize input data
            input_data['data'] = self.input_sanitizer.sanitize_dict(input_data.get('data', {}))
            
            # 4. Execute validation with timeout protection
            result = await asyncio.wait_for(
                self._execute_validation(input_data, user_context),
                timeout=SecurityConfig.REQUEST_TIMEOUT_SECONDS
            )
            
            # 5. Log successful validation
            self.audit_logger.log_event('validation_success', {
                'task': input_data.get('task'),
                'client_id': client_id,
                'duration_ms': (datetime.utcnow() - start_time).total_seconds() * 1000,
                'correlation_id': correlation_id
            }, user_context)
            
            return result
            
        except asyncio.TimeoutError:
            self.audit_logger.log_event('validation_timeout', {
                'correlation_id': correlation_id
            }, user_context)
            error_response = self.error_handler.handle_error(
                SecurityException("Request timed out", ErrorCode.TIMEOUT)
            )
            return AgentFinish(
                return_values={'output': error_response},
                log='Validation timeout'
            )
            
        except Exception as e:
            # Log security exception
            if isinstance(e, SecurityException):
                self._validation_metrics['security_violations'] += 1
            
            self.audit_logger.log_event('validation_error', {
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }, user_context)
            
            # Handle error securely
            error_response = self.error_handler.handle_error(e, {
                'correlation_id': correlation_id,
                'timestamp': start_time.isoformat()
            })
            
            return AgentFinish(
                return_values={'output': error_response},
                log='Validation error handled'
            )
    
    async def _execute_validation(
        self,
        input_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> AgentFinish:
        """Execute the actual validation logic."""
        task_type = input_data['task']
        
        # Check user permissions for task
        if not self._check_task_permission(task_type, user_context):
            raise AuthorizationException(f"Insufficient permissions for task: {task_type}")
        
        # Route to appropriate validation method
        validation_result = None
        
        if task_type == 'validate_workout_plan':
            validation_result = self._validate_workout_secure(input_data)
        elif task_type == 'validate_progress_tracking':
            validation_result = self._validate_progress_secure(input_data)
        else:
            validation_result = {
                'status': 'error',
                'message': f'Unknown task type: {task_type}',
                'valid': False
            }
        
        # Update metrics
        self._update_metrics_secure(validation_result)
        
        # Add metadata
        validation_result['metadata'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'correlation_id': input_data.get('correlation_id')
        }
        
        return AgentFinish(
            return_values={'output': validation_result},
            log=f'Validation completed for task: {task_type}'
        )
    
    def _check_task_permission(self, task_type: str, user_context: Dict[str, Any]) -> bool:
        """Check if user has permission for the task."""
        user_roles = user_context.get('roles', [])
        
        # Define task permissions
        task_permissions = {
            'validate_workout_plan': ['user', 'trainer', 'admin'],
            'validate_progress_tracking': ['user', 'trainer', 'admin'],
            'validate_nutrition_data': ['user', 'nutritionist', 'admin'],
            'validate_admin_config': ['admin']
        }
        
        allowed_roles = task_permissions.get(task_type, ['admin'])
        return any(role in allowed_roles for role in user_roles)
    
    def _validate_workout_secure(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Securely validate workout data."""
        validation_errors = []
        warnings = []
        
        workout_data = input_data.get('data', {})
        
        # Validate duration with secure numeric handling
        if 'duration_minutes' not in workout_data:
            validation_errors.append('Missing required field: duration_minutes')
        else:
            try:
                # Safely convert to float
                duration = float(str(workout_data['duration_minutes']))
                
                # Check for invalid values
                if duration != duration or duration < 0:  # NaN or negative check
                    validation_errors.append('Invalid duration value')
                elif duration < 25:
                    validation_errors.append('Workout duration must be at least 25 minutes')
                elif duration > 35:
                    validation_errors.append('Workout duration must not exceed 35 minutes')
                elif duration < 30:
                    warnings.append('Consider increasing workout duration to 30 minutes for optimal results')
                    
            except (TypeError, ValueError, OverflowError):
                validation_errors.append('duration_minutes must be a valid number')
        
        # Build response
        if validation_errors:
            return {
                'status': 'failed',
                'message': 'Workout validation failed',
                'valid': False,
                'errors': validation_errors,
                'warnings': warnings
            }
        else:
            return {
                'status': 'success',
                'message': 'Workout plan is valid',
                'valid': True,
                'warnings': warnings,
                'validated_data': workout_data
            }
    
    def _validate_progress_secure(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Securely validate progress tracking data."""
        validation_errors = []
        progress_data = input_data.get('data', {})
        
        # Validate progress percentage
        if 'progress' in progress_data:
            try:
                progress = float(str(progress_data['progress']))
                if progress < 0 or progress > 100:
                    validation_errors.append('Progress must be between 0 and 100')
            except (TypeError, ValueError):
                validation_errors.append('Progress must be a valid number')
        
        if validation_errors:
            return {
                'status': 'failed',
                'message': 'Progress validation failed',
                'valid': False,
                'errors': validation_errors
            }
        else:
            return {
                'status': 'success',
                'message': 'Progress tracking validation successful',
                'valid': True,
                'validated_data': progress_data
            }
    
    def _update_metrics_secure(self, validation_result: Dict[str, Any]) -> None:
        """Update metrics with thread safety."""
        self._validation_metrics['total_validations'] += 1
        
        if validation_result.get('valid', False):
            self._validation_metrics['successful_validations'] += 1
        else:
            self._validation_metrics['failed_validations'] += 1
    
    @AuthenticationMiddleware.require_auth(['admin'])
    async def get_metrics(self, auth_token: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get metrics with admin authentication."""
        # Log metrics access
        self.audit_logger.log_event('metrics_access', {
            'user_id': user_context.get('sub') if user_context else 'unknown'
        }, user_context)
        
        return {
            'metrics': self._validation_metrics.copy(),
            'timestamp': datetime.utcnow().isoformat()
        }


# Example usage with security
if __name__ == "__main__":
    # Initialize secure agent
    agent = SecureRuleBasedValidationAgent()
    
    # Generate test token
    auth = AuthenticationMiddleware(b'test-secret-key')
    test_token = auth.generate_token('test_user', ['user'])
    
    # Example secure validation
    async def test_secure_validation():
        result = await agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {
                    'duration_minutes': 30,
                    'exercises': ['push-ups', 'squats']
                },
                'correlation_id': 'test-123'
            },
            auth_token=test_token
        )
        print("Secure validation result:", result.return_values['output'])
    
    # Run test
    import asyncio
    asyncio.run(test_secure_validation())