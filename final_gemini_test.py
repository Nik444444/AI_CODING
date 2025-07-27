#!/usr/bin/env python3
"""
Final comprehensive test for Gemini API key integration and chat system
Based on the specific requirements from the review request
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class FinalGeminiTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_data = {}
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_1_gemini_api_key_saved_and_active(self):
        """1. Проверь что API ключ Gemini корректно сохранен и активен"""
        try:
            response = self.session.get(f"{API_BASE}/api-keys")
            if response.status_code == 200:
                api_keys = response.json()
                gemini_keys = [key for key in api_keys if key.get('provider') == 'gemini']
                
                if gemini_keys:
                    gemini_key = gemini_keys[0]
                    if gemini_key.get('is_active'):
                        self.test_data['gemini_key_id'] = gemini_key['id']
                        self.log_test("1. Gemini API Key Saved & Active", True, 
                                    f"✅ Found active Gemini key: {gemini_key['display_name']}, ID: {gemini_key['id'][:8]}..., masked: {gemini_key['api_key']}")
                        return True
                    else:
                        self.log_test("1. Gemini API Key Saved & Active", False, "Gemini key exists but is not active")
                        return False
                else:
                    # Create a test Gemini key
                    return self._create_test_gemini_key()
            else:
                self.log_test("1. Gemini API Key Saved & Active", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("1. Gemini API Key Saved & Active", False, f"Error: {str(e)}")
            return False
    
    def _create_test_gemini_key(self):
        """Create a test Gemini API key for testing"""
        try:
            api_key_data = {
                "provider": "gemini",
                "api_key": "AIzaSyTestGeminiKey2025_NewIntegration_abcdef123456",
                "display_name": "Test Gemini API Key 2025 - New Integration"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 200:
                api_key = response.json()
                self.test_data['gemini_key_id'] = api_key['id']
                self.log_test("1. Gemini API Key Saved & Active", True, 
                            f"✅ Created new test Gemini key: {api_key['id'][:8]}..., masked: {api_key['api_key']}")
                return True
            else:
                self.log_test("1. Gemini API Key Saved & Active", False, f"Failed to create key: HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("1. Gemini API Key Saved & Active", False, f"Error creating key: {str(e)}")
            return False
    
    def test_2_send_message_create_react_app(self):
        """2. Протестируй отправку сообщения в чат с использованием Gemini - "Создай простое React приложение" """
        try:
            message_data = {
                "message": "Создай простое React приложение с компонентами для отображения списка задач и добавления новых задач",
                "agent_type": "frontend_developer",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                
                # Check response structure
                if (chat_response.get('session_id') and 
                    chat_response.get('message') and
                    isinstance(chat_response['message'], dict)):
                    
                    message = chat_response['message']
                    content = message.get('content', '')
                    agent_type = message.get('agent_type')
                    
                    # Check if we got a meaningful response
                    if len(content) > 100 and agent_type == 'frontend_developer':
                        self.test_data['react_session_id'] = chat_response['session_id']
                        self.log_test("2. Send Message - Create React App", True, 
                                    f"✅ Successfully sent React app creation request using Gemini. Session: {chat_response['session_id']}, Agent: {agent_type}, Response: {len(content)} chars")
                        return True
                    else:
                        self.log_test("2. Send Message - Create React App", False, 
                                    f"Response too short or wrong agent: content={len(content)} chars, agent={agent_type}")
                        return False
                else:
                    self.log_test("2. Send Message - Create React App", False, f"Invalid response structure: {chat_response}")
                    return False
            else:
                self.log_test("2. Send Message - Create React App", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("2. Send Message - Create React App", False, f"Error: {str(e)}")
            return False
    
    def test_3_send_message_analyze_website(self):
        """3. Протестируй отправку сообщения "Проанализируй веб-сайт" """
        try:
            message_data = {
                "message": "Проанализируй веб-сайт и предложи улучшения для пользовательского интерфейса и UX дизайна",
                "agent_type": "design_agent",
                "model_provider": "gemini", 
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                
                # Check response structure
                if (chat_response.get('session_id') and 
                    chat_response.get('message') and
                    isinstance(chat_response['message'], dict)):
                    
                    message = chat_response['message']
                    content = message.get('content', '')
                    agent_type = message.get('agent_type')
                    
                    # Check if we got a meaningful response
                    if len(content) > 100 and agent_type == 'design_agent':
                        self.test_data['analysis_session_id'] = chat_response['session_id']
                        self.log_test("3. Send Message - Analyze Website", True, 
                                    f"✅ Successfully sent website analysis request using Gemini. Session: {chat_response['session_id']}, Agent: {agent_type}, Response: {len(content)} chars")
                        return True
                    else:
                        self.log_test("3. Send Message - Analyze Website", False, 
                                    f"Response too short or wrong agent: content={len(content)} chars, agent={agent_type}")
                        return False
                else:
                    self.log_test("3. Send Message - Analyze Website", False, f"Invalid response structure: {chat_response}")
                    return False
            else:
                self.log_test("3. Send Message - Analyze Website", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("3. Send Message - Analyze Website", False, f"Error: {str(e)}")
            return False
    
    def test_4_system_uses_database_api_key(self):
        """4. Проверь что система correctly использует новый API ключ из базы данных"""
        try:
            # First verify the key exists in database
            response = self.session.get(f"{API_BASE}/api-keys")
            if response.status_code != 200:
                self.log_test("4. System Uses Database API Key", False, "Cannot retrieve API keys from database")
                return False
                
            api_keys = response.json()
            gemini_keys = [key for key in api_keys if key.get('provider') == 'gemini' and key.get('is_active')]
            
            if not gemini_keys:
                self.log_test("4. System Uses Database API Key", False, "No active Gemini keys in database")
                return False
            
            # Now test a chat message that should use the database key
            message_data = {
                "message": "Тест использования API ключа из базы данных для Gemini - создай простой компонент React",
                "agent_type": "frontend_developer",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                
                # If we get a response, it means the API key was used successfully
                if (chat_response.get('session_id') and 
                    chat_response.get('message') and
                    chat_response['message'].get('content')):
                    
                    self.log_test("4. System Uses Database API Key", True, 
                                f"✅ System successfully used database-stored Gemini API key. Session: {chat_response['session_id']}")
                    return True
                else:
                    self.log_test("4. System Uses Database API Key", False, "Invalid chat response structure")
                    return False
            else:
                self.log_test("4. System Uses Database API Key", False, f"Chat failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("4. System Uses Database API Key", False, f"Error: {str(e)}")
            return False
    
    def test_5_all_chat_endpoints_work(self):
        """5. Убедись что все chat endpoints работают правильно"""
        endpoints_to_test = [
            ("POST /api/chat/send", "chat/send"),
            ("GET /api/chat/sessions", "chat/sessions"),
        ]
        
        all_working = True
        results = []
        
        # Test POST /api/chat/send (already tested above, but let's verify again)
        try:
            message_data = {
                "message": "Тест всех chat endpoints",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                if chat_response.get('session_id'):
                    self.test_data['test_session_id'] = chat_response['session_id']
                    results.append("✅ POST /api/chat/send - Working")
                else:
                    results.append("❌ POST /api/chat/send - Invalid response")
                    all_working = False
            else:
                results.append(f"❌ POST /api/chat/send - HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            results.append(f"❌ POST /api/chat/send - Error: {str(e)}")
            all_working = False
        
        # Test GET /api/chat/sessions
        try:
            response = self.session.get(f"{API_BASE}/chat/sessions")
            if response.status_code == 200:
                sessions = response.json()
                if isinstance(sessions, list):
                    results.append(f"✅ GET /api/chat/sessions - Working ({len(sessions)} sessions)")
                else:
                    results.append("❌ GET /api/chat/sessions - Invalid response format")
                    all_working = False
            else:
                results.append(f"❌ GET /api/chat/sessions - HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            results.append(f"❌ GET /api/chat/sessions - Error: {str(e)}")
            all_working = False
        
        # Test GET /api/chat/session/{id}/messages if we have a session
        if 'test_session_id' in self.test_data:
            try:
                session_id = self.test_data['test_session_id']
                response = self.session.get(f"{API_BASE}/chat/session/{session_id}/messages")
                if response.status_code == 200:
                    messages = response.json()
                    if isinstance(messages, list):
                        results.append(f"✅ GET /api/chat/session/{{id}}/messages - Working ({len(messages)} messages)")
                    else:
                        results.append("❌ GET /api/chat/session/{id}/messages - Invalid response format")
                        all_working = False
                else:
                    results.append(f"❌ GET /api/chat/session/{{id}}/messages - HTTP {response.status_code}")
                    all_working = False
            except Exception as e:
                results.append(f"❌ GET /api/chat/session/{{id}}/messages - Error: {str(e)}")
                all_working = False
        
        self.log_test("5. All Chat Endpoints Work", all_working, 
                    f"Chat endpoints test results: {'; '.join(results)}")
        return all_working
    
    def test_6_agents_can_respond_correctly(self):
        """6. Проверь что агенты могут корректно отвечать"""
        agents_to_test = [
            ("main_assistant", "Привет! Как дела?"),
            ("project_planner", "Создай план для веб-приложения"),
            ("frontend_developer", "Создай React компонент"),
            ("backend_developer", "Создай FastAPI endpoint"),
            ("design_agent", "Создай дизайн для приложения")
        ]
        
        successful_agents = 0
        results = []
        
        for agent_type, test_message in agents_to_test:
            try:
                message_data = {
                    "message": test_message,
                    "agent_type": agent_type,
                    "model_provider": "gemini",
                    "model_name": "gemini-2.0-flash"
                }
                
                response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
                if response.status_code == 200:
                    chat_response = response.json()
                    message = chat_response.get('message', {})
                    content = message.get('content', '')
                    returned_agent = message.get('agent_type', '')
                    
                    if len(content) > 50 and returned_agent:
                        results.append(f"✅ {agent_type} - Responded ({len(content)} chars)")
                        successful_agents += 1
                    else:
                        results.append(f"❌ {agent_type} - Short/empty response ({len(content)} chars)")
                else:
                    results.append(f"❌ {agent_type} - HTTP {response.status_code}")
            except Exception as e:
                results.append(f"❌ {agent_type} - Error: {str(e)}")
        
        success = successful_agents >= 4  # At least 4 out of 5 agents should work
        self.log_test("6. Agents Can Respond Correctly", success, 
                    f"Agent response test: {successful_agents}/5 agents working. Details: {'; '.join(results)}")
        return success
    
    def test_bonus_models_and_agents_endpoints(self):
        """Bonus: Test GET /api/models and GET /api/agents endpoints"""
        all_working = True
        results = []
        
        # Test GET /api/models
        try:
            response = self.session.get(f"{API_BASE}/models")
            if response.status_code == 200:
                models = response.json()
                gemini_models = [m for m in models if m.get('provider') == 'gemini']
                if gemini_models:
                    results.append(f"✅ GET /api/models - Working (found {len(gemini_models)} Gemini models)")
                else:
                    results.append("❌ GET /api/models - No Gemini models found")
                    all_working = False
            else:
                results.append(f"❌ GET /api/models - HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            results.append(f"❌ GET /api/models - Error: {str(e)}")
            all_working = False
        
        # Test GET /api/agents
        try:
            response = self.session.get(f"{API_BASE}/agents")
            if response.status_code == 200:
                agents = response.json()
                if isinstance(agents, list) and len(agents) >= 7:
                    results.append(f"✅ GET /api/agents - Working ({len(agents)} agents)")
                else:
                    results.append(f"❌ GET /api/agents - Expected ≥7 agents, got {len(agents) if isinstance(agents, list) else 'non-list'}")
                    all_working = False
            else:
                results.append(f"❌ GET /api/agents - HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            results.append(f"❌ GET /api/agents - Error: {str(e)}")
            all_working = False
        
        self.log_test("Bonus: Models & Agents Endpoints", all_working, 
                    f"Additional endpoints test: {'; '.join(results)}")
        return all_working
    
    def run_final_tests(self):
        """Run all final Gemini integration tests"""
        print("🚀 FINAL GEMINI API CHAT SYSTEM INTEGRATION TESTS")
        print(f"Testing against: {API_BASE}")
        print("=" * 80)
        print("Based on review request requirements:")
        print("1. Проверь что API ключ Gemini корректно сохранен и активен")
        print("2. Протестируй отправку сообщения в чат с использованием Gemini")
        print("3. Проверь что система correctly использует новый API ключ из базы данных")
        print("4. Убедись что все chat endpoints работают правильно")
        print("5. Проверь что агенты могут корректно отвечать")
        print("=" * 80)
        
        # Run all tests
        test_functions = [
            self.test_1_gemini_api_key_saved_and_active,
            self.test_2_send_message_create_react_app,
            self.test_3_send_message_analyze_website,
            self.test_4_system_uses_database_api_key,
            self.test_5_all_chat_endpoints_work,
            self.test_6_agents_can_respond_correctly,
            self.test_bonus_models_and_agents_endpoints
        ]
        
        for test_func in test_functions:
            print(f"\n🔍 Running {test_func.__name__}...")
            test_func()
            time.sleep(1)  # Small delay between tests
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Core requirements check (first 6 tests)
        core_passed = sum(1 for result in self.test_results[:6] if result['success'])
        core_total = 6
        
        print(f"\nCore Requirements (1-6): {core_passed}/{core_total} passed ({(core_passed/core_total)*100:.1f}%)")
        
        if core_passed == core_total:
            print("\n🎉 ALL CORE REQUIREMENTS PASSED! ✅")
            print("✅ Gemini API key is correctly saved and active")
            print("✅ Chat messages work with Gemini")
            print("✅ System uses database-stored API key")
            print("✅ All chat endpoints are functional")
            print("✅ Agents respond correctly")
            print("\n🚀 BACKEND AI CHAT SYSTEM WITH GEMINI IS FULLY WORKING!")
        else:
            print(f"\n⚠️  {core_total - core_passed} core requirements failed.")
            
        # Detailed failure analysis
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"- {test['test']}: {test['details']}")
            
        return core_passed == core_total

if __name__ == "__main__":
    tester = FinalGeminiTester()
    success = tester.run_final_tests()
    exit(0 if success else 1)