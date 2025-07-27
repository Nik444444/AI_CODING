#!/usr/bin/env python3
"""
Debug test for chat system to understand empty content issue
"""

import requests
import json
import time
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def debug_chat_response():
    """Debug chat response structure"""
    session = requests.Session()
    
    print("🔍 DEBUGGING CHAT SYSTEM")
    print(f"Testing against: {API_BASE}")
    print("=" * 60)
    
    # Test 1: Simple message with main_assistant
    print("\n1️⃣ Testing simple message with main_assistant...")
    message_data = {
        "message": "Привет! Как дела?",
        "agent_type": "main_assistant",
        "model_provider": "gemini",
        "model_name": "gemini-2.0-flash"
    }
    
    try:
        response = session.post(f"{API_BASE}/chat/send", json=message_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chat_response = response.json()
            print("Response structure:")
            print(json.dumps(chat_response, indent=2, ensure_ascii=False))
            
            # Check message content
            message = chat_response.get('message', {})
            content = message.get('content', '')
            print(f"\nMessage content length: {len(content)}")
            print(f"Message content preview: {content[:200]}...")
            
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Project creation message
    print("\n2️⃣ Testing project creation message...")
    message_data = {
        "message": "Создай простое React приложение для управления задачами",
        "agent_type": "project_planner",
        "model_provider": "gemini",
        "model_name": "gemini-2.0-flash"
    }
    
    try:
        response = session.post(f"{API_BASE}/chat/send", json=message_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chat_response = response.json()
            
            # Check message content
            message = chat_response.get('message', {})
            content = message.get('content', '')
            agent_type = message.get('agent_type', '')
            
            print(f"Agent type: {agent_type}")
            print(f"Message content length: {len(content)}")
            print(f"Message content preview: {content[:300]}...")
            
            # Check if there are created files mentioned
            if 'created_files' in str(chat_response):
                print("✅ Response mentions created files")
            else:
                print("❌ No created files mentioned")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Check if agent_tools.py exists and is accessible
    print("\n3️⃣ Checking agent tools availability...")
    try:
        import sys
        sys.path.append('/app/backend')
        from agent_tools import AgentToolsManager
        print("✅ AgentToolsManager imported successfully")
        
        # Test if we can create an instance
        tools = AgentToolsManager()
        print("✅ AgentToolsManager instance created")
        
    except Exception as e:
        print(f"❌ AgentToolsManager error: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Check real_agent_executor
    print("\n4️⃣ Checking real agent executor...")
    try:
        import sys
        sys.path.append('/app/backend')
        from real_agent_executor import RealAgentExecutor
        print("✅ RealAgentExecutor imported successfully")
        
        executor = RealAgentExecutor()
        print("✅ RealAgentExecutor instance created")
        
    except Exception as e:
        print(f"❌ RealAgentExecutor error: {str(e)}")

if __name__ == "__main__":
    debug_chat_response()