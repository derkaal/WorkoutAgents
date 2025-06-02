# Rule-Based Validation Agent API Documentation

## Overview

The Rule-Based Validation Agent provides a secure, RESTful API for validating data against configurable business rules. All endpoints require authentication and respect rate limits.

## Base URL

```
https://api.example.com/api/v1/validation
```

## Authentication

All API requests require JWT authentication:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```python
from secure_validation_agent_implementation import AuthenticationMiddleware

auth = AuthenticationMiddleware(b'your-secret-key')
token = auth.generate_token(
    user_id='user123',
    roles=['user', 'trainer'],
    additional_claims={'org_id': 'org456'}
)
```

## API Endpoints

### 1. Validate Data

Perform synchronous validation against configured rules.

**Endpoint:** `POST /validate`

**Request:**

```json
{
  "task": "validate_workout_plan",
  "data": {
    "duration_minutes": 30,
    "exercises": ["push-ups", "squats", "lunges"],
    "intensity": "moderate"
  },
  "correlation_id": "req-123-456"
}
```

**Response (Success):**

```json
{
  "valid": true,
  "status": "success",
  "message": "Workout plan is valid",
  "warnings": [
    "Consider adding cardio exercises for balanced workout"
  ],
  "validated_data": {
    "duration_minutes": 30,
    "exercises": ["push-ups", "squats", "lunges"],
    "intensity": "moderate"
  },
  "metadata": {
    "timestamp": "2025-05-30T00:00:00Z",
    "correlation_id": "req-123-456",
    "execution_time_ms": 45.2,
    "rules_applied": 5
  }
}
```

**Response (Validation Failed):**

```json
{
  "valid": false,
  "status": "failed",
  "message": "Workout validation failed",
  "errors": [
    "Workout duration must be at least 25 minutes"
  ],
  "warnings": [],
  "metadata": {
    "timestamp": "2025-05-30T00:00:00Z",
    "correlation_id": "req-123-456"
  }
}
```

**Response (Error):**

```json
{
  "status": "error",
  "code": "VAL001",
  "message": "Validation failed. Please check your input.",
  "valid": false,
  "details": {
    "retry_after": 30
  }
}
```

### 2. Async Validation

Submit validation for asynchronous processing.

**Endpoint:** `POST /validate/async`

**Request:**

```json
{
  "task": "validate_progress_tracking",
  "data": {
    "user_id": "user123",
    "progress": 75,
    "completed_workouts": 15,
    "week": 3
  },
  "callback_url": "https://your-app.com/webhook/validation",
  "correlation_id": "async-req-789"
}
```

**Response:**

```json
{
  "job_id": "job-abc-123",
  "status": "queued",
  "estimated_completion": "2025-05-30T00:01:00Z",
  "correlation_id": "async-req-789"
}
```

### 3. Get Validation Metrics

Retrieve validation metrics (requires admin role).

**Endpoint:** `GET /metrics`

**Response:**

```json
{
  "metrics": {
    "total_validations": 15234,
    "successful_validations": 14892,
    "failed_validations": 342,
    "security_violations": 12,
    "rate_limit_hits": 45
  },
  "timestamp": "2025-05-30T00:00:00Z"
}
```

### 4. Health Check

Check service health status.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "uptime_seconds": 86400,
  "dependencies": {
    "database": "healthy",
    "cache": "healthy",
    "message_broker": "healthy"
  }
}
```

## Validation Tasks

### Available Tasks

1. **validate_workout_plan**
   - Validates workout duration, exercises, and intensity
   - Required fields: `duration_minutes`, `exercises`
   - Optional fields: `intensity`, `target_muscles`, `equipment`

2. **validate_progress_tracking**
   - Validates user progress data
   - Required fields: `progress`, `user_id`
   - Optional fields: `completed_workouts`, `week`, `notes`

3. **validate_nutrition_data**
   - Validates nutrition information (requires nutritionist role)
   - Required fields: `calories`, `meal_type`
   - Optional fields: `macros`, `ingredients`, `allergens`

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| AUTH001 | Authentication required | 401 |
| AUTH002 | Invalid authentication token | 401 |
| AUTH003 | Token expired | 401 |
| PERM001 | Insufficient permissions | 403 |
| RATE001 | Rate limit exceeded | 429 |
| VAL001 | Validation failed | 400 |
| VAL002 | Invalid input format | 400 |
| SYS001 | Internal system error | 500 |
| TIME001 | Request timeout | 408 |
| SVC001 | Service unavailable | 503 |

## Rate Limiting

Default rate limits:
- 100 requests per minute per user
- 1000 requests per hour per user
- 10000 requests per day per user

Rate limit headers in response:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1622476800
```

## Code Examples

### Python Example

```python
import asyncio
import aiohttp
import json

async def validate_workout():
    url = "https://api.example.com/api/v1/validation/validate"
    headers = {
        "Authorization": "Bearer your-jwt-token",
        "Content-Type": "application/json"
    }
    
    payload = {
        "task": "validate_workout_plan",
        "data": {
            "duration_minutes": 30,
            "exercises": ["push-ups", "squats"],
            "intensity": "moderate"
        },
        "correlation_id": "py-example-001"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.json()
            
            if result.get('valid'):
                print("Validation successful!")
                print(f"Warnings: {result.get('warnings', [])}")
            else:
                print("Validation failed!")
                print(f"Errors: {result.get('errors', [])}")

# Run the validation
asyncio.run(validate_workout())
```

### JavaScript Example

```javascript
async function validateWorkout() {
    const url = 'https://api.example.com/api/v1/validation/validate';
    const token = 'your-jwt-token';
    
    const payload = {
        task: 'validate_workout_plan',
        data: {
            duration_minutes: 30,
            exercises: ['push-ups', 'squats'],
            intensity: 'moderate'
        },
        correlation_id: 'js-example-001'
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.valid) {
            console.log('Validation successful!');
            console.log('Warnings:', result.warnings);
        } else {
            console.log('Validation failed!');
            console.log('Errors:', result.errors);
        }
    } catch (error) {
        console.error('Validation error:', error);
    }
}

// Call the function
validateWorkout();
```

### cURL Example

```bash
curl -X POST https://api.example.com/api/v1/validation/validate \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "validate_workout_plan",
    "data": {
      "duration_minutes": 30,
      "exercises": ["push-ups", "squats"],
      "intensity": "moderate"
    },
    "correlation_id": "curl-example-001"
  }'
```

## Webhooks

For async validation, configure webhooks to receive results:

### Webhook Payload

```json
{
  "job_id": "job-abc-123",
  "correlation_id": "async-req-789",
  "status": "completed",
  "result": {
    "valid": true,
    "status": "success",
    "message": "Validation completed successfully",
    "warnings": [],
    "metadata": {
      "timestamp": "2025-05-30T00:01:00Z",
      "execution_time_ms": 125.4
    }
  }
}
```

### Webhook Security

Webhooks include HMAC signature for verification:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Best Practices

1. **Always include correlation IDs** for request tracking
2. **Handle rate limits gracefully** with exponential backoff
3. **Validate input client-side** before API calls
4. **Cache validation results** when appropriate
5. **Use async validation** for large datasets
6. **Monitor webhook failures** and implement retry logic
7. **Rotate JWT tokens** regularly
8. **Log all validation failures** for audit purposes

## SDK Support

Official SDKs available:
- Python: `pip install validation-agent-sdk`
- JavaScript/Node.js: `npm install @validation-agent/sdk`
- Java: `com.example:validation-agent-sdk:1.2.3`
- Go: `go get github.com/example/validation-agent-go`

## Support

- API Status: https://status.example.com
- Documentation: https://docs.example.com/validation-agent
- Support: support@example.com