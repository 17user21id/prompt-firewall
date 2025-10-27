#!/usr/bin/env python3
"""
Test script for password-based authentication with encrypted API keys.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.common.auth import AuthManager


def test_password_hashing():
    """Test password hashing and verification."""
    auth_manager = AuthManager()
    
    # Test password hashing
    password = "SecurePassword123!"
    hashed = auth_manager.hash_password(password)
    
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    
    # Test password verification
    is_valid = auth_manager.verify_password(password, hashed)
    assert is_valid, "Password verification should succeed for correct password"
    
    # Test wrong password
    wrong_password = "WrongPassword456!"
    is_invalid = auth_manager.verify_password(wrong_password, hashed)
    assert not is_invalid, "Password verification should fail for wrong password"


def test_bearer_token_format():
    """Test bearer token format with encrypted API keys."""
    # Simulate tenant data
    tenant_id = "550e8400-e29b-41d4-a716-446655440000"
    api_key = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
    
    # Create bearer token
    bearer_token = f"{tenant_id}:{api_key}"
    
    # Parse bearer token
    parsed_tenant_id, parsed_api_key = bearer_token.split(":", 1)
    assert parsed_tenant_id == tenant_id
    assert parsed_api_key == api_key


if __name__ == "__main__":
    test_password_hashing()
    test_bearer_token_format()
    print("All tests passed!")
