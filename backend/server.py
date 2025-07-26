from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import List, Optional
from datetime import datetime
import json

# Import our models and services
from models import (
    ChatSession, ChatMessage, Project, AppTemplate, SendMessageRequest, 
    SendMessageResponse, CreateProjectRequest, UpdateProjectRequest,
    AgentType, MessageRole, ProjectStatus
)
from agents import AgentManager
from ai_service import AIService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
agent_manager = AgentManager()
ai_service = AIService()

# Create the main app
app = FastAPI()

# Create API router
api_router = APIRouter(prefix="/api")


# Templates data
DEFAULT_TEMPLATES = [
    {
        "id": "spotify-clone",
        "name": "Clone Spotify",
        "description": "Music streaming app",
        "icon": "Music",
        "color": "bg-green-600",
        "category": "entertainment",
        "prompt": "Create a Spotify clone with music streaming, playlists, search functionality, and user profiles",
        "tech_stack": ["React", "FastAPI", "MongoDB", "Audio API"],
        "features": ["Music playback", "Playlists", "Search", "User profiles", "Social features"]
    },
    {
        "id": "task-manager",
        "name": "Task Manager", 
        "description": "Productivity tool",
        "icon": "CheckSquare",
        "color": "bg-yellow-600",
        "category": "productivity",
        "prompt": "Build a task management app with project organization, deadlines, team collaboration, and progress tracking",
        "tech_stack": ["React", "FastAPI", "MongoDB", "WebSocket"],
        "features": ["Task management", "Project organization", "Team collaboration", "Progress tracking", "Notifications"]
    },
    {
        "id": "ai-pen",
        "name": "AI Pen",
        "description": "Writing assistant", 
        "icon": "PenTool",
        "color": "bg-blue-600",
        "category": "productivity",
        "prompt": "Develop an AI-powered writing assistant with grammar checking, style suggestions, and content generation",
        "tech_stack": ["React", "FastAPI", "OpenAI API", "MongoDB"],
        "features": ["Grammar checking", "Style suggestions", "Content generation", "Document management", "AI assistance"]
    },
    {
        "id": "surprise-me",
        "name": "Surprise Me",
        "description": "Random app idea",
        "icon": "Wand2", 
        "color": "bg-purple-600",
        "category": "creative",
        "prompt": "Generate a unique and innovative app idea based on current trends and user needs",
        "tech_stack": ["React", "FastAPI", "MongoDB", "AI APIs"],
        "features": ["Random generation", "Trend analysis", "Innovation scoring", "Idea refinement", "Market research"]
    }
]


# Chat endpoints
@api_router.post("/chat/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """Send a message to an AI agent"""
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create new session
            session = ChatSession(
                active_agent=request.agent_type or AgentType.MAIN_ASSISTANT,
                model_provider=request.model_provider,
                model_name=request.model_name
            )
            await db.chat_sessions.insert_one(session.dict())
            session_id = session.id
        else:
            # Update existing session
            await db.chat_sessions.update_one(
                {"id": session_id},
                {"$set": {"updated_at": datetime.utcnow()}}
            )
        
        # Determine agent type
        agent_type = request.agent_type
        if not agent_type:
            # Suggest best agent based on message content
            agent_type = ai_service.suggest_agent(request.message)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.USER,
            content=request.message
        )
        await db.chat_messages.insert_one(user_message.dict())
        
        # Get AI response
        ai_response = await ai_service.send_message(
            session_id=session_id,
            message=request.message,
            agent_type=agent_type,
            provider=request.model_provider,
            model=request.model_name
        )
        
        # Generate suggested actions based on context
        suggested_actions = _generate_suggested_actions(request.message, agent_type)
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            agent_type=agent_type,
            suggested_actions=suggested_actions
        )
        await db.chat_messages.insert_one(assistant_message.dict())
        
        return SendMessageResponse(
            session_id=session_id,
            message=assistant_message,
            suggested_actions=suggested_actions
        )
        
    except Exception as e:
        logging.error(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_suggested_actions(message: str, agent_type: AgentType) -> List[str]:
    """Generate contextual suggested actions"""
    actions = []
    message_lower = message.lower()
    
    if agent_type == AgentType.PROJECT_PLANNER:
        actions = [
            "Show me the tech stack recommendations",
            "Create a detailed development roadmap", 
            "Help me define user requirements",
            "Switch to Frontend Developer for UI design"
        ]
    elif agent_type == AgentType.FRONTEND_DEVELOPER:
        actions = [
            "Generate React component structure",
            "Create responsive design mockup",
            "Set up routing and navigation",
            "Switch to Backend Developer for API integration"
        ]
    elif agent_type == AgentType.BACKEND_DEVELOPER:
        actions = [
            "Design database schema",
            "Create API endpoints structure", 
            "Set up authentication system",
            "Switch to Deployment Engineer for production setup"
        ]
    elif agent_type == AgentType.DEPLOYMENT_ENGINEER:
        actions = [
            "Create Docker configuration",
            "Set up CI/CD pipeline",
            "Configure cloud deployment",
            "Set up monitoring and logging"
        ]
    else:
        actions = [
            "Create a new project from this idea",
            "Switch to Project Planner for detailed planning",
            "Get started with a template",
            "Explore similar project examples"
        ]
    
    return actions[:4]  # Limit to 4 actions


@api_router.get("/chat/session/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for a chat session"""
    try:
        messages = await db.chat_messages.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
        return [ChatMessage(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/chat/sessions")
async def get_chat_sessions():
    """Get all chat sessions"""
    try:
        sessions = await db.chat_sessions.find().sort("updated_at", -1).to_list(100)
        return [ChatSession(**session) for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    try:
        project = Project(
            name=request.name,
            description=request.description,
            template_id=request.template_id,
            tech_stack=request.tech_stack,
            status=ProjectStatus.PLANNING
        )
        await db.projects.insert_one(project.dict())
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    """Get all projects"""
    try:
        projects = await db.projects.find().sort("updated_at", -1).to_list(100)
        return [Project(**project) for project in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project"""
    try:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return Project(**project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, request: UpdateProjectRequest):
    """Update a project"""
    try:
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.projects.update_one(
            {"id": project_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = await db.projects.find_one({"id": project_id})
        return Project(**project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Template endpoints
@api_router.get("/templates", response_model=List[AppTemplate])
async def get_templates():
    """Get all app templates"""
    try:
        # Check if templates exist in database
        templates_count = await db.templates.count_documents({})
        
        if templates_count == 0:
            # Insert default templates
            template_docs = []
            for template_data in DEFAULT_TEMPLATES:
                template = AppTemplate(**template_data)
                template_docs.append(template.dict())
            
            if template_docs:
                await db.templates.insert_many(template_docs)
        
        # Return templates from database
        templates = await db.templates.find().to_list(100)
        return [AppTemplate(**template) for template in templates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/templates/{template_id}", response_model=AppTemplate)
async def get_template(template_id: str):
    """Get a specific template"""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return AppTemplate(**template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent endpoints
@api_router.get("/agents")
async def get_agents():
    """Get all available AI agents"""
    try:
        agents = agent_manager.get_all_agents()
        return [agent.dict() for agent in agents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/models")
async def get_models():
    """Get all available AI models"""
    try:
        return ai_service.get_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@api_router.get("/")
async def root():
    return {"message": "Emergent Clone API is running!", "status": "healthy"}


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "ai_service": "active",
            "agents": len(agent_manager.get_all_agents())
        }
    }


# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware with production domains
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # In production, replace with specific domains: ["https://your-site.netlify.app", "http://localhost:3000"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
