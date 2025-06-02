"""
Environment Validator Module

This module provides utilities for validating environment variables
at application startup, ensuring all required API keys and configuration
values are properly set.
"""

import os
import sys
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


class APIKeyConfig(BaseModel):
    """Validate and store API key configuration."""
    
    openai_api_key: str = Field(..., min_length=20)
    mistral_api_key: str = Field(..., min_length=20)
    elevenlabs_api_key: str = Field(..., min_length=20)
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        """Ensure OpenAI API key meets security requirements."""
        if not v or len(v) < 20:
            raise ValueError("OpenAI API key is missing or invalid")
        if not v.startswith("sk-"):
            raise ValueError("OpenAI API key should start with 'sk-'")
        return v
    
    @validator("mistral_api_key")
    def validate_mistral_key(cls, v):
        """Ensure Mistral API key meets security requirements."""
        if not v or len(v) < 20:
            raise ValueError("Mistral API key is missing or invalid")
        return v
    
    @validator("elevenlabs_api_key")
    def validate_elevenlabs_key(cls, v):
        """Ensure ElevenLabs API key meets security requirements."""
        if not v or len(v) < 20:
            raise ValueError("ElevenLabs API key is missing or invalid")
        return v


def load_and_validate_environment(required_keys: Optional[Set[str]] = None) -> Dict[str, str]:
    """
    Load environment variables and validate required API keys.
    
    Args:
        required_keys: Set of required API key names to validate.
                      If None, validates all keys in APIKeyConfig.
    
    Returns:
        Dict[str, str]: Dictionary of validated environment variables
        
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Determine which keys to validate
    if required_keys is None:
        required_keys = {"openai_api_key", "mistral_api_key", "elevenlabs_api_key"}
    
    # Collect environment variables
    env_vars = {}
    for key in required_keys:
        env_name = key.upper()
        env_vars[key] = os.getenv(env_name, "")
    
    try:
        # Create and validate config with only the required keys
        config_dict = {k: v for k, v in env_vars.items() if k in required_keys}
        APIKeyConfig(**config_dict)
        return env_vars
    except ValueError as e:
        print(f"Environment configuration error: {e}")
        return {}


def validate_environment_or_exit(required_keys: Optional[Set[str]] = None) -> Dict[str, str]:
    """
    Validate environment variables and exit if validation fails.
    
    Args:
        required_keys: Set of required API key names to validate.
                      If None, validates all keys in APIKeyConfig.
    
    Returns:
        Dict[str, str]: Dictionary of validated environment variables
    """
    env_vars = load_and_validate_environment(required_keys)
    if not env_vars:
        print("ERROR: Environment validation failed. Application cannot start.")
        sys.exit(1)
    return env_vars


def check_for_exposed_keys() -> List[str]:
    """
    Check for potentially exposed API keys in the environment.
    
    This function looks for common patterns that might indicate an API key
    has been accidentally committed to version control or exposed in logs.
    
    Returns:
        List[str]: List of warnings about potentially exposed keys
    """
    warnings = []
    
    # Check if .env is in version control
    if os.path.exists(".git") and os.path.exists(".env"):
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()
            if ".env" not in gitignore_content:
                warnings.append(
                    "WARNING: .env file may not be properly excluded from version control. "
                    "Ensure '.env' is in your .gitignore file."
                )
    
    # Check for API keys in example files
    if os.path.exists(".env.example"):
        with open(".env.example", "r") as f:
            example_content = f.read()
            if "sk-" in example_content:
                warnings.append(
                    "WARNING: Possible real API key found in .env.example file. "
                    "Use placeholder values only in example files."
                )
    
    return warnings


if __name__ == "__main__":
    """
    Run environment validation as a standalone script.
    
    This allows quick verification of environment configuration.
    """
    print("Validating environment variables...")
    
    # Check for exposed keys
    warnings = check_for_exposed_keys()
    for warning in warnings:
        print(warning)
    
    # Validate environment variables
    try:
        env_vars = validate_environment_or_exit()
        print("Environment validation successful!")
        print(f"Validated {len(env_vars)} environment variables.")
    except SystemExit:
        # The function will have already printed error messages
        pass