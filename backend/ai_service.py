import os
import asyncio
from typing import List, Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from models import AgentType, ChatMessage, MessageRole
from agents import AgentManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import APIKeyDB, AsyncSessionLocal


class AIService:
    """Service for handling AI interactions with different models and agents"""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.active_chats: Dict[str, LlmChat] = {}
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider"""
        key_mapping = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        env_key = key_mapping.get(provider)
        if env_key:
            return os.environ.get(env_key)
        return None
    
    def _create_chat_instance(self, session_id: str, agent_type: AgentType, 
                            provider: str, model: str) -> LlmChat:
        """Create a new chat instance for the session"""
        api_key = self._get_api_key(provider)
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
    ) -> str:
        """Send a message to the AI agent and get response"""
        
        # Get or create chat instance for this session
        chat_key = f"{session_id}_{agent_type}_{provider}_{model}"
        
        if chat_key not in self.active_chats:
            self.active_chats[chat_key] = self._create_chat_instance(
                session_id, agent_type, provider, model
            )
        
        chat = self.active_chats[chat_key]
        
        # Create user message
        user_message = UserMessage(text=message)
        
        try:
            # For demo purposes, return a mock response if no API key
            api_key = self._get_api_key(provider)
            if not api_key or api_key == "demo-key":
                return await self._get_mock_response(message, agent_type)
            
            # Send message to AI
            response = await chat.send_message(user_message)
            return response
            
        except Exception as e:
            # Fallback to mock response on error
            return await self._get_mock_response(message, agent_type)
    
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