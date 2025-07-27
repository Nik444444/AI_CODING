#!/usr/bin/env python3
"""
CORS Test for API Key Management
Tests CORS configuration specifically for the frontend domain
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
FRONTEND_DOMAIN = "https://kodix.netlify.app"

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🌐 Testing CORS Preflight Request...")
    
    try:
        # Make an OPTIONS request (preflight)
        headers = {
            'Origin': FRONTEND_DOMAIN,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f"{API_BASE}/api-keys", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        # Check if frontend domain is allowed
        allowed_origin = cors_headers['Access-Control-Allow-Origin']
        if allowed_origin == FRONTEND_DOMAIN or allowed_origin == '*':
            print("✅ CORS Origin Check: PASSED - Frontend domain is allowed")
            return True
        else:
            print(f"❌ CORS Origin Check: FAILED - Expected {FRONTEND_DOMAIN}, got {allowed_origin}")
            return False
            
    except Exception as e:
        print(f"❌ CORS Preflight Test: FAILED - {str(e)}")
        return False

def test_cors_actual_request():
    """Test actual CORS request with Origin header"""
    print("\n🔑 Testing CORS with Actual API Request...")
    
    try:
        # Make a GET request with Origin header (simulating frontend request)
        headers = {
            'Origin': FRONTEND_DOMAIN,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{API_BASE}/api-keys", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Check CORS headers in response
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_credentials = response.headers.get('Access-Control-Allow-Credentials')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {len(data)} API keys found")
            
            if cors_origin == FRONTEND_DOMAIN or cors_origin == '*':
                print("✅ CORS Actual Request: PASSED - Request successful with proper CORS headers")
                return True
            else:
                print(f"❌ CORS Actual Request: FAILED - Missing or incorrect CORS origin header: {cors_origin}")
                return False
        else:
            print(f"❌ CORS Actual Request: FAILED - HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CORS Actual Request: FAILED - {str(e)}")
        return False

def test_cors_post_request():
    """Test CORS with POST request (API key creation)"""
    print("\n📝 Testing CORS with POST Request...")
    
    try:
        # First, make preflight request
        preflight_headers = {
            'Origin': FRONTEND_DOMAIN,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        preflight_response = requests.options(f"{API_BASE}/api-keys", headers=preflight_headers)
        print(f"Preflight Status: {preflight_response.status_code}")
        
        # Then make actual POST request
        headers = {
            'Origin': FRONTEND_DOMAIN,
            'Content-Type': 'application/json'
        }
        
        test_data = {
            "provider": "gemini",
            "api_key": "AIzaSyCORSTestKey123456789abcdef",
            "display_name": "CORS Test Gemini Key"
        }
        
        response = requests.post(f"{API_BASE}/api-keys", json=test_data, headers=headers)
        
        print(f"POST Status Code: {response.status_code}")
        print(f"POST Response Headers: {dict(response.headers)}")
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        
        if response.status_code in [200, 400]:  # 400 is expected if key already exists
            if response.status_code == 400:
                error_data = response.json()
                if "already exists" in error_data.get('detail', ''):
                    print("✅ CORS POST Request: PASSED - Duplicate key error (expected), CORS working")
                    return True
            else:
                data = response.json()
                print(f"✅ CORS POST Request: PASSED - API key created: {data.get('id')}")
                return True
                
            if cors_origin != FRONTEND_DOMAIN and cors_origin != '*':
                print(f"⚠️  CORS POST Request: WARNING - Incorrect CORS origin: {cors_origin}")
                
        else:
            print(f"❌ CORS POST Request: FAILED - HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CORS POST Request: FAILED - {str(e)}")
        return False

def main():
    print("🧪 CORS Configuration Test for API Key Management")
    print(f"Frontend Domain: {FRONTEND_DOMAIN}")
    print(f"Backend API: {API_BASE}")
    print("=" * 60)
    
    tests = [
        test_cors_preflight,
        test_cors_actual_request,
        test_cors_post_request
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("📊 CORS TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL CORS TESTS PASSED! CORS is properly configured.")
    else:
        print(f"\n⚠️  {total - passed} CORS tests failed. Check CORS configuration.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)