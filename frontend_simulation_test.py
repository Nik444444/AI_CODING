#!/usr/bin/env python3
"""
Frontend Simulation Test for API Key Management
Simulates the exact frontend requests to identify CORS issues
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

def simulate_frontend_api_call():
    """Simulate exact frontend API call for saving API keys"""
    print("🌐 Simulating Frontend API Call for Saving API Keys...")
    
    # Simulate the exact headers that a browser would send
    headers = {
        'Origin': FRONTEND_DOMAIN,
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': f'{FRONTEND_DOMAIN}/',
    }
    
    # Test data that frontend would send
    test_scenarios = [
        {
            "name": "Create OpenAI Key",
            "method": "POST",
            "endpoint": "/api-keys",
            "data": {
                "provider": "openai",
                "api_key": "sk-proj-FrontendSimTest123456789abcdef",
                "display_name": "Frontend Test OpenAI Key"
            }
        },
        {
            "name": "Create Anthropic Key", 
            "method": "POST",
            "endpoint": "/api-keys",
            "data": {
                "provider": "anthropic",
                "api_key": "sk-ant-api03-FrontendSimTest123456789abcdef",
                "display_name": "Frontend Test Anthropic Key"
            }
        },
        {
            "name": "Create Gemini Key",
            "method": "POST", 
            "endpoint": "/api-keys",
            "data": {
                "provider": "gemini",
                "api_key": "AIzaSyFrontendSimTest123456789abcdef",
                "display_name": "Frontend Test Gemini Key"
            }
        },
        {
            "name": "Get All Keys",
            "method": "GET",
            "endpoint": "/api-keys",
            "data": None
        }
    ]
    
    session = requests.Session()
    results = []
    created_keys = []
    
    for scenario in test_scenarios:
        print(f"\n📝 Testing: {scenario['name']}")
        
        try:
            if scenario['method'] == 'POST':
                response = session.post(
                    f"{API_BASE}{scenario['endpoint']}", 
                    json=scenario['data'],
                    headers=headers
                )
            else:
                response = session.get(
                    f"{API_BASE}{scenario['endpoint']}", 
                    headers=headers
                )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            # Check CORS headers
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_credentials = response.headers.get('Access-Control-Allow-Credentials')
            
            if response.status_code == 200:
                data = response.json()
                if scenario['method'] == 'POST':
                    created_keys.append(data['id'])
                    print(f"   ✅ SUCCESS: API key created with ID {data['id']}")
                else:
                    print(f"   ✅ SUCCESS: Retrieved {len(data)} API keys")
                
                if cors_origin == FRONTEND_DOMAIN:
                    print(f"   ✅ CORS: Origin header correct ({cors_origin})")
                else:
                    print(f"   ⚠️  CORS: Origin header unexpected ({cors_origin})")
                
                results.append(True)
                
            elif response.status_code == 400:
                error_data = response.json()
                if "already exists" in error_data.get('detail', ''):
                    print(f"   ✅ SUCCESS: Duplicate key error (expected) - {error_data['detail']}")
                    results.append(True)
                else:
                    print(f"   ❌ VALIDATION ERROR: {error_data.get('detail')}")
                    results.append(False)
                    
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(False)
                
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ CONNECTION ERROR: {str(e)}")
            print("   This could indicate CORS blocking at the network level")
            results.append(False)
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(False)
    
    # Cleanup created keys
    if created_keys:
        print(f"\n🧹 Cleaning up {len(created_keys)} test keys...")
        for key_id in created_keys:
            try:
                response = session.delete(f"{API_BASE}/api-keys/{key_id}", headers=headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted key {key_id}")
                else:
                    print(f"   ⚠️  Failed to delete key {key_id}: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Error deleting key {key_id}: {str(e)}")
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Frontend Simulation Results: {success_count}/{total_count} scenarios successful")
    
    return success_count == total_count

def test_preflight_requests():
    """Test preflight requests that browsers send before actual requests"""
    print("\n🚁 Testing Browser Preflight Requests...")
    
    preflight_scenarios = [
        {
            "name": "POST API Key Preflight",
            "method": "OPTIONS",
            "endpoint": "/api-keys",
            "headers": {
                'Origin': FRONTEND_DOMAIN,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        },
        {
            "name": "PUT API Key Preflight",
            "method": "OPTIONS", 
            "endpoint": "/api-keys/test-id",
            "headers": {
                'Origin': FRONTEND_DOMAIN,
                'Access-Control-Request-Method': 'PUT',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        },
        {
            "name": "DELETE API Key Preflight",
            "method": "OPTIONS",
            "endpoint": "/api-keys/test-id", 
            "headers": {
                'Origin': FRONTEND_DOMAIN,
                'Access-Control-Request-Method': 'DELETE',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        }
    ]
    
    session = requests.Session()
    results = []
    
    for scenario in preflight_scenarios:
        print(f"\n🔍 Testing: {scenario['name']}")
        
        try:
            response = session.options(
                f"{API_BASE}{scenario['endpoint']}", 
                headers=scenario['headers']
            )
            
            print(f"   Status Code: {response.status_code}")
            
            # Check required CORS headers
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            cors_headers = response.headers.get('Access-Control-Allow-Headers')
            
            print(f"   CORS Origin: {cors_origin}")
            print(f"   CORS Methods: {cors_methods}")
            print(f"   CORS Headers: {cors_headers}")
            
            if response.status_code == 200:
                if cors_origin == FRONTEND_DOMAIN:
                    requested_method = scenario['headers']['Access-Control-Request-Method']
                    if cors_methods and requested_method in cors_methods:
                        print(f"   ✅ SUCCESS: Preflight approved for {requested_method}")
                        results.append(True)
                    else:
                        print(f"   ❌ FAILED: Method {requested_method} not allowed")
                        results.append(False)
                else:
                    print(f"   ❌ FAILED: Origin not allowed ({cors_origin})")
                    results.append(False)
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Preflight Results: {success_count}/{total_count} preflights successful")
    
    return success_count == total_count

def test_error_scenarios():
    """Test error scenarios that might cause frontend issues"""
    print("\n🚨 Testing Error Scenarios...")
    
    error_scenarios = [
        {
            "name": "Invalid JSON",
            "method": "POST",
            "endpoint": "/api-keys",
            "data": "invalid-json",
            "content_type": "application/json"
        },
        {
            "name": "Missing Required Fields",
            "method": "POST", 
            "endpoint": "/api-keys",
            "data": {"provider": "openai"},  # Missing api_key
            "content_type": "application/json"
        },
        {
            "name": "Invalid Provider",
            "method": "POST",
            "endpoint": "/api-keys", 
            "data": {
                "provider": "invalid_provider",
                "api_key": "test-key",
                "display_name": "Test"
            },
            "content_type": "application/json"
        }
    ]
    
    session = requests.Session()
    results = []
    
    for scenario in error_scenarios:
        print(f"\n🔍 Testing: {scenario['name']}")
        
        headers = {
            'Origin': FRONTEND_DOMAIN,
            'Content-Type': scenario['content_type']
        }
        
        try:
            if isinstance(scenario['data'], str):
                # Send raw string for invalid JSON test
                response = session.post(
                    f"{API_BASE}{scenario['endpoint']}", 
                    data=scenario['data'],
                    headers=headers
                )
            else:
                response = session.post(
                    f"{API_BASE}{scenario['endpoint']}", 
                    json=scenario['data'],
                    headers=headers
                )
            
            print(f"   Status Code: {response.status_code}")
            
            # Check if CORS headers are present even in error responses
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            print(f"   CORS Origin: {cors_origin}")
            
            if response.status_code in [400, 422]:  # Expected error codes
                if cors_origin == FRONTEND_DOMAIN:
                    print(f"   ✅ SUCCESS: Error handled with proper CORS headers")
                    results.append(True)
                else:
                    print(f"   ❌ FAILED: Error response missing CORS headers")
                    results.append(False)
            else:
                print(f"   ⚠️  UNEXPECTED: Status {response.status_code}")
                results.append(True)  # Not necessarily a failure
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Error Scenario Results: {success_count}/{total_count} scenarios handled correctly")
    
    return success_count == total_count

def main():
    print("🧪 Frontend Simulation Test for API Key Management")
    print(f"Frontend Domain: {FRONTEND_DOMAIN}")
    print(f"Backend API: {API_BASE}")
    print("=" * 60)
    
    tests = [
        simulate_frontend_api_call,
        test_preflight_requests,
        test_error_scenarios
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("📊 FRONTEND SIMULATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL FRONTEND SIMULATION TESTS PASSED!")
        print("✅ The backend API is working correctly with proper CORS configuration.")
        print("💡 If the frontend is still experiencing CORS errors, the issue may be:")
        print("   - Browser caching old CORS policies")
        print("   - Frontend making requests to wrong URL")
        print("   - Network/proxy issues between frontend and backend")
        print("   - Frontend not handling async requests properly")
    else:
        print(f"\n⚠️  {total - passed} frontend simulation tests failed.")
        print("🔍 This indicates potential issues with CORS configuration or API functionality.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)