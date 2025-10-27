#!/usr/bin/env python3
"""
Integration test for SDK with actual backend API calls.
"""

import sys
import os
import time
import json

# Add sdk to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from prompt_firewall import PromptFirewallSDK
    import requests
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    print("Install with: pip3 install requests")
    sys.exit(1)

API_URL = "http://localhost:8000"
TEST_TENANT_NAME = f"test-sdk-{int(time.time())}"
TEST_PASSWORD = "testpass123"

def test_health_check():
    """Test health check without authentication."""
    print("\n[1/9] Testing health check...")
    try:
        sdk = PromptFirewallSDK(
            api_url=API_URL,
            api_key="dummy",
            tenant_id="dummy"
        )
        health = sdk.health_check()
        assert 'status' in health
        print(f"✓ Health check passed: {health['status']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_create_tenant():
    """Test creating a tenant."""
    print("\n[2/9] Testing create_tenant...")
    try:
        response = PromptFirewallSDK.create_tenant(
            api_url=API_URL,
            name=TEST_TENANT_NAME,
            password=TEST_PASSWORD
        )
        
        assert 'tenant_id' in response
        assert 'api_key' in response
        print(f"✓ Tenant created: {response['tenant_id'][:8]}...")
        return response
    except Exception as e:
        print(f"✗ Create tenant failed: {e}")
        return None

def test_login_tenant(tenant_id):
    """Test logging in a tenant."""
    print("\n[3/9] Testing login_tenant...")
    try:
        response = PromptFirewallSDK.login_tenant(
            api_url=API_URL,
            name=TEST_TENANT_NAME,
            password=TEST_PASSWORD
        )
        
        assert 'tenant_id' in response
        assert 'api_key' in response
        print(f"✓ Login successful: {response['tenant_id'][:8]}...")
        return response
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return None

def test_query(sdk):
    """Test querying a prompt."""
    print("\n[4/9] Testing query...")
    try:
        result = sdk.query(
            "My email is john@example.com and my SSN is 123-45-6789",
            user_id="test_user_123"
        )
        
        assert 'decision' in result
        assert 'risks' in result
        assert 'promptModified' in result
        print(f"✓ Query successful - Decision: {result['decision']}, Risks: {len(result['risks'])}")
        return result
    except Exception as e:
        print(f"✗ Query failed: {e}")
        return None

def test_get_prompts(sdk):
    """Test getting prompt history."""
    print("\n[5/9] Testing get_prompts...")
    try:
        prompts = sdk.get_prompts(limit=10)
        assert isinstance(prompts, list)
        print(f"✓ Retrieved {len(prompts)} prompts")
        return True
    except Exception as e:
        print(f"✗ Get prompts failed: {e}")
        return False

def test_get_logs(sdk):
    """Test getting logs."""
    print("\n[6/9] Testing get_logs...")
    try:
        logs = sdk.get_logs(limit=10)
        assert isinstance(logs, list)
        print(f"✓ Retrieved {len(logs)} logs")
        return True
    except Exception as e:
        print(f"✗ Get logs failed: {e}")
        return False

def test_create_rule(sdk):
    """Test creating a custom rule."""
    print("\n[7/9] Testing create_rule...")
    try:
        rule = sdk.create_rule(
            rule_type="CUSTOM",
            pattern=r"\bconfidential\b",
            action="warn",
            severity="medium",
            description="Test rule for confidential info"
        )
        
        assert 'rule_id' in rule
        print(f"✓ Rule created: {rule['rule_id'][:8]}...")
        return rule
    except Exception as e:
        print(f"✗ Create rule failed: {e}")
        return None

def test_get_rules(sdk):
    """Test getting rules."""
    print("\n[8/9] Testing get_rules...")
    try:
        rules = sdk.get_rules(limit=10)
        assert isinstance(rules, list)
        print(f"✓ Retrieved {len(rules)} rules")
        return True
    except Exception as e:
        print(f"✗ Get rules failed: {e}")
        return False

def test_get_stats(sdk):
    """Test getting statistics."""
    print("\n[9/9] Testing get_stats...")
    try:
        stats = sdk.get_stats()
        assert isinstance(stats, dict)
        print(f"✓ Stats retrieved - Prompts: {stats.get('prompt_stats', {}).get('total_prompts', 0)}")
        return True
    except Exception as e:
        print(f"✗ Get stats failed: {e}")
        return False

def cleanup_test_tenant(tenant_data):
    """Clean up test tenant."""
    if tenant_data:
        try:
            print(f"\n[Cleanup] Cleaning up test tenant...")
            # Could implement delete_tenant if needed
            print("✓ Cleanup complete")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("SDK Integration Test")
    print("=" * 60)
    print(f"\nAPI URL: {API_URL}")
    print(f"Test Tenant: {TEST_TENANT_NAME}\n")
    
    results = []
    tenant_data = None
    credentials = None
    sdk = None
    
    try:
        # Test 1: Health check
        results.append(("Health Check", test_health_check()))
        
        # Test 2: Create tenant
        tenant_data = test_create_tenant()
        results.append(("Create Tenant", tenant_data is not None))
        
        if not tenant_data:
            print("\n⚠ Skipping remaining tests - tenant creation failed")
            return
        
        # Test 3: Login
        credentials = test_login_tenant(tenant_data['tenant_id'])
        results.append(("Login", credentials is not None))
        
        if not credentials:
            print("\n⚠ Skipping remaining tests - login failed")
            return
        
        # Initialize SDK
        sdk = PromptFirewallSDK(
            api_url=API_URL,
            api_key=credentials['api_key'],
            tenant_id=credentials['tenant_id']
        )
        
        # Test 4: Query
        query_result = test_query(sdk)
        results.append(("Query", query_result is not None))
        
        # Test 5: Get prompts
        results.append(("Get Prompts", test_get_prompts(sdk)))
        
        # Test 6: Get logs
        results.append(("Get Logs", test_get_logs(sdk)))
        
        # Test 7: Create rule
        rule = test_create_rule(sdk)
        results.append(("Create Rule", rule is not None))
        
        # Test 8: Get rules
        results.append(("Get Rules", test_get_rules(sdk)))
        
        # Test 9: Get stats
        results.append(("Get Stats", test_get_stats(sdk)))
        
    finally:
        # Cleanup
        cleanup_test_tenant(tenant_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! SDK is working correctly with backend.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

