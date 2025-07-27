#!/usr/bin/env python3
"""
Authentication Test for API Key Management
Tests if there are any authentication requirements
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_no_auth_required():
    """Test if API endpoints work without authentication"""
    print("🔓 Testing API Access Without Authentication...")
    
    endpoints_to_test = [
        ("GET", "/api-keys", "Get all API keys"),
        ("GET", "/health", "Health check"),
        ("GET", "/", "Root endpoint"),
        ("GET", "/agents", "Get agents"),
        ("GET", "/models", "Get models"),
        ("GET", "/templates", "Get templates")
    ]
    
    session = requests.Session()
    # Explicitly remove any auth headers
    session.headers.clear()
    
    results = []
    
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = session.get(f"{API_BASE}{endpoint}")
            elif method == "POST":
                response = session.post(f"{API_BASE}{endpoint}", json={})
            
            if response.status_code in [200, 201]:
                print(f"✅ {description}: Accessible without auth (HTTP {response.status_code})")
                results.append(True)
            elif response.status_code in [401, 403]:
                print(f"🔒 {description}: Requires authentication (HTTP {response.status_code})")
                results.append(False)
            else:
                print(f"⚠️  {description}: Unexpected status {response.status_code}")
                results.append(True)  # Not an auth issue
                
        except Exception as e:
            print(f"❌ {description}: Error - {str(e)}")
            results.append(False)
    
    accessible_count = sum(results)
    total_count = len(results)
    
    print(f"\nSummary: {accessible_count}/{total_count} endpoints accessible without authentication")
    
    if accessible_count == total_count:
        print("✅ All endpoints are publicly accessible - No authentication required")
        return True
    else:
        print("🔒 Some endpoints require authentication")
        return False

def test_with_common_auth_headers():
    """Test with common authentication headers to see if they're expected"""
    print("\n🔑 Testing with Common Authentication Headers...")
    
    auth_headers_to_test = [
        {"Authorization": "Bearer test-token"},
        {"Authorization": "Basic dGVzdDp0ZXN0"},  # test:test in base64
        {"X-API-Key": "test-api-key"},
        {"X-Auth-Token": "test-auth-token"},
        {"Cookie": "session=test-session"}
    ]
    
    session = requests.Session()
    
    for auth_header in auth_headers_to_test:
        try:
            session.headers.update(auth_header)
            response = session.get(f"{API_BASE}/api-keys")
            
            auth_type = list(auth_header.keys())[0]
            
            if response.status_code == 200:
                print(f"✅ {auth_type}: Request successful (HTTP 200)")
            elif response.status_code in [401, 403]:
                print(f"🔒 {auth_type}: Authentication failed (HTTP {response.status_code})")
            else:
                print(f"⚠️  {auth_type}: Unexpected status {response.status_code}")
            
            # Clear headers for next test
            session.headers.clear()
            
        except Exception as e:
            print(f"❌ {auth_type}: Error - {str(e)}")
    
    return True

def test_cors_with_credentials():
    """Test CORS with credentials to see if authentication cookies are expected"""
    print("\n🍪 Testing CORS with Credentials...")
    
    try:
        headers = {
            'Origin': 'https://kodix.netlify.app',
            'Content-Type': 'application/json'
        }
        
        # Test with credentials
        response = requests.get(f"{API_BASE}/api-keys", headers=headers)
        
        cors_credentials = response.headers.get('Access-Control-Allow-Credentials')
        
        if cors_credentials == 'true':
            print("✅ CORS allows credentials - Authentication via cookies may be supported")
            
            # Test with a sample cookie
            headers['Cookie'] = 'auth_token=test-token; session_id=test-session'
            response_with_cookie = requests.get(f"{API_BASE}/api-keys", headers=headers)
            
            if response_with_cookie.status_code == 200:
                print("✅ Request with cookies successful")
            elif response_with_cookie.status_code in [401, 403]:
                print("🔒 Request with cookies failed - authentication required")
            else:
                print(f"⚠️  Request with cookies returned {response_with_cookie.status_code}")
                
        else:
            print("ℹ️  CORS does not allow credentials - Cookie-based auth not expected")
        
        return True
        
    except Exception as e:
        print(f"❌ CORS credentials test failed: {str(e)}")
        return False

def test_api_key_creation_auth():
    """Test if API key creation requires authentication"""
    print("\n🔐 Testing API Key Creation Authentication...")
    
    test_data = {
        "provider": "anthropic",
        "api_key": "sk-ant-api03-AuthTestKey123456789abcdef",
        "display_name": "Auth Test Key"
    }
    
    session = requests.Session()
    
    # Test without any authentication
    try:
        response = session.post(f"{API_BASE}/api-keys", json=test_data)
        
        if response.status_code == 200:
            created_key = response.json()
            print("✅ API key creation successful without authentication")
            
            # Clean up
            key_id = created_key['id']
            delete_response = session.delete(f"{API_BASE}/api-keys/{key_id}")
            if delete_response.status_code == 200:
                print("✅ Test key cleaned up successfully")
            
            return True
            
        elif response.status_code in [401, 403]:
            print(f"🔒 API key creation requires authentication (HTTP {response.status_code})")
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', 'No details provided')}")
            return False
            
        elif response.status_code == 400:
            error_data = response.json()
            if "already exists" in error_data.get('detail', ''):
                print("✅ API key creation accessible (duplicate key error expected)")
                return True
            else:
                print(f"⚠️  API key creation failed with validation error: {error_data.get('detail')}")
                return True  # Not an auth issue
        else:
            print(f"⚠️  Unexpected response: HTTP {response.status_code}")
            return True  # Not an auth issue
            
    except Exception as e:
        print(f"❌ API key creation test failed: {str(e)}")
        return False

def main():
    print("🧪 Authentication Requirements Test for API Key Management")
    print(f"Backend API: {API_BASE}")
    print("=" * 60)
    
    tests = [
        test_no_auth_required,
        test_with_common_auth_headers,
        test_cors_with_credentials,
        test_api_key_creation_auth
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("📊 AUTHENTICATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL AUTHENTICATION TESTS PASSED!")
        print("🔓 The API appears to be publicly accessible without authentication requirements.")
        print("💡 This means the CORS errors are likely not related to missing authentication.")
    else:
        print(f"\n⚠️  {total - passed} authentication tests failed.")
        print("🔒 Some endpoints may require authentication that is not being provided by the frontend.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)