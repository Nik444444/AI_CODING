#!/usr/bin/env python3
"""
Final Comprehensive API Key Management Test
Tests all aspects of the API key management system
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
FRONTEND_DOMAIN = "https://kodix.netlify.app"

class ComprehensiveAPIKeyTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_keys = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            headers = {
                'Origin': FRONTEND_DOMAIN,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(f"{API_BASE}/api-keys", headers=headers)
            
            if response.status_code == 200:
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                cors_methods = response.headers.get('Access-Control-Allow-Methods')
                
                if cors_origin == FRONTEND_DOMAIN and 'POST' in cors_methods:
                    self.log_test("CORS Configuration", True, f"Frontend domain allowed with proper methods")
                    return True
                else:
                    self.log_test("CORS Configuration", False, f"CORS headers incorrect: origin={cors_origin}, methods={cors_methods}")
                    return False
            else:
                self.log_test("CORS Configuration", False, f"Preflight failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {str(e)}")
            return False
    
    def test_create_api_keys(self):
        """Test creating API keys for all providers"""
        providers = [
            {
                "provider": "openai",
                "api_key": "sk-proj-FinalTest123456789abcdef",
                "display_name": "Final Test OpenAI Key"
            },
            {
                "provider": "anthropic", 
                "api_key": "sk-ant-api03-FinalTest123456789abcdef",
                "display_name": "Final Test Anthropic Key"
            },
            {
                "provider": "gemini",
                "api_key": "AIzaSyFinalTest123456789abcdef", 
                "display_name": "Final Test Gemini Key"
            }
        ]
        
        headers = {
            'Origin': FRONTEND_DOMAIN,
            'Content-Type': 'application/json'
        }
        
        success_count = 0
        
        for provider_data in providers:
            try:
                response = self.session.post(f"{API_BASE}/api-keys", json=provider_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.created_keys.append(data['id'])
                    self.log_test(f"Create {provider_data['provider'].title()} Key", True, f"Created with ID: {data['id']}")
                    success_count += 1
                elif response.status_code == 400:
                    error_data = response.json()
                    if "already exists" in error_data.get('detail', ''):
                        self.log_test(f"Create {provider_data['provider'].title()} Key", True, f"Already exists (expected): {error_data['detail']}")
                        success_count += 1
                    else:
                        self.log_test(f"Create {provider_data['provider'].title()} Key", False, f"Validation error: {error_data['detail']}")
                else:
                    self.log_test(f"Create {provider_data['provider'].title()} Key", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Create {provider_data['provider'].title()} Key", False, f"Error: {str(e)}")
        
        return success_count == len(providers)
    
    def test_get_api_keys(self):
        """Test getting all API keys"""
        try:
            headers = {
                'Origin': FRONTEND_DOMAIN,
                'Accept': 'application/json'
            }
            
            response = self.session.get(f"{API_BASE}/api-keys", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 3:
                    providers = [key['provider'] for key in data]
                    expected_providers = ['openai', 'anthropic', 'gemini']
                    
                    found_providers = [p for p in expected_providers if p in providers]
                    if len(found_providers) >= 3:
                        # Check masking
                        all_masked = all('*' in key.get('api_key', '') for key in data)
                        if all_masked:
                            self.log_test("Get All API Keys", True, f"Retrieved {len(data)} keys with proper masking")
                            return True
                        else:
                            self.log_test("Get All API Keys", False, "Keys not properly masked")
                            return False
                    else:
                        self.log_test("Get All API Keys", False, f"Missing providers: {set(expected_providers) - set(found_providers)}")
                        return False
                else:
                    self.log_test("Get All API Keys", False, f"Expected at least 3 keys, got {len(data) if isinstance(data, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Get All API Keys", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get All API Keys", False, f"Error: {str(e)}")
            return False
    
    def test_update_api_key(self):
        """Test updating an API key"""
        try:
            # First get all keys to find one to update
            response = self.session.get(f"{API_BASE}/api-keys")
            if response.status_code != 200:
                self.log_test("Update API Key", False, "Could not get keys for update test")
                return False
            
            keys = response.json()
            if not keys:
                self.log_test("Update API Key", False, "No keys available for update test")
                return False
            
            key_to_update = keys[0]
            key_id = key_to_update['id']
            
            headers = {
                'Origin': FRONTEND_DOMAIN,
                'Content-Type': 'application/json'
            }
            
            update_data = {
                "display_name": "Updated Final Test Key",
                "is_active": False
            }
            
            response = self.session.put(f"{API_BASE}/api-keys/{key_id}", json=update_data, headers=headers)
            
            if response.status_code == 200:
                updated_key = response.json()
                if (updated_key['display_name'] == update_data['display_name'] and
                    updated_key['is_active'] == update_data['is_active']):
                    self.log_test("Update API Key", True, f"Key {key_id} updated successfully")
                    return True
                else:
                    self.log_test("Update API Key", False, "Update not reflected in response")
                    return False
            else:
                self.log_test("Update API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update API Key", False, f"Error: {str(e)}")
            return False
    
    def test_delete_api_key(self):
        """Test deleting an API key"""
        if not self.created_keys:
            self.log_test("Delete API Key", False, "No created keys available for deletion test")
            return False
        
        try:
            key_id = self.created_keys[0]
            
            headers = {
                'Origin': FRONTEND_DOMAIN
            }
            
            response = self.session.delete(f"{API_BASE}/api-keys/{key_id}", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if "deleted successfully" in result.get('message', ''):
                    # Verify deletion
                    verify_response = self.session.get(f"{API_BASE}/api-keys/{key_id}")
                    if verify_response.status_code == 404:
                        self.log_test("Delete API Key", True, f"Key {key_id} deleted and verified")
                        self.created_keys.remove(key_id)
                        return True
                    else:
                        self.log_test("Delete API Key", False, "Key still exists after deletion")
                        return False
                else:
                    self.log_test("Delete API Key", False, f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Delete API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete API Key", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling"""
        try:
            headers = {
                'Origin': FRONTEND_DOMAIN,
                'Content-Type': 'application/json'
            }
            
            # Test invalid provider
            invalid_data = {
                "provider": "invalid_provider",
                "api_key": "test-key",
                "display_name": "Invalid Test"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=invalid_data, headers=headers)
            
            if response.status_code == 400:
                error_data = response.json()
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                
                if "Invalid provider" in error_data.get('detail', '') and cors_origin == FRONTEND_DOMAIN:
                    self.log_test("Error Handling", True, "Invalid provider error handled correctly with CORS")
                    return True
                else:
                    self.log_test("Error Handling", False, f"Error response incorrect: {error_data}, CORS: {cors_origin}")
                    return False
            else:
                self.log_test("Error Handling", False, f"Expected HTTP 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up any remaining test keys"""
        if self.created_keys:
            print(f"\n🧹 Cleaning up {len(self.created_keys)} remaining test keys...")
            for key_id in self.created_keys:
                try:
                    response = self.session.delete(f"{API_BASE}/api-keys/{key_id}")
                    if response.status_code == 200:
                        print(f"   ✅ Deleted key {key_id}")
                    else:
                        print(f"   ⚠️  Failed to delete key {key_id}: {response.status_code}")
                except Exception as e:
                    print(f"   ⚠️  Error deleting key {key_id}: {str(e)}")
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive API Key Management Tests")
        print(f"Frontend Domain: {FRONTEND_DOMAIN}")
        print(f"Backend API: {API_BASE}")
        print("=" * 60)
        
        tests = [
            self.test_cors_configuration,
            self.test_create_api_keys,
            self.test_get_api_keys,
            self.test_update_api_key,
            self.test_delete_api_key,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Cleanup
        self.cleanup()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            print("✅ API Key Management system is working correctly")
            print("✅ CORS is properly configured for the frontend domain")
            print("✅ Database persistence is working")
            print("✅ All CRUD operations are functional")
            print("✅ Error handling is working with proper CORS headers")
            print("\n💡 If users are still experiencing CORS errors, the issue is likely:")
            print("   - Browser caching old CORS policies (try hard refresh)")
            print("   - Frontend code making requests to wrong URL")
            print("   - Network/proxy issues")
            print("   - Frontend not handling async requests properly")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            
        return passed == total

if __name__ == "__main__":
    tester = ComprehensiveAPIKeyTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)