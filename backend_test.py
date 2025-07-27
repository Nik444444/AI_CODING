#!/usr/bin/env python3
"""
Comprehensive Backend API Test Suite for Emergent Clone
Tests all backend endpoints and functionality
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

class BackendTester:
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
        
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("Health Check", True, "API is healthy", data)
                    return True
                else:
                    self.log_test("Health Check", False, f"Unhealthy status: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "Emergent Clone API" in data.get('message', ''):
                    self.log_test("Root Endpoint", True, "Root endpoint working", data)
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_get_agents(self):
        """Test getting all available agents"""
        try:
            response = self.session.get(f"{API_BASE}/agents")
            if response.status_code == 200:
                agents = response.json()
                if isinstance(agents, list) and len(agents) == 7:
                    # Check for expected agent types
                    agent_types = [agent.get('type') for agent in agents]
                    expected_types = [
                        'main_assistant', 'project_planner', 'frontend_developer',
                        'backend_developer', 'fullstack_developer', 'deployment_engineer', 'testing_expert'
                    ]
                    
                    missing_types = [t for t in expected_types if t not in agent_types]
                    if not missing_types:
                        self.log_test("Get Agents", True, f"All 7 agents available: {agent_types}", agents)
                        return True
                    else:
                        self.log_test("Get Agents", False, f"Missing agent types: {missing_types}")
                        return False
                else:
                    self.log_test("Get Agents", False, f"Expected 7 agents, got {len(agents) if isinstance(agents, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Get Agents", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Agents", False, f"Error: {str(e)}")
            return False
    
    def test_get_models(self):
        """Test getting available AI models"""
        try:
            response = self.session.get(f"{API_BASE}/models")
            if response.status_code == 200:
                models = response.json()
                if isinstance(models, list) and len(models) >= 3:
                    # Check for expected models
                    model_names = [f"{model.get('provider')}/{model.get('name')}" for model in models]
                    expected_models = ['gemini/gemini-2.0-flash', 'openai/gpt-4o', 'openai/gpt-4o-mini']
                    
                    found_models = [m for m in expected_models if m in model_names]
                    if len(found_models) == 3:
                        self.log_test("Get Models", True, f"All expected models available: {found_models}", models)
                        return True
                    else:
                        self.log_test("Get Models", False, f"Missing models. Found: {found_models}, Expected: {expected_models}")
                        return False
                else:
                    self.log_test("Get Models", False, f"Expected at least 3 models, got {len(models) if isinstance(models, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Get Models", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Models", False, f"Error: {str(e)}")
            return False
    
    def test_get_templates(self):
        """Test getting app templates"""
        try:
            response = self.session.get(f"{API_BASE}/templates")
            if response.status_code == 200:
                templates = response.json()
                if isinstance(templates, list) and len(templates) >= 4:
                    # Check for expected templates
                    template_ids = [template.get('id') for template in templates]
                    expected_templates = ['spotify-clone', 'task-manager', 'ai-pen', 'surprise-me']
                    
                    found_templates = [t for t in expected_templates if t in template_ids]
                    if len(found_templates) >= 4:
                        self.test_data['template_id'] = templates[0]['id']  # Store for later use
                        self.log_test("Get Templates", True, f"Templates loaded: {found_templates}", templates)
                        return True
                    else:
                        self.log_test("Get Templates", False, f"Missing templates. Found: {found_templates}")
                        return False
                else:
                    self.log_test("Get Templates", False, f"Expected at least 4 templates, got {len(templates) if isinstance(templates, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Get Templates", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Templates", False, f"Error: {str(e)}")
            return False
    
    def test_get_specific_template(self):
        """Test getting a specific template"""
        if 'template_id' not in self.test_data:
            self.log_test("Get Specific Template", False, "No template ID available from previous test")
            return False
            
        try:
            template_id = self.test_data['template_id']
            response = self.session.get(f"{API_BASE}/templates/{template_id}")
            if response.status_code == 200:
                template = response.json()
                if template.get('id') == template_id:
                    self.log_test("Get Specific Template", True, f"Template {template_id} retrieved successfully", template)
                    return True
                else:
                    self.log_test("Get Specific Template", False, f"Template ID mismatch: expected {template_id}, got {template.get('id')}")
                    return False
            else:
                self.log_test("Get Specific Template", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Specific Template", False, f"Error: {str(e)}")
            return False
    
    def test_create_project(self):
        """Test creating a new project"""
        try:
            project_data = {
                "name": "Test Music Streaming App",
                "description": "A comprehensive music streaming application with playlists and social features",
                "template_id": self.test_data.get('template_id'),
                "tech_stack": ["React", "FastAPI", "MongoDB", "Audio API"]
            }
            
            response = self.session.post(f"{API_BASE}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                if project.get('name') == project_data['name']:
                    self.test_data['project_id'] = project['id']  # Store for later use
                    self.log_test("Create Project", True, f"Project created with ID: {project['id']}", project)
                    return True
                else:
                    self.log_test("Create Project", False, f"Project name mismatch: {project}")
                    return False
            else:
                self.log_test("Create Project", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Project", False, f"Error: {str(e)}")
            return False
    
    def test_get_projects(self):
        """Test getting all projects"""
        try:
            response = self.session.get(f"{API_BASE}/projects")
            if response.status_code == 200:
                projects = response.json()
                if isinstance(projects, list):
                    # Should have at least the project we created
                    if len(projects) >= 1:
                        self.log_test("Get Projects", True, f"Retrieved {len(projects)} projects", projects)
                        return True
                    else:
                        self.log_test("Get Projects", False, "No projects found")
                        return False
                else:
                    self.log_test("Get Projects", False, f"Expected list, got: {type(projects)}")
                    return False
            else:
                self.log_test("Get Projects", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Projects", False, f"Error: {str(e)}")
            return False
    
    def test_get_specific_project(self):
        """Test getting a specific project"""
        if 'project_id' not in self.test_data:
            self.log_test("Get Specific Project", False, "No project ID available from previous test")
            return False
            
        try:
            project_id = self.test_data['project_id']
            response = self.session.get(f"{API_BASE}/projects/{project_id}")
            if response.status_code == 200:
                project = response.json()
                if project.get('id') == project_id:
                    self.log_test("Get Specific Project", True, f"Project {project_id} retrieved successfully", project)
                    return True
                else:
                    self.log_test("Get Specific Project", False, f"Project ID mismatch: expected {project_id}, got {project.get('id')}")
                    return False
            else:
                self.log_test("Get Specific Project", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Specific Project", False, f"Error: {str(e)}")
            return False
    
    def test_update_project(self):
        """Test updating a project"""
        if 'project_id' not in self.test_data:
            self.log_test("Update Project", False, "No project ID available from previous test")
            return False
            
        try:
            project_id = self.test_data['project_id']
            update_data = {
                "status": "in_progress",
                "progress": 25,
                "repository_url": "https://github.com/user/test-music-app"
            }
            
            response = self.session.put(f"{API_BASE}/projects/{project_id}", json=update_data)
            if response.status_code == 200:
                project = response.json()
                if (project.get('status') == 'in_progress' and 
                    project.get('progress') == 25 and
                    project.get('repository_url') == update_data['repository_url']):
                    self.log_test("Update Project", True, f"Project {project_id} updated successfully", project)
                    return True
                else:
                    self.log_test("Update Project", False, f"Update not reflected properly: {project}")
                    return False
            else:
                self.log_test("Update Project", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update Project", False, f"Error: {str(e)}")
            return False
    
    def test_send_chat_message(self):
        """Test sending a chat message"""
        try:
            message_data = {
                "message": "I want to build a music streaming app like Spotify with React and FastAPI",
                "agent_type": "project_planner",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                if (chat_response.get('session_id') and 
                    chat_response.get('message') and
                    chat_response['message'].get('content')):
                    self.test_data['session_id'] = chat_response['session_id']
                    self.log_test("Send Chat Message", True, f"Chat message sent, session: {chat_response['session_id']}", chat_response)
                    return True
                else:
                    self.log_test("Send Chat Message", False, f"Invalid response structure: {chat_response}")
                    return False
            else:
                self.log_test("Send Chat Message", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Send Chat Message", False, f"Error: {str(e)}")
            return False
    
    def test_get_session_messages(self):
        """Test getting messages for a chat session"""
        if 'session_id' not in self.test_data:
            self.log_test("Get Session Messages", False, "No session ID available from previous test")
            return False
            
        try:
            session_id = self.test_data['session_id']
            response = self.session.get(f"{API_BASE}/chat/session/{session_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                if isinstance(messages, list) and len(messages) >= 2:  # Should have user + assistant messages
                    # Check message structure
                    user_msg = next((m for m in messages if m.get('role') == 'user'), None)
                    assistant_msg = next((m for m in messages if m.get('role') == 'assistant'), None)
                    
                    if user_msg and assistant_msg:
                        self.log_test("Get Session Messages", True, f"Retrieved {len(messages)} messages for session", messages)
                        return True
                    else:
                        self.log_test("Get Session Messages", False, f"Missing user or assistant messages: {messages}")
                        return False
                else:
                    self.log_test("Get Session Messages", False, f"Expected at least 2 messages, got {len(messages) if isinstance(messages, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Get Session Messages", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Session Messages", False, f"Error: {str(e)}")
            return False
    
    def test_get_chat_sessions(self):
        """Test getting all chat sessions"""
        try:
            response = self.session.get(f"{API_BASE}/chat/sessions")
            if response.status_code == 200:
                sessions = response.json()
                if isinstance(sessions, list):
                    # Should have at least the session we created
                    if len(sessions) >= 1:
                        session_ids = [s.get('id') for s in sessions]
                        if self.test_data.get('session_id') in session_ids:
                            self.log_test("Get Chat Sessions", True, f"Retrieved {len(sessions)} sessions", sessions)
                            return True
                        else:
                            self.log_test("Get Chat Sessions", False, f"Our session not found in list: {session_ids}")
                            return False
                    else:
                        self.log_test("Get Chat Sessions", False, "No sessions found")
                        return False
                else:
                    self.log_test("Get Chat Sessions", False, f"Expected list, got: {type(sessions)}")
                    return False
            else:
                self.log_test("Get Chat Sessions", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Chat Sessions", False, f"Error: {str(e)}")
            return False
    
    def test_agent_suggestion(self):
        """Test agent suggestion functionality by sending different types of messages"""
        test_cases = [
            {
                "message": "I need help with React components and CSS styling",
                "expected_agent": "frontend_developer"
            },
            {
                "message": "Help me design the database schema and API endpoints",
                "expected_agent": "backend_developer"
            },
            {
                "message": "I want to deploy my app to production with Docker",
                "expected_agent": "deployment_engineer"
            }
        ]
        
        success_count = 0
        for i, test_case in enumerate(test_cases):
            try:
                message_data = {
                    "message": test_case["message"],
                    "model_provider": "gemini",
                    "model_name": "gemini-2.0-flash"
                }
                
                response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
                if response.status_code == 200:
                    chat_response = response.json()
                    agent_type = chat_response.get('message', {}).get('agent_type')
                    
                    if agent_type == test_case["expected_agent"]:
                        self.log_test(f"Agent Suggestion {i+1}", True, f"Correctly suggested {agent_type} for message about {test_case['expected_agent'].replace('_', ' ')}")
                        success_count += 1
                    else:
                        self.log_test(f"Agent Suggestion {i+1}", False, f"Expected {test_case['expected_agent']}, got {agent_type}")
                else:
                    self.log_test(f"Agent Suggestion {i+1}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Agent Suggestion {i+1}", False, f"Error: {str(e)}")
        
        # Overall agent suggestion test result
        if success_count >= 2:  # At least 2 out of 3 should work
            self.log_test("Agent Suggestion System", True, f"{success_count}/3 agent suggestions worked correctly")
            return True
        else:
            self.log_test("Agent Suggestion System", False, f"Only {success_count}/3 agent suggestions worked")
            return False
    
    def test_create_api_key_gemini(self):
        """Test creating a Gemini API key"""
        try:
            api_key_data = {
                "provider": "gemini",
                "api_key": "AIzaSyDemoGeminiKey123456789abcdef",
                "display_name": "My Gemini API Key"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 200:
                api_key = response.json()
                if (api_key.get('provider') == 'gemini' and 
                    api_key.get('display_name') == api_key_data['display_name'] and
                    api_key.get('api_key').endswith('cdef') and  # Check masking
                    '*' in api_key.get('api_key')):  # Check masking
                    self.test_data['gemini_key_id'] = api_key['id']
                    self.log_test("Create Gemini API Key", True, f"Gemini API key created with ID: {api_key['id']}, masked key: {api_key['api_key']}", api_key)
                    return True
                else:
                    self.log_test("Create Gemini API Key", False, f"Invalid API key response: {api_key}")
                    return False
            else:
                self.log_test("Create Gemini API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Gemini API Key", False, f"Error: {str(e)}")
            return False
    
    def test_create_api_key_openai(self):
        """Test creating an OpenAI API key"""
        try:
            api_key_data = {
                "provider": "openai",
                "api_key": "sk-proj-DemoOpenAIKey123456789abcdef",
                "display_name": "My OpenAI API Key"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 200:
                api_key = response.json()
                if (api_key.get('provider') == 'openai' and 
                    api_key.get('display_name') == api_key_data['display_name'] and
                    api_key.get('api_key').endswith('cdef') and  # Check masking
                    '*' in api_key.get('api_key')):  # Check masking
                    self.test_data['openai_key_id'] = api_key['id']
                    self.log_test("Create OpenAI API Key", True, f"OpenAI API key created with ID: {api_key['id']}, masked key: {api_key['api_key']}", api_key)
                    return True
                else:
                    self.log_test("Create OpenAI API Key", False, f"Invalid API key response: {api_key}")
                    return False
            else:
                self.log_test("Create OpenAI API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create OpenAI API Key", False, f"Error: {str(e)}")
            return False
    
    def test_create_api_key_anthropic(self):
        """Test creating an Anthropic API key"""
        try:
            api_key_data = {
                "provider": "anthropic",
                "api_key": "sk-ant-api03-DemoAnthropicKey123456789abcdef",
                "display_name": "My Anthropic API Key"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 200:
                api_key = response.json()
                if (api_key.get('provider') == 'anthropic' and 
                    api_key.get('display_name') == api_key_data['display_name'] and
                    api_key.get('api_key').endswith('cdef') and  # Check masking
                    '*' in api_key.get('api_key')):  # Check masking
                    self.test_data['anthropic_key_id'] = api_key['id']
                    self.log_test("Create Anthropic API Key", True, f"Anthropic API key created with ID: {api_key['id']}, masked key: {api_key['api_key']}", api_key)
                    return True
                else:
                    self.log_test("Create Anthropic API Key", False, f"Invalid API key response: {api_key}")
                    return False
            else:
                self.log_test("Create Anthropic API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Anthropic API Key", False, f"Error: {str(e)}")
            return False
    
    def test_create_api_key_invalid_provider(self):
        """Test creating API key with invalid provider"""
        try:
            api_key_data = {
                "provider": "invalid_provider",
                "api_key": "test-key-123",
                "display_name": "Invalid Provider Key"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 400:
                error_data = response.json()
                if "Invalid provider" in error_data.get('detail', ''):
                    self.log_test("Create API Key - Invalid Provider", True, f"Correctly rejected invalid provider: {error_data['detail']}")
                    return True
                else:
                    self.log_test("Create API Key - Invalid Provider", False, f"Wrong error message: {error_data}")
                    return False
            else:
                self.log_test("Create API Key - Invalid Provider", False, f"Expected HTTP 400, got {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create API Key - Invalid Provider", False, f"Error: {str(e)}")
            return False
    
    def test_create_duplicate_api_key(self):
        """Test creating duplicate API key for same provider"""
        try:
            # Try to create another Gemini key
            api_key_data = {
                "provider": "gemini",
                "api_key": "AIzaSyAnotherGeminiKey987654321",
                "display_name": "Another Gemini Key"
            }
            
            response = self.session.post(f"{API_BASE}/api-keys", json=api_key_data)
            if response.status_code == 400:
                error_data = response.json()
                if "already exists" in error_data.get('detail', ''):
                    self.log_test("Create Duplicate API Key", True, f"Correctly rejected duplicate provider: {error_data['detail']}")
                    return True
                else:
                    self.log_test("Create Duplicate API Key", False, f"Wrong error message: {error_data}")
                    return False
            else:
                self.log_test("Create Duplicate API Key", False, f"Expected HTTP 400, got {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Duplicate API Key", False, f"Error: {str(e)}")
            return False
    
    def test_get_all_api_keys(self):
        """Test getting all API keys"""
        try:
            response = self.session.get(f"{API_BASE}/api-keys")
            if response.status_code == 200:
                api_keys = response.json()
                if isinstance(api_keys, list) and len(api_keys) >= 3:
                    # Check that we have our created keys
                    providers = [key.get('provider') for key in api_keys]
                    expected_providers = ['gemini', 'openai', 'anthropic']
                    
                    found_providers = [p for p in expected_providers if p in providers]
                    if len(found_providers) >= 3:
                        # Check masking
                        all_masked = all('*' in key.get('api_key', '') for key in api_keys)
                        if all_masked:
                            self.log_test("Get All API Keys", True, f"Retrieved {len(api_keys)} API keys with proper masking: {providers}", api_keys)
                            return True
                        else:
                            self.log_test("Get All API Keys", False, "API keys not properly masked")
                            return False
                    else:
                        self.log_test("Get All API Keys", False, f"Missing providers. Found: {found_providers}, Expected: {expected_providers}")
                        return False
                else:
                    self.log_test("Get All API Keys", False, f"Expected at least 3 API keys, got {len(api_keys) if isinstance(api_keys, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Get All API Keys", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get All API Keys", False, f"Error: {str(e)}")
            return False
    
    def test_get_specific_api_key(self):
        """Test getting a specific API key"""
        if 'gemini_key_id' not in self.test_data:
            self.log_test("Get Specific API Key", False, "No Gemini key ID available from previous test")
            return False
            
        try:
            key_id = self.test_data['gemini_key_id']
            response = self.session.get(f"{API_BASE}/api-keys/{key_id}")
            if response.status_code == 200:
                api_key = response.json()
                if (api_key.get('id') == key_id and 
                    api_key.get('provider') == 'gemini' and
                    '*' in api_key.get('api_key', '')):  # Check masking
                    self.log_test("Get Specific API Key", True, f"Retrieved API key {key_id} with proper masking", api_key)
                    return True
                else:
                    self.log_test("Get Specific API Key", False, f"Invalid API key data: {api_key}")
                    return False
            else:
                self.log_test("Get Specific API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Specific API Key", False, f"Error: {str(e)}")
            return False
    
    def test_update_api_key(self):
        """Test updating an API key"""
        if 'openai_key_id' not in self.test_data:
            self.log_test("Update API Key", False, "No OpenAI key ID available from previous test")
            return False
            
        try:
            key_id = self.test_data['openai_key_id']
            update_data = {
                "display_name": "Updated OpenAI Key",
                "is_active": False
            }
            
            response = self.session.put(f"{API_BASE}/api-keys/{key_id}", json=update_data)
            if response.status_code == 200:
                api_key = response.json()
                if (api_key.get('display_name') == 'Updated OpenAI Key' and 
                    api_key.get('is_active') == False):
                    self.log_test("Update API Key", True, f"API key {key_id} updated successfully", api_key)
                    return True
                else:
                    self.log_test("Update API Key", False, f"Update not reflected properly: {api_key}")
                    return False
            else:
                self.log_test("Update API Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update API Key", False, f"Error: {str(e)}")
            return False
    
    def test_delete_api_key(self):
        """Test deleting an API key"""
        if 'anthropic_key_id' not in self.test_data:
            self.log_test("Delete API Key", False, "No Anthropic key ID available from previous test")
            return False
            
        try:
            key_id = self.test_data['anthropic_key_id']
            response = self.session.delete(f"{API_BASE}/api-keys/{key_id}")
            if response.status_code == 200:
                result = response.json()
                if "deleted successfully" in result.get('message', ''):
                    # Verify key is actually deleted
                    verify_response = self.session.get(f"{API_BASE}/api-keys/{key_id}")
                    if verify_response.status_code == 404:
                        self.log_test("Delete API Key", True, f"API key {key_id} deleted successfully and verified", result)
                        return True
                    else:
                        self.log_test("Delete API Key", False, f"Key still exists after deletion: {verify_response.status_code}")
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
    
    def test_get_nonexistent_api_key(self):
        """Test getting a non-existent API key"""
        try:
            fake_key_id = "non-existent-key-id"
            response = self.session.get(f"{API_BASE}/api-keys/{fake_key_id}")
            if response.status_code == 404:
                error_data = response.json()
                if "not found" in error_data.get('detail', '').lower():
                    self.log_test("Get Non-existent API Key", True, f"Correctly returned 404 for non-existent key: {error_data['detail']}")
                    return True
                else:
                    self.log_test("Get Non-existent API Key", False, f"Wrong error message: {error_data}")
                    return False
            else:
                self.log_test("Get Non-existent API Key", False, f"Expected HTTP 404, got {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Non-existent API Key", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_web_analysis(self):
        """Test web analysis functionality - проанализируй сайт https://example.com"""
        try:
            message_data = {
                "message": "проанализируй сайт https://example.com",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if response contains web analysis indicators
                if (any(indicator in message_content.lower() for indicator in 
                       ['анализ веб-сайтов', 'example.com', 'сайт:', 'заголовок:', 'контент']) and
                    'https://example.com' in message_content):
                    self.log_test("Emergent Tools - Web Analysis", True, 
                                f"Web analysis working - analyzed example.com successfully", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - Web Analysis", False, 
                                f"Web analysis response doesn't contain expected content: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - Web Analysis", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - Web Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_web_search(self):
        """Test web search functionality - найди информацию о Python FastAPI"""
        try:
            message_data = {
                "message": "найди информацию о Python FastAPI",
                "agent_type": "main_assistant", 
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if response contains search results
                if (any(indicator in message_content.lower() for indicator in 
                       ['результаты поиска', 'fastapi', 'python', 'поиск']) and
                    ('http' in message_content or 'www' in message_content)):
                    self.log_test("Emergent Tools - Web Search", True, 
                                f"Web search working - found FastAPI information", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - Web Search", False, 
                                f"Web search response doesn't contain expected results: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - Web Search", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - Web Search", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_file_creation_react(self):
        """Test React file creation - создай файл React компонента"""
        try:
            message_data = {
                "message": "создай файл React компонента",
                "agent_type": "frontend_developer",
                "model_provider": "gemini", 
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if file was created and response contains React code
                if (any(indicator in message_content.lower() for indicator in 
                       ['файл создан', 'react', 'jsx', 'component']) and
                    ('import React' in message_content or 'export default' in message_content)):
                    self.log_test("Emergent Tools - React File Creation", True, 
                                f"React file creation working - created component file", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - React File Creation", False, 
                                f"React file creation response doesn't contain expected content: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - React File Creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - React File Creation", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_file_creation_python(self):
        """Test Python file creation - создай Python файл"""
        try:
            message_data = {
                "message": "создай Python файл",
                "agent_type": "backend_developer",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if Python file was created
                if (any(indicator in message_content.lower() for indicator in 
                       ['файл создан', 'python', '.py']) and
                    ('def main' in message_content or 'print(' in message_content or '__name__' in message_content)):
                    self.log_test("Emergent Tools - Python File Creation", True, 
                                f"Python file creation working - created script file", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - Python File Creation", False, 
                                f"Python file creation response doesn't contain expected content: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - Python File Creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - Python File Creation", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_command_execution(self):
        """Test command execution - выполни команду pwd"""
        try:
            message_data = {
                "message": "выполни команду pwd",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if command was executed
                if (any(indicator in message_content.lower() for indicator in 
                       ['выполнена команда', 'pwd', '$ pwd']) and
                    ('/app' in message_content or '/home' in message_content or '/usr' in message_content)):
                    self.log_test("Emergent Tools - Command Execution", True, 
                                f"Command execution working - pwd command executed", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - Command Execution", False, 
                                f"Command execution response doesn't contain expected output: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - Command Execution", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - Command Execution", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_integration_playbook(self):
        """Test integration playbook - интеграция Stripe"""
        try:
            message_data = {
                "message": "интеграция Stripe",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if integration playbook was generated
                if (any(indicator in message_content.lower() for indicator in 
                       ['playbook', 'stripe', 'интеграция', 'шаги']) and
                    ('pip install stripe' in message_content or 'stripe.api_key' in message_content)):
                    self.log_test("Emergent Tools - Integration Playbook", True, 
                                f"Integration playbook working - generated Stripe integration guide", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - Integration Playbook", False, 
                                f"Integration playbook response doesn't contain expected content: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - Integration Playbook", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - Integration Playbook", False, f"Error: {str(e)}")
            return False
    
    def test_emergent_tools_image_generation(self):
        """Test image generation - создай изображение"""
        try:
            message_data = {
                "message": "создай изображение",
                "agent_type": "main_assistant",
                "model_provider": "gemini",
                "model_name": "gemini-2.0-flash"
            }
            
            response = self.session.post(f"{API_BASE}/chat/send", json=message_data)
            if response.status_code == 200:
                chat_response = response.json()
                message_content = chat_response.get('message', {}).get('content', '')
                
                # Check if image generation response was provided
                if (any(indicator in message_content.lower() for indicator in 
                       ['изображение создано', 'картинку', 'изображение']) and
                    ('base64' in message_content.lower() or 'отображено' in message_content.lower())):
                    self.log_test("Emergent Tools - Image Generation", True, 
                                f"Image generation working - generated placeholder image", chat_response)
                    return True
                else:
                    self.log_test("Emergent Tools - Image Generation", False, 
                                f"Image generation response doesn't contain expected content: {message_content[:200]}")
                    return False
            else:
                self.log_test("Emergent Tools - Image Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Emergent Tools - Image Generation", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Emergent Clone Backend API Tests")
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        # Core system tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Agent and model tests
        self.test_get_agents()
        self.test_get_models()
        
        # Template tests
        self.test_get_templates()
        self.test_get_specific_template()
        
        # Project management tests
        self.test_create_project()
        self.test_get_projects()
        self.test_get_specific_project()
        self.test_update_project()
        
        # Chat system tests
        self.test_send_chat_message()
        self.test_get_session_messages()
        self.test_get_chat_sessions()
        self.test_agent_suggestion()
        
        # API Key management tests
        print("\n🔑 Testing API Key Management...")
        self.test_create_api_key_gemini()
        self.test_create_api_key_openai()
        self.test_create_api_key_anthropic()
        self.test_create_api_key_invalid_provider()
        self.test_create_duplicate_api_key()
        self.test_get_all_api_keys()
        self.test_get_specific_api_key()
        self.test_update_api_key()
        self.test_delete_api_key()
        self.test_get_nonexistent_api_key()
        
        # Emergent Tools Integration Tests
        print("\n🛠️ Testing Emergent Tools Integration...")
        self.test_emergent_tools_web_analysis()
        self.test_emergent_tools_web_search()
        self.test_emergent_tools_file_creation_react()
        self.test_emergent_tools_file_creation_python()
        self.test_emergent_tools_command_execution()
        self.test_emergent_tools_integration_playbook()
        self.test_emergent_tools_image_generation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)