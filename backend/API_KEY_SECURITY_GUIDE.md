# API Key Security Guide

## Security Risks Identified

During a security audit of the Workout Agents application, the following critical issues were identified:

1. **Exposed API Keys in Source Code**: API keys for OpenAI and Mistral were directly embedded in the `.env` file and committed to version control.

2. **Lack of API Key Validation**: No validation was performed to ensure API keys meet minimum security requirements.

3. **Missing Environment Variable Documentation**: The `.env.example` file was incomplete, missing entries for some required API keys.

## Why Sharing API Keys is a Security Risk

Exposing API keys in messages, code, or repositories creates several serious security vulnerabilities:

1. **Unauthorized Access**: Anyone with your API key can make requests on your behalf, potentially:
   - Consuming your usage quota and incurring unexpected charges
   - Accessing sensitive data through your account
   - Performing malicious actions that appear to come from you

2. **Data Breaches**: Exposed keys can lead to unauthorized access to user data, violating privacy regulations like GDPR or CCPA.

3. **Service Abuse**: Attackers can use your keys to:
   - Send spam or malicious content through services like ElevenLabs
   - Generate harmful AI content that violates terms of service
   - Perform denial-of-service attacks against your account

4. **Financial Impact**: Unauthorized API usage can result in:
   - Unexpected billing charges
   - Account suspension due to unusual activity
   - Potential liability for data breaches

5. **Reputation Damage**: Security incidents can harm your professional reputation and user trust.

## Secure Implementation for API Keys

### 1. Proper Storage in .env Files

The `.env` file should:
- Never be committed to version control
- Contain only placeholder values in example files
- Be properly listed in `.gitignore`

Example of a secure `.env` file:
```
# OpenAI API Key
OPENAI_API_KEY="your-actual-api-key"

# Mistral API Key
MISTRAL_API_KEY="your-actual-mistral-key"

# ElevenLabs API Key
ELEVENLABS_API_KEY="your-actual-elevenlabs-key"
```

### 2. Loading Environment Variables Securely

Use `python-dotenv` to load environment variables:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
api_key = os.getenv("ELEVENLABS_API_KEY")
```

### 3. Environment Variable Validation

Implement validation to ensure API keys are present and meet security requirements:

```python
from pydantic import BaseModel, Field, validator

class EnvironmentConfig(BaseModel):
    elevenlabs_api_key: str = Field(..., min_length=32)
    
    @validator("elevenlabs_api_key")
    def validate_api_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("ElevenLabs API key is missing or invalid")
        return v
```

### 4. Secure API Key Usage

When making API calls:
- Never log or display API keys
- Use HTTPS for all API requests
- Handle API responses securely

```python
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": config.elevenlabs_api_key
}

try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.content
except requests.exceptions.RequestException as e:
    print(f"Error calling ElevenLabs API: {e}")
    # Don't log the full exception which might contain the API key
    return None
```

## Additional Security Measures

### 1. API Key Rotation

- Regularly rotate API keys (every 30-90 days)
- Immediately rotate keys if a potential exposure is detected
- Implement a process for secure key rotation

### 2. Environment-Specific Keys

- Use different API keys for development, testing, and production
- Limit the scope and permissions of development keys

### 3. Secret Management Services

For production environments, consider using:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager

### 4. Runtime Environment Validation

Implement startup checks to validate the environment:

```python
def validate_environment():
    """Validate all required environment variables on application startup."""
    required_vars = ["OPENAI_API_KEY", "MISTRAL_API_KEY", "ELEVENLABS_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
```

### 5. API Key Usage Monitoring

- Implement logging for API key usage
- Set up alerts for unusual activity
- Monitor API usage against expected patterns

## Immediate Actions Required

1. **Revoke Exposed Keys**: The OpenAI and Mistral API keys in the `.env` file have been exposed and should be revoked immediately.

2. **Generate New Keys**: Create new API keys for all services after revoking the exposed ones.

3. **Update Environment Files**: Ensure `.env` files contain only placeholder values in repositories.

4. **Implement Validation**: Add environment variable validation to the application startup.

5. **Security Audit**: Conduct a thorough security audit to identify any other potential vulnerabilities.

## Conclusion

Proper API key management is essential for maintaining the security and integrity of your application. By following the guidelines in this document, you can significantly reduce the risk of unauthorized access and potential security breaches.

The example implementation provided in `elevenlabs_example.py` demonstrates these best practices and can serve as a template for secure API key handling throughout your application.