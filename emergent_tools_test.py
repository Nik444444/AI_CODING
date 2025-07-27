#!/usr/bin/env python3
"""
Focused Emergent Tools Testing
Tests the specific Emergent tools functionality as requested in the review
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class EmergentToolsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: any = None):
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
        if not success and response_data:
            print(f"   Response preview: {str(response_data)[:200]}...")
    
    def test_web_analysis_httpbin(self):
        """Test web analysis with httpbin.org/json as requested"""
        try:
            message_data = {
                "message": "проанализируй сайт https://httpbin.org/json",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if response contains web analysis of httpbin.org/json
                if (any(indicator in message_content.lower() for indicator in 
                       ['httpbin.org', 'json', 'анализ', 'сайт']) and
                    'httpbin.org/json' in message_content):
                    self.log_test("Web Analysis - httpbin.org/json", True, 
                                f"Successfully analyzed httpbin.org/json", chat_response)
                    return True
                else:
                    self.log_test("Web Analysis - httpbin.org/json", False, 
                                f"Response doesn't contain expected httpbin analysis", chat_response)
                    return False
            else:
                self.log_test("Web Analysis - httpbin.org/json", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Web Analysis - httpbin.org/json", False, f"Error: {str(e)}")
            return False
    
    def test_web_search_python_tutorials(self):
        """Test web search with 'Python tutorials' as requested"""
        try:
            message_data = {
                "message": "поиск Python tutorials",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if response contains search results for Python tutorials
                if (any(indicator in message_content.lower() for indicator in 
                       ['python', 'tutorial', 'поиск', 'результат']) and
                    ('http' in message_content or 'www' in message_content or 'tutorial' in message_content.lower())):
                    self.log_test("Web Search - Python tutorials", True, 
                                f"Successfully searched for Python tutorials", chat_response)
                    return True
                else:
                    self.log_test("Web Search - Python tutorials", False, 
                                f"Response doesn't contain expected search results", chat_response)
                    return False
            else:
                self.log_test("Web Search - Python tutorials", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Web Search - Python tutorials", False, f"Error: {str(e)}")
            return False
    
    def test_react_component_creation(self):
        """Test React component creation as requested"""
        try:
            message_data = {
                "message": "создай файл React компонента ButtonExample",
                "agent_type": "frontend_developer",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if React component file was created
                if (any(indicator in message_content.lower() for indicator in 
                       ['buttonexample', 'react', 'компонент', 'файл создан']) and
                    ('jsx' in message_content.lower() or 'import react' in message_content.lower())):
                    self.log_test("React Component Creation - ButtonExample", True, 
                                f"Successfully created ButtonExample React component", chat_response)
                    return True
                else:
                    self.log_test("React Component Creation - ButtonExample", False, 
                                f"Response doesn't contain expected React component creation", chat_response)
                    return False
            else:
                self.log_test("React Component Creation - ButtonExample", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("React Component Creation - ButtonExample", False, f"Error: {str(e)}")
            return False
    
    def test_python_api_script_creation(self):
        """Test Python API script creation as requested"""
        try:
            message_data = {
                "message": "создать файл Python скрипта для API",
                "agent_type": "backend_developer",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if Python API script was created
                if (any(indicator in message_content.lower() for indicator in 
                       ['python', 'api', 'скрипт', 'файл создан']) and
                    ('def' in message_content or 'import' in message_content or '.py' in message_content)):
                    self.log_test("Python API Script Creation", True, 
                                f"Successfully created Python API script", chat_response)
                    return True
                else:
                    self.log_test("Python API Script Creation", False, 
                                f"Response doesn't contain expected Python script creation", chat_response)
                    return False
            else:
                self.log_test("Python API Script Creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Python API Script Creation", False, f"Error: {str(e)}")
            return False
    
    def test_command_execution_date(self):
        """Test command execution with 'date' command as requested"""
        try:
            message_data = {
                "message": "выполни команду date",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if date command was executed
                if (any(indicator in message_content.lower() for indicator in 
                       ['date', 'команда', 'выполнена']) and
                    ('2025' in message_content or 'jan' in message_content.lower() or 'янв' in message_content.lower())):
                    self.log_test("Command Execution - date", True, 
                                f"Successfully executed date command", chat_response)
                    return True
                else:
                    self.log_test("Command Execution - date", False, 
                                f"Response doesn't contain expected date command output", chat_response)
                    return False
            else:
                self.log_test("Command Execution - date", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Command Execution - date", False, f"Error: {str(e)}")
            return False
    
    def test_openai_integration_playbook(self):
        """Test integration playbook with OpenAI API as requested"""
        try:
            message_data = {
                "message": "интеграция с OpenAI API",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if OpenAI integration playbook was generated
                if (any(indicator in message_content.lower() for indicator in 
                       ['openai', 'playbook', 'интеграция', 'api']) and
                    ('pip install openai' in message_content or 'openai.api_key' in message_content or 'client = OpenAI' in message_content)):
                    self.log_test("Integration Playbook - OpenAI API", True, 
                                f"Successfully generated OpenAI integration playbook", chat_response)
                    return True
                else:
                    self.log_test("Integration Playbook - OpenAI API", False, 
                                f"Response doesn't contain expected OpenAI playbook", chat_response)
                    return False
            else:
                self.log_test("Integration Playbook - OpenAI API", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Integration Playbook - OpenAI API", False, f"Error: {str(e)}")
            return False
    
    def test_fallback_system(self):
        """Test fallback system with casual message as requested"""
        try:
            message_data = {
                "message": "Как дела?",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if fallback system provides a reasonable response
                if (len(message_content) > 50 and
                    any(indicator in message_content.lower() for indicator in 
                       ['помочь', 'assistant', 'проект', 'разработк'])):
                    self.log_test("Fallback System - Casual Message", True, 
                                f"Fallback system working - provided helpful response", chat_response)
                    return True
                else:
                    self.log_test("Fallback System - Casual Message", False, 
                                f"Fallback response too short or unhelpful", chat_response)
                    return False
            else:
                self.log_test("Fallback System - Casual Message", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Fallback System - Casual Message", False, f"Error: {str(e)}")
            return False
    
    def run_emergent_tools_tests(self):
        """Run all Emergent tools tests as specified in the review request"""
        print("🛠️ Starting Emergent Tools Testing (Review Request)")
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        # Test each tool as specified in the review request
        self.test_web_analysis_httpbin()
        self.test_web_search_python_tutorials()
        self.test_react_component_creation()
        self.test_python_api_script_creation()
        self.test_command_execution_date()
        self.test_openai_integration_playbook()
        self.test_fallback_system()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 EMERGENT TOOLS TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL EMERGENT TOOLS WORKING! System is ready.")
        else:
            print(f"\n⚠️  {total - passed} Emergent tools failed. Routing logic needs fixing.")
            
        return passed, total

if __name__ == "__main__":
    tester = EmergentToolsTester()
    passed, total = tester.run_emergent_tools_tests()
    exit(0 if passed == total else 1)