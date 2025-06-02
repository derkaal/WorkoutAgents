#!/usr/bin/env python3
"""
Environment Security Test Script

This script tests the security of environment variables and API key handling.
It checks for common security issues and provides recommendations for fixing them.
"""

import os
import sys
from dotenv import load_dotenv
from env_validator import (
    load_and_validate_environment,
    validate_environment_or_exit,
    check_for_exposed_keys
)


def test_env_file_exists():
    """Test if .env file exists."""
    if not os.path.exists(".env"):
        print("❌ ERROR: .env file not found")
        print("   Create a .env file with your API keys")
        return False
    print("✅ .env file exists")
    return True


def test_env_example_file_exists():
    """Test if .env.example file exists."""
    if not os.path.exists(".env.example"):
        print("❌ WARNING: .env.example file not found")
        print("   Create a .env.example file with placeholder values")
        return False
    print("✅ .env.example file exists")
    return True


def test_gitignore_excludes_env():
    """Test if .gitignore excludes .env file."""
    if not os.path.exists(".gitignore"):
        print("❌ WARNING: .gitignore file not found")
        print("   Create a .gitignore file to exclude sensitive files")
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
        if ".env" not in content:
            print("❌ ERROR: .env not excluded in .gitignore")
            print("   Add '.env' to your .gitignore file")
            return False
    
    print("✅ .gitignore properly excludes .env file")
    return True


def test_env_example_has_placeholders():
    """Test if .env.example uses placeholders instead of real keys."""
    if not os.path.exists(".env.example"):
        return False
    
    with open(".env.example", "r") as f:
        content = f.read()
        suspicious_patterns = ["sk-", "key-", "api_", "secret"]
        for pattern in suspicious_patterns:
            if pattern in content and len(pattern) > 20:
                print(f"❌ WARNING: Possible real API key in .env.example ({pattern}...)")
                print("   Use placeholder values in example files")
                return False
    
    print("✅ .env.example appears to use proper placeholders")
    return True


def test_env_variables_loaded():
    """Test if environment variables are properly loaded."""
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY", "MISTRAL_API_KEY", "ELEVENLABS_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("   Add these variables to your .env file")
        return False
    
    print("✅ All required environment variables are loaded")
    return True


def test_env_validator():
    """Test the environment validator."""
    try:
        env_vars = load_and_validate_environment()
        if not env_vars:
            print("❌ ERROR: Environment validation failed")
            return False
        print("✅ Environment validation successful")
        return True
    except Exception as e:
        print(f"❌ ERROR: Environment validation failed: {e}")
        return False


def test_for_exposed_keys():
    """Test for potentially exposed API keys."""
    warnings = check_for_exposed_keys()
    if warnings:
        for warning in warnings:
            print(f"❌ {warning}")
        return False
    
    print("✅ No potentially exposed API keys detected")
    return True


def run_all_tests():
    """Run all security tests."""
    print("\n🔒 ENVIRONMENT SECURITY TEST 🔒\n")
    
    tests = [
        test_env_file_exists,
        test_env_example_file_exists,
        test_gitignore_excludes_env,
        test_env_example_has_placeholders,
        test_env_variables_loaded,
        test_env_validator,
        test_for_exposed_keys
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print("")
    
    # Summary
    print("\n📋 TEST SUMMARY 📋")
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {results.count(True)}")
    print(f"Failed: {results.count(False)}")
    
    if False in results:
        print("\n❌ SECURITY ISSUES DETECTED")
        print("   Please fix the issues above to ensure secure API key handling")
        return 1
    else:
        print("\n✅ ALL SECURITY TESTS PASSED")
        print("   Your environment is properly configured for secure API key handling")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())