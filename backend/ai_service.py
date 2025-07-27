import os
import asyncio
from typing import List, Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from models import AgentType, ChatMessage, MessageRole
from agents import AgentManager
from real_agent_executor import RealAgentExecutor
from agent_tools import AgentToolsManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import APIKeyDB, AsyncSessionLocal


class AIService:
    """Service for handling AI interactions with real agent execution and tools"""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.real_executor = RealAgentExecutor()
        self.tools_manager = AgentToolsManager()
        self.active_chats: Dict[str, LlmChat] = {}
    
    async def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider from database or environment"""
        try:
            # First, try to get from database
            async with AsyncSessionLocal() as db:
                stmt = select(APIKeyDB).where(
                    APIKeyDB.provider == provider,
                    APIKeyDB.is_active == 1
                )
                result = await db.execute(stmt)
                api_key_db = result.scalar_one_or_none()
                
                if api_key_db:
                    return api_key_db.api_key
            
            # Fallback to environment variables
            key_mapping = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY", 
                "anthropic": "ANTHROPIC_API_KEY"
            }
            
            env_key = key_mapping.get(provider)
            if env_key:
                return os.environ.get(env_key)
                
        except Exception as e:
            print(f"Error getting API key for {provider}: {e}")
            # Fallback to environment variables on database error
            key_mapping = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY", 
                "anthropic": "ANTHROPIC_API_KEY"
            }
            
            env_key = key_mapping.get(provider)
            if env_key:
                return os.environ.get(env_key)
        
        return None
    
    async def _create_chat_instance(self, session_id: str, agent_type: AgentType, 
                            provider: str, model: str) -> LlmChat:
        """Create a new chat instance for the session"""
        api_key = await self._get_api_key(provider)
        if not api_key:
            # For demo purposes, we'll use a placeholder
            # In production, this should raise an error
            api_key = "demo-key"
        
        system_prompt = self.agent_manager.get_system_prompt(agent_type)
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_prompt
        )
        
        # Configure the model
        chat.with_model(provider, model)
        
        return chat
    
    async def send_message(
        self,
        session_id: str,
        message: str,
        agent_type: AgentType = AgentType.MAIN_ASSISTANT,
        provider: str = "gemini",
        model: str = "gemini-2.0-flash"
    ) -> Dict[str, Any]:
        """Execute real agent task instead of just returning text"""
        
        try:
            # Выполнить реальную задачу агента
            result = await self.real_executor.execute_agent_task(
                agent_type=agent_type,
                message=message,
                session_id=session_id,
                context={}
            )
            
            if result["success"]:
                response_text = result["response"]
                
                # Добавить информацию о созданных файлах
                if result.get("created_files"):
                    files_info = "\n\n📁 **Созданные файлы:**\n"
                    for file_path in result["created_files"]:
                        files_info += f"- `{file_path}`\n"
                    response_text += files_info
                
                # Добавить информацию о следующем агенте
                if result.get("next_agent"):
                    response_text += f"\n\n🔄 **Следующий этап:** {result['next_agent']}"
                
                return {
                    "response": response_text,
                    "agent_type": result["agent_type"],
                    "created_files": result.get("created_files", []),
                    "next_agent": result.get("next_agent"),
                    "success": True
                }
            else:
                # Fallback to mock response if agent execution fails
                return {
                    "response": await self._get_mock_response(message, agent_type),
                    "agent_type": agent_type.value,
                    "created_files": [],
                    "next_agent": None,
                    "success": False,
                    "error": result.get("error")
                }
                
        except Exception as e:
            print(f"Error executing agent {agent_type}: {e}")
            # Fallback to mock response on error
            return {
                "response": await self._get_mock_response(message, agent_type),
                "agent_type": agent_type.value,
                "created_files": [],
                "next_agent": None,
                "success": False,
                "error": str(e)
            }
    
    async def process_message(self, message: str, agent_type: AgentType) -> Dict[str, Any]:
        """Basic message processing without tools"""
        return {
            "response": await self._get_mock_response(message, agent_type),
            "agent_type": agent_type.value,
            "success": True
        }
    
    async def process_message_with_tools(self, message: str, agent_type: AgentType) -> Dict[str, Any]:
        """Process message using appropriate tools based on content analysis"""
        message_lower = message.lower()
        
        # Initialize tools manager context
        tools_manager = None
        
        try:
            # Create and initialize tools manager with proper async context
            tools_manager = AgentToolsManager()
            
            async with tools_manager:
                # Анализ веб-сайтов
                if any(phrase in message_lower for phrase in ['анализ', 'сайт', 'https://', 'http://', 'веб-страниц', 'проанализируй']):
                    # Извлекаем URL из сообщения
                    import re
                    urls = re.findall(r'https?://[^\s]+', message)
                    
                    if urls:
                        results = []
                        for url in urls[:3]:  # Ограничиваем до 3 URL
                            try:
                                crawl_result = await tools_manager.crawl_tool(
                                    url=url,
                                    question="Анализируй функциональность, дизайн и особенности сайта"
                                )
                                if crawl_result["success"]:
                                    results.append({
                                        "url": url,
                                        "content": crawl_result["content"][:2000],  # Ограничиваем размер
                                        "title": crawl_result.get("title", "")
                                    })
                            except Exception as e:
                                print(f"Error crawling {url}: {e}")
                                continue
                        
                        if results:
                            analysis = f"""🌐 **Анализ веб-сайтов**

"""
                            for result in results:
                                analysis += f"""**Сайт:** {result['url']}
**Заголовок:** {result['title']}

**Контент и функциональность:**
{result['content']}

---

"""
                            
                            return {
                                "response": analysis,
                                "agent_type": agent_type.value,
                                "tool_results": results,
                                "success": True
                            }
                
                # Поиск в интернете
                elif any(phrase in message_lower for phrase in ['найди', 'поиск', 'ищи', 'search']):
                    search_query = message.replace('найди', '').replace('поиск', '').replace('ищи', '').strip()
                    
                    if search_query:
                        try:
                            search_result = await tools_manager.web_search_tool(search_query)
                            
                            if search_result["success"]:
                                response = f"""🔍 **Результаты поиска для:** "{search_query}"

"""
                                for i, result in enumerate(search_result["results"][:5], 1):
                                    response += f"""**{i}. {result['title']}**
{result['url']}
{result['snippet']}

"""
                                
                                return {
                                    "response": response,
                                    "agent_type": agent_type.value,
                                    "search_results": search_result["results"],
                                    "success": True
                                }
                        except Exception as e:
                            print(f"Error in web search: {e}")
                            # Continue to fallback
                
                # Создание файлов
                elif any(phrase in message_lower for phrase in ['создай файл', 'создать файл', 'напиши код', 'создай проект']):
                    # Определяем тип файла из контекста
                    if 'react' in message_lower or 'jsx' in message_lower:
                        # Создаем React компонент
                        file_content = """import React from 'react';

const MyComponent = () => {
  return (
    <div>
      <h1>Hello, World!</h1>
      <p>This is a React component.</p>
    </div>
  );
};

export default MyComponent;"""
                        
                        try:
                            create_result = await tools_manager.create_file(
                                path="frontend/src/components/MyComponent.jsx",
                                content=file_content
                            )
                            
                            if create_result["success"]:
                                return {
                                    "response": f"""✅ **Файл создан:** `{create_result['path']}`

```jsx
{file_content}
```

Файл успешно создан в проекте!""",
                                    "agent_type": agent_type.value,
                                    "created_files": [create_result["path"]],
                                    "success": True
                                }
                        except Exception as e:
                            print(f"Error creating React file: {e}")
                            # Continue to fallback
                    
                    elif 'python' in message_lower or '.py' in message_lower:
                        # Создаем Python файл
                        file_content = """#!/usr/bin/env python3
\"\"\"
Example Python script
\"\"\"

def main():
    print("Hello, World!")
    print("This is a Python script.")

if __name__ == "__main__":
    main()"""
                        
                        try:
                            create_result = await tools_manager.create_file(
                                path="backend/example_script.py",
                                content=file_content
                            )
                            
                            if create_result["success"]:
                                return {
                                    "response": f"""✅ **Файл создан:** `{create_result['path']}`

```python
{file_content}
```

Файл успешно создан в проекте!""",
                                    "agent_type": agent_type.value,
                                    "created_files": [create_result["path"]],
                                    "success": True
                                }
                        except Exception as e:
                            print(f"Error creating Python file: {e}")
                            # Continue to fallback
                
                # Выполнение команд
                elif any(phrase in message_lower for phrase in ['выполни команду', 'запусти', 'установи', 'npm', 'pip', 'yarn', 'команду date', 'команду pwd', 'команду ls', 'date', 'pwd', 'ls']):
                    # Безопасные команды для демо
                    safe_commands = ['ls', 'pwd', 'echo', 'date', 'whoami', 'node --version', 'python --version']
                    
                    # Извлекаем команду из сообщения
                    command = None
                    for cmd in safe_commands:
                        if cmd in message_lower:
                            command = cmd  
                            break
                    
                    # Альтернативный способ извлечения команды
                    if not command:
                        if 'date' in message_lower:
                            command = 'date'
                        elif 'pwd' in message_lower:
                            command = 'pwd'
                        elif 'ls' in message_lower:
                            command = 'ls'
                    
                    if command:
                        try:
                            exec_result = await tools_manager.execute_bash(command)
                            
                            if exec_result["success"]:
                                return {
                                    "response": f"""💻 **Выполнена команда:** `{command}`

```bash
$ {command}
{exec_result['stdout']}
```

Команда выполнена успешно!""",
                                    "agent_type": agent_type.value,
                                    "command_output": exec_result,
                                    "success": True
                                }
                            else:
                                return {
                                    "response": f"""❌ **Ошибка выполнения команды:** `{command}`

```
{exec_result.get('stderr', exec_result.get('error', 'Unknown error'))}
```""",
                                    "agent_type": agent_type.value,
                                    "success": False
                                }
                        except Exception as e:
                            print(f"Error executing command {command}: {e}")
                            return {
                                "response": f"""❌ **Ошибка выполнения команды:** `{command}`

```
{str(e)}
```""",
                                "agent_type": agent_type.value,
                                "success": False
                            }
                    else:
                        return {
                            "response": "⚠️ Команда не разрешена или не распознана. Доступны только безопасные команды для демонстрации.",
                            "agent_type": agent_type.value,
                            "success": False
                        }
                
                # Просмотр файлов
                elif any(phrase in message_lower for phrase in ['покажи файл', 'открой файл', 'содержимое файла']):
                    # Ищем упоминание пути к файлу
                    import re
                    file_patterns = re.findall(r'[^\s]+\.[a-zA-Z]{2,4}', message)
                    
                    if file_patterns:
                        file_path = file_patterns[0]
                        try:
                            view_result = await tools_manager.view_file(file_path)
                            
                            if view_result["success"]:
                                return {
                                    "response": f"""📄 **Содержимое файла:** `{file_path}`

```
{view_result['content'][:1000]}{'...' if len(view_result['content']) > 1000 else ''}
```""",
                                    "agent_type": agent_type.value,
                                    "file_content": view_result,
                                    "success": True
                                }
                        except Exception as e:
                            print(f"Error viewing file {file_path}: {e}")
                            # Continue to fallback
                
                # Генерация изображений
                elif any(phrase in message_lower for phrase in ['создай изображение', 'генерируй картинку', 'нарисуй']):
                    try:
                        vision_result = await tools_manager.vision_expert_agent(message)
                        
                        if vision_result["success"]:
                            return {
                                "response": f"""🎨 **Изображение создано**

{vision_result['summary']}

[Изображение будет отображено ниже]""",
                                "agent_type": agent_type.value,
                                "generated_images": vision_result.get("image_urls", []),
                                "success": True
                            }
                    except Exception as e:
                        print(f"Error generating image: {e}")
                        # Continue to fallback
                
                # Интеграции
                elif any(phrase in message_lower for phrase in ['интеграция', 'api', 'подключи', 'stripe', 'openai', 'gemini']):
                    # Определяем тип интеграции
                    integration_type = None
                    for service in ['stripe', 'openai', 'gemini', 'anthropic']:
                        if service in message_lower:
                            integration_type = service
                            break
                    
                    if integration_type:
                        try:
                            playbook_result = await tools_manager.integration_playbook_expert(
                                integration=integration_type,
                                constraints=""
                            )
                            
                            if playbook_result["success"]:
                                playbook = playbook_result["playbook"]
                                response = f"""🔧 **Playbook для интеграции {integration_type.upper()}**

**{playbook['title']}**

**Шаги интеграции:**
"""
                                for step in playbook["steps"]:
                                    response += f"- {step}\n"
                                
                                response += f"""
**Пример кода:**
```python
{playbook['code_example']}
```

**Требуемые API ключи:**
"""
                                for key in playbook["required_keys"]:
                                    response += f"- {key}\n"
                                
                                return {
                                    "response": response,
                                    "agent_type": agent_type.value,
                                    "integration_playbook": playbook,
                                    "success": True
                                }
                        except Exception as e:
                            print(f"Error generating integration playbook: {e}")
                            # Continue to fallback
                
                # Если инструменты не применимы, используем стандартную обработку агентов
                print(f"No specific tool matched for message: {message[:50]}...")
                return await self.send_message(
                    session_id="temp",
                    message=message,
                    agent_type=agent_type
                )
                
        except Exception as e:
            print(f"Critical error in process_message_with_tools: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to standard agent processing
            return await self.send_message(
                session_id="temp",
                message=message,
                agent_type=agent_type
            )
    
    async def _get_mock_response(self, message: str, agent_type: AgentType) -> str:
        """Generate mock responses for demo purposes"""
        agent_info = self.agent_manager.get_agent(agent_type)
        agent_name = agent_info.name if agent_info else "AI Assistant"
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        message_lower = message.lower()
        
        if agent_type == AgentType.PROJECT_PLANNER:
            if any(word in message_lower for word in ["plan", "architecture", "design"]):
                return f"""Excellent! As your {agent_name}, I'll help you plan this project. Let me break this down:

**Project Analysis:**
Based on your requirements, I recommend:

1. **Architecture**: Modern full-stack approach with React frontend and FastAPI backend
2. **Database**: MongoDB for flexible data storage
3. **Key Features**: 
   - User authentication
   - Responsive design
   - Real-time updates
   - API-first architecture

**Development Phases:**
1. **Phase 1**: Core backend API and database setup
2. **Phase 2**: Frontend components and routing
3. **Phase 3**: Integration and testing
4. **Phase 4**: Deployment and optimization

Would you like me to elaborate on any specific aspect of the architecture?"""
        
        elif agent_type == AgentType.FRONTEND_DEVELOPER:
            if any(word in message_lower for word in ["react", "component", "ui", "frontend"]):
                return f"""As your {agent_name}, I'll help you build an amazing frontend! Here's my approach:

**Frontend Strategy:**
- **React** with modern hooks and functional components
- **Tailwind CSS** for efficient, responsive styling
- **Component-based architecture** for reusability
- **State management** with Context API or Zustand

**Key Components I'll create:**
- Navigation and layout components
- Interactive UI elements
- Form handling with validation
- Responsive design patterns

**Development Approach:**
1. Set up the project structure
2. Create reusable UI components
3. Implement routing and navigation
4. Add interactive features
5. Optimize for performance

What specific frontend features would you like to focus on first?"""
        
        elif agent_type == AgentType.BACKEND_DEVELOPER:
            if any(word in message_lower for word in ["api", "backend", "database", "server"]):
                return f"""Perfect! As your {agent_name}, I'll build a robust backend for you:

**Backend Architecture:**
- **FastAPI** for high-performance API development
- **MongoDB** for flexible, document-based storage
- **Pydantic** models for data validation
- **JWT authentication** for secure access

**API Design:**
- RESTful endpoints with proper HTTP methods
- Comprehensive error handling
- Input validation and sanitization
- OpenAPI documentation

**Development Plan:**
1. Set up FastAPI project structure
2. Create database models and connections
3. Implement authentication system
4. Build core API endpoints
5. Add comprehensive testing

What specific backend functionality should we prioritize?"""
        
        elif agent_type == AgentType.DEPLOYMENT_ENGINEER:
            if any(word in message_lower for word in ["deploy", "production", "docker"]):
                return f"""Great! As your {agent_name}, I'll get your application production-ready:

**Deployment Strategy:**
- **Docker containerization** for consistent environments
- **Cloud deployment** (AWS, GCP, or Vercel)
- **CI/CD pipeline** for automated deployments
- **Environment management** for different stages

**Infrastructure Setup:**
- Production-ready database configuration
- Load balancing and scaling
- SSL certificates and security
- Monitoring and logging

**Deployment Steps:**
1. Containerize the application
2. Set up cloud infrastructure
3. Configure CI/CD pipeline
4. Deploy to staging environment
5. Production deployment with monitoring

Which deployment platform would you prefer to use?"""
        
        else:  # Main Assistant or others
            return f"""Hi! I'm your {agent_name}. I can help you build full-stack applications, analyze requirements, and coordinate with specialized agents.

Based on your message, I can assist with:
- **Project planning** and architecture design
- **Code development** for both frontend and backend
- **Problem-solving** and debugging
- **Best practices** and recommendations

What specific aspect of your project would you like to work on? I can also connect you with specialized agents:
- **Project Planner** for architecture and requirements
- **Frontend Developer** for React and UI development  
- **Backend Developer** for APIs and databases
- **Deployment Engineer** for production deployment
- **Testing Expert** for quality assurance

How can I help you today?"""
        
        return f"I'm your {agent_name}. How can I help you with your development project?"
    
    def suggest_agent(self, message: str) -> AgentType:
        """Suggest the best agent for handling the message"""
        return self.agent_manager.suggest_agent(message)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available AI models"""
        return [
            {
                "provider": "gemini",
                "name": "gemini-2.0-flash",
                "display_name": "Gemini 2.0 Flash",
                "is_free": True,
                "description": "Fast, efficient model for general development tasks"
            },
            {
                "provider": "openai", 
                "name": "gpt-4o",
                "display_name": "GPT-4o",
                "is_free": False,
                "description": "Advanced model with superior reasoning capabilities"
            },
            {
                "provider": "openai",
                "name": "gpt-4o-mini", 
                "display_name": "GPT-4o Mini",
                "is_free": False,
                "description": "Faster, cost-effective version of GPT-4o"
            }
        ]
    
    def cleanup_session(self, session_id: str):
        """Clean up chat instances for a session"""
        keys_to_remove = [key for key in self.active_chats.keys() if key.startswith(session_id)]
        for key in keys_to_remove:
            del self.active_chats[key]