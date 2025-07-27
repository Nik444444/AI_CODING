#!/usr/bin/env python3
"""
Focused test for Gemini API key integration and chat system
Tests the specific requirements from the review request
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

class GeminiChatTester:
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
        
    def test_gemini_api_key_exists_and_active(self):
        """Test that Gemini API key is correctly saved and active"""
        try:
            response = self.session.get(f"{API_BASE}/api-keys")
            if response.status_code == 200:
                api_keys = response.json()
                gemini_keys = [key for key in api_keys if key.get('provider') == 'gemini']
                
                if gemini_keys:
                    gemini_key = gemini_keys[0]
                    if gemini_key.get('is_active'):
                        self.test_data['gemini_key_id'] = gemini_key['id']
                        self.log_test("Gemini API Key Active", True, 
                                    f"Found active Gemini key: {gemini_key['display_name']}, masked: {gemini_key['api_key']}", 
                                    gemini_key)
                        return True
                    else:
                        self.log_test("Gemini API Key Active", False, "Gemini key exists but is not active")
                        return False
                else:
                    # Create a Gemini key for testing
                    return self.create_test_gemini_key()
            else:
                self.log_test("Gemini API Key Active", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Gemini API Key Active", False, f"Error: {str(e)}")
            return False
    
    def create_test_gemini_key(self):
        """Create a test Gemini API key"""
        try:
            api_key_data = {
                "provider": "gemini",
                "api_key": "AIzaSyTestGeminiKey2025_abcdef123456",
                "display_name": "Test Gemini API Key 2025"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 200:
                api_key = response.json()
                self.test_data['gemini_key_id'] = api_key['id']
                self.log_test("Create Test Gemini Key", True, 
                            f"Created test Gemini key: {api_key['id']}", api_key)
                return True
            else:
                self.log_test("Create Test Gemini Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test Gemini Key", False, f"Error: {str(e)}")
            return False
    
    def test_chat_send_with_gemini_react_app(self):
        """Test sending a message to create a simple React app using Gemini"""
        try:
            message_data = {
                "message": "Создай простое React приложение с компонентами для отображения списка задач",
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
                    if len(content) > 50 and agent_type:
                        self.test_data['react_session_id'] = chat_response['session_id']
                        self.log_test("Chat Send - React App", True, 
                                    f"Successfully sent React app request. Session: {chat_response['session_id']}, Agent: {agent_type}, Response length: {len(content)}", 
                                    chat_response)
                        return True
                    else:
                        self.log_test("Chat Send - React App", False, 
                                    f"Response too short or missing agent: content={len(content)} chars, agent={agent_type}")
                        return False
                else:
                    self.log_test("Chat Send - React App", False, f"Invalid response structure: {chat_response}")
                    return False
            else:
                self.log_test("Chat Send - React App", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Chat Send - React App", False, f"Error: {str(e)}")
            return False
    
    def test_chat_send_with_gemini_website_analysis(self):
        """Test sending a message to analyze a website using Gemini"""
        try:
            message_data = {
                "message": "Проанализируй веб-сайт и предложи улучшения для пользовательского интерфейса",
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
                    if len(content) > 50 and agent_type:
                        self.test_data['analysis_session_id'] = chat_response['session_id']
                        self.log_test("Chat Send - Website Analysis", True, 
                                    f"Successfully sent website analysis request. Session: {chat_response['session_id']}, Agent: {agent_type}, Response length: {len(content)}", 
                                    chat_response)
                        return True
                    else:
                        self.log_test("Chat Send - Website Analysis", False, 
                                    f"Response too short or missing agent: content={len(content)} chars, agent={agent_type}")
                        return False
                else:
                    self.log_test("Chat Send - Website Analysis", False, f"Invalid response structure: {chat_response}")
                    return False
            else:
                self.log_test("Chat Send - Website Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Chat Send - Website Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_models_endpoint(self):
        """Test that models endpoint returns Gemini models"""
        try:
            response = self.session.get(f"{API_BASE}/models")
            if response.status_code == 200:
                models = response.json()
                gemini_models = [m for m in models if m.get('provider') == 'gemini']
                
                if gemini_models:
                    gemini_model = gemini_models[0]
                    if gemini_model.get('name') == 'gemini-2.0-flash':
                        self.log_test("Models Endpoint - Gemini", True, 
                                    f"Gemini model available: {gemini_model['display_name']}", models)
                        return True
                    else:
                        self.log_test("Models Endpoint - Gemini", False, 
                                    f"Wrong Gemini model: {gemini_model.get('name')}")
                        return False
                else:
                    self.log_test("Models Endpoint - Gemini", False, "No Gemini models found")
                    return False
            else:
                self.log_test("Models Endpoint - Gemini", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Models Endpoint - Gemini", False, f"Error: {str(e)}")
            return False
    
    def test_agents_endpoint(self):
        """Test that agents endpoint returns available agents"""
        try:
            response = self.session.get(f"{API_BASE}/agents")
            if response.status_code == 200:
                agents = response.json()
                if isinstance(agents, list) and len(agents) >= 7:
                    # Check for key agent types
                    agent_types = [agent.get('type') for agent in agents]
                    required_agents = ['frontend_developer', 'backend_developer', 'design_agent']
                    
                    found_agents = [a for a in required_agents if a in agent_types]
                    if len(found_agents) >= 3:
                        self.log_test("Agents Endpoint", True, 
                                    f"Found {len(agents)} agents including required ones: {found_agents}", agents)
                        return True
                    else:
                        self.log_test("Agents Endpoint", False, 
                                    f"Missing required agents. Found: {found_agents}, Required: {required_agents}")
                        return False
                else:
                    self.log_test("Agents Endpoint", False, f"Expected at least 7 agents, got {len(agents) if isinstance(agents, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Agents Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Agents Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_session_messages_retrieval(self):
        """Test retrieving messages from chat sessions"""
        if 'react_session_id' not in self.test_data:
            self.log_test("Session Messages Retrieval", False, "No React session ID available")
            return False
            
        try:
            session_id = self.test_data['react_session_id']
            response = self.session.get(f"{API_BASE}/chat/session/{session_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                if isinstance(messages, list) and len(messages) >= 2:
                    # Check for user and assistant messages
                    user_msgs = [m for m in messages if m.get('role') == 'user']
                    assistant_msgs = [m for m in messages if m.get('role') == 'assistant']
                    
                    if user_msgs and assistant_msgs:
                        self.log_test("Session Messages Retrieval", True, 
                                    f"Retrieved {len(messages)} messages: {len(user_msgs)} user, {len(assistant_msgs)} assistant", 
                                    messages)
                        return True
                    else:
                        self.log_test("Session Messages Retrieval", False, 
                                    f"Missing message types: user={len(user_msgs)}, assistant={len(assistant_msgs)}")
                        return False
                else:
                    self.log_test("Session Messages Retrieval", False, 
                                f"Expected at least 2 messages, got {len(messages) if isinstance(messages, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Session Messages Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Session Messages Retrieval", False, f"Error: {str(e)}")
            return False
    
    def test_database_api_key_usage(self):
        """Test that the system correctly uses API key from database"""
        try:
            # First verify the key exists in database
            response = self.session.get(f"{API_BASE}/api-keys")
            if response.status_code != 200:
                self.log_test("Database API Key Usage", False, "Cannot retrieve API keys")
                return False
                
            api_keys = response.json()
            gemini_keys = [key for key in api_keys if key.get('provider') == 'gemini' and key.get('is_active')]
            
            if not gemini_keys:
                self.log_test("Database API Key Usage", False, "No active Gemini keys in database")
                return False
            
            # Now test a chat message that should use the database key
            message_data = {
                "message": "Тест использования API ключа из базы данных для Gemini",
                "agent_type": "main_assistant",
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
                    
                    self.log_test("Database API Key Usage", True, 
                                f"Successfully used database API key for Gemini chat. Session: {chat_response['session_id']}", 
                                chat_response)
                    return True
                else:
                    self.log_test("Database API Key Usage", False, "Invalid chat response structure")
                    return False
            else:
                self.log_test("Database API Key Usage", False, f"Chat failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database API Key Usage", False, f"Error: {str(e)}")
            return False
    
    def run_gemini_tests(self):
        """Run all Gemini-focused tests"""
        print("🤖 Starting Gemini API Chat System Tests")
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        # Test 1: Check that API key Gemini is correctly saved and active
        print("\n1️⃣ Testing Gemini API Key Storage and Status...")
        self.test_gemini_api_key_exists_and_active()
        
        # Test 2: Test available models endpoint
        print("\n2️⃣ Testing Available Models...")
        self.test_models_endpoint()
        
        # Test 3: Test available agents endpoint  
        print("\n3️⃣ Testing Available Agents...")
        self.test_agents_endpoint()
        
        # Test 4: Test sending message to create React app using Gemini
        print("\n4️⃣ Testing Chat - Create React App...")
        self.test_chat_send_with_gemini_react_app()
        
        # Test 5: Test sending message to analyze website using Gemini
        print("\n5️⃣ Testing Chat - Website Analysis...")
        self.test_chat_send_with_gemini_website_analysis()
        
        # Test 6: Test session message retrieval
        print("\n6️⃣ Testing Session Message Retrieval...")
        self.test_session_messages_retrieval()
        
        # Test 7: Test that system uses database API key
        print("\n7️⃣ Testing Database API Key Usage...")
        self.test_database_api_key_usage()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 GEMINI CHAT SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL GEMINI TESTS PASSED! Backend AI chat system with Gemini is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            
        # Detailed failure analysis
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"- {test['test']}: {test['details']}")
            
        return passed == total

if __name__ == "__main__":
    tester = GeminiChatTester()
    success = tester.run_gemini_tests()
    exit(0 if success else 1)