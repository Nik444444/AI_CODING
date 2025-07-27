from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import uuid
from typing import List, Optional
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

# Import our models and services
from models import (
    ChatSession, ChatMessage, Project, AppTemplate, SendMessageRequest, 
    SendMessageResponse, CreateProjectRequest, UpdateProjectRequest,
    AgentType, MessageRole, ProjectStatus, APIKey, CreateAPIKeyRequest, UpdateAPIKeyRequest
)
from agents import AgentManager, AgentCollaborationManager
from ai_service import AIService
from database import (
    get_db, create_tables, ChatSessionDB, ChatMessageDB, ProjectDB, AppTemplateDB,
    APIKeyDB, serialize_json_field, deserialize_json_field
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize services
agent_manager = AgentManager()
collaboration_manager = AgentCollaborationManager()
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
        "tech_stack": ["React", "FastAPI", "SQLite", "Audio API"],
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
        "tech_stack": ["React", "FastAPI", "SQLite", "WebSocket"],
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
        "tech_stack": ["React", "FastAPI", "OpenAI API", "SQLite"],
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
        "tech_stack": ["React", "FastAPI", "SQLite", "AI APIs"],
        "features": ["Random generation", "Trend analysis", "Innovation scoring", "Idea refinement", "Market research"]
    }
]


# Chat endpoints
@api_router.post("/chat/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, db: AsyncSession = Depends(get_db)):
    """Send a message to an AI agent"""
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create new session
            session = ChatSessionDB(
                id=str(datetime.utcnow().timestamp()),
                active_agent=request.agent_type or AgentType.MAIN_ASSISTANT,
                model_provider=request.model_provider,
                model_name=request.model_name,
                context=serialize_json_field({})
            )
            db.add(session)
            await db.commit()
            session_id = session.id
        else:
            # Update existing session
            stmt = update(ChatSessionDB).where(ChatSessionDB.id == session_id).values(
                updated_at=datetime.utcnow()
            )
            await db.execute(stmt)
            await db.commit()
        
        # Determine agent type
        agent_type = request.agent_type
        if not agent_type:
            # Suggest best agent based on message content
            agent_type = ai_service.suggest_agent(request.message)
        
        # Save user message
        user_message = ChatMessageDB(
            id=f"msg_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            role=MessageRole.USER,
            content=request.message,
            message_metadata=serialize_json_field({}),
            suggested_actions=serialize_json_field([])
        )
        db.add(user_message)
        await db.commit()
        
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
        assistant_message_db = ChatMessageDB(
            id=f"msg_{datetime.utcnow().timestamp()}_assistant",
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            agent_type=agent_type,
            message_metadata=serialize_json_field({}),
            suggested_actions=serialize_json_field(suggested_actions)
        )
        db.add(assistant_message_db)
        await db.commit()
        
        # Convert to response model
        assistant_message = ChatMessage(
            id=assistant_message_db.id,
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            agent_type=agent_type,
            timestamp=assistant_message_db.timestamp,
            suggested_actions=suggested_actions
        )
        
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
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages for a chat session"""
    try:
        stmt = select(ChatMessageDB).where(ChatMessageDB.session_id == session_id).order_by(ChatMessageDB.timestamp)
        result = await db.execute(stmt)
        messages_db = result.scalars().all()
        
        messages = []
        for msg_db in messages_db:
            messages.append(ChatMessage(
                id=msg_db.id,
                session_id=msg_db.session_id,
                role=msg_db.role,
                content=msg_db.content,
                agent_type=msg_db.agent_type,
                timestamp=msg_db.timestamp,
                metadata=deserialize_json_field(msg_db.message_metadata),
                suggested_actions=deserialize_json_field(msg_db.suggested_actions, "list")
            ))
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/chat/sessions")
async def get_chat_sessions(db: AsyncSession = Depends(get_db)):
    """Get all chat sessions"""
    try:
        stmt = select(ChatSessionDB).order_by(ChatSessionDB.updated_at.desc())
        result = await db.execute(stmt)
        sessions_db = result.scalars().all()
        
        sessions = []
        for session_db in sessions_db:
            sessions.append(ChatSession(
                id=session_db.id,
                title=session_db.title,
                created_at=session_db.created_at,
                updated_at=session_db.updated_at,
                active_agent=session_db.active_agent,
                model_provider=session_db.model_provider,
                model_name=session_db.model_name,
                context=deserialize_json_field(session_db.context)
            ))
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(request: CreateProjectRequest, db: AsyncSession = Depends(get_db)):
    """Create a new project"""
    try:
        project_db = ProjectDB(
            id=f"proj_{datetime.utcnow().timestamp()}",
            name=request.name,
            description=request.description,
            template_id=request.template_id,
            tech_stack=serialize_json_field(request.tech_stack),
            status=ProjectStatus.PLANNING,
            metadata=serialize_json_field({})
        )
        db.add(project_db)
        await db.commit()
        
        project = Project(
            id=project_db.id,
            name=project_db.name,
            description=project_db.description,
            status=project_db.status,
            template_id=project_db.template_id,
            created_at=project_db.created_at,
            updated_at=project_db.updated_at,
            progress=project_db.progress,
            tech_stack=deserialize_json_field(project_db.tech_stack, "list"),
            repository_url=project_db.repository_url,
            deployment_url=project_db.deployment_url,
            chat_session_id=project_db.chat_session_id,
            metadata=deserialize_json_field(project_db.metadata)
        )
        
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/projects", response_model=List[Project])
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects"""
    try:
        stmt = select(ProjectDB).order_by(ProjectDB.updated_at.desc())
        result = await db.execute(stmt)
        projects_db = result.scalars().all()
        
        projects = []
        for project_db in projects_db:
            projects.append(Project(
                id=project_db.id,
                name=project_db.name,
                description=project_db.description,
                status=project_db.status,
                template_id=project_db.template_id,
                created_at=project_db.created_at,
                updated_at=project_db.updated_at,
                progress=project_db.progress,
                tech_stack=deserialize_json_field(project_db.tech_stack, "list"),
                repository_url=project_db.repository_url,
                deployment_url=project_db.deployment_url,
                chat_session_id=project_db.chat_session_id,
                metadata=deserialize_json_field(project_db.metadata)
            ))
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific project"""
    try:
        stmt = select(ProjectDB).where(ProjectDB.id == project_id)
        result = await db.execute(stmt)
        project_db = result.scalar_one_or_none()
        
        if not project_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = Project(
            id=project_db.id,
            name=project_db.name,
            description=project_db.description,
            status=project_db.status,
            template_id=project_db.template_id,
            created_at=project_db.created_at,
            updated_at=project_db.updated_at,
            progress=project_db.progress,
            tech_stack=deserialize_json_field(project_db.tech_stack, "list"),
            repository_url=project_db.repository_url,
            deployment_url=project_db.deployment_url,
            chat_session_id=project_db.chat_session_id,
            metadata=deserialize_json_field(project_db.metadata)
        )
        
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, request: UpdateProjectRequest, db: AsyncSession = Depends(get_db)):
    """Update a project"""
    try:
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = update(ProjectDB).where(ProjectDB.id == project_id).values(**update_data)
        result = await db.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        await db.commit()
        
        # Get updated project
        stmt = select(ProjectDB).where(ProjectDB.id == project_id)
        result = await db.execute(stmt)
        project_db = result.scalar_one()
        
        project = Project(
            id=project_db.id,
            name=project_db.name,
            description=project_db.description,
            status=project_db.status,
            template_id=project_db.template_id,
            created_at=project_db.created_at,
            updated_at=project_db.updated_at,
            progress=project_db.progress,
            tech_stack=deserialize_json_field(project_db.tech_stack, "list"),
            repository_url=project_db.repository_url,
            deployment_url=project_db.deployment_url,
            chat_session_id=project_db.chat_session_id,
            metadata=deserialize_json_field(project_db.metadata)
        )
        
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Template endpoints
@api_router.get("/templates", response_model=List[AppTemplate])
async def get_templates(db: AsyncSession = Depends(get_db)):
    """Get all app templates"""
    try:
        # Check if templates exist in database
        stmt = select(AppTemplateDB)
        result = await db.execute(stmt)
        templates_db = result.scalars().all()
        
        if not templates_db:
            # Insert default templates
            for template_data in DEFAULT_TEMPLATES:
                template_db = AppTemplateDB(
                    id=template_data["id"],
                    name=template_data["name"],
                    description=template_data["description"],
                    icon=template_data["icon"],
                    color=template_data["color"],
                    category=template_data["category"],
                    prompt=template_data["prompt"],
                    tech_stack=serialize_json_field(template_data["tech_stack"]),
                    features=serialize_json_field(template_data["features"])
                )
                db.add(template_db)
            
            await db.commit()
            
            # Get templates again
            stmt = select(AppTemplateDB)
            result = await db.execute(stmt)
            templates_db = result.scalars().all()
        
        templates = []
        for template_db in templates_db:
            templates.append(AppTemplate(
                id=template_db.id,
                name=template_db.name,
                description=template_db.description,
                icon=template_db.icon,
                color=template_db.color,
                category=template_db.category,
                prompt=template_db.prompt,
                tech_stack=deserialize_json_field(template_db.tech_stack, "list"),
                features=deserialize_json_field(template_db.features, "list")
            ))
        
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/templates/{template_id}", response_model=AppTemplate)
async def get_template(template_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific template"""
    try:
        stmt = select(AppTemplateDB).where(AppTemplateDB.id == template_id)
        result = await db.execute(stmt)
        template_db = result.scalar_one_or_none()
        
        if not template_db:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template = AppTemplate(
            id=template_db.id,
            name=template_db.name,
            description=template_db.description,
            icon=template_db.icon,
            color=template_db.color,
            category=template_db.category,
            prompt=template_db.prompt,
            tech_stack=deserialize_json_field(template_db.tech_stack, "list"),
            features=deserialize_json_field(template_db.features, "list")
        )
        
        return template
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


# API Key endpoints
@api_router.post("/api-keys", response_model=APIKey)
async def create_api_key(request: CreateAPIKeyRequest, db: AsyncSession = Depends(get_db)):
    """Create a new API key"""
    try:
        # Validate provider
        valid_providers = ["gemini", "openai", "anthropic"]
        if request.provider not in valid_providers:
            raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {valid_providers}")
        
        # Check if provider already has a key
        stmt = select(APIKeyDB).where(APIKeyDB.provider == request.provider)
        result = await db.execute(stmt)
        existing_key = result.scalar_one_or_none()
        
        if existing_key:
            raise HTTPException(status_code=400, detail=f"API key for {request.provider} already exists. Use PUT to update.")
        
        api_key_db = APIKeyDB(
            id=str(uuid.uuid4()),
            provider=request.provider,
            api_key=request.api_key,
            display_name=request.display_name or f"{request.provider.title()} API Key",
            is_active=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            key_metadata=serialize_json_field({})
        )
        
        db.add(api_key_db)
        await db.commit()
        await db.refresh(api_key_db)
        
        # Convert to response model (mask the key)
        api_key = APIKey(
            id=api_key_db.id,
            provider=api_key_db.provider,
            api_key="*" * 20 + api_key_db.api_key[-4:] if len(api_key_db.api_key) > 4 else "*" * len(api_key_db.api_key),
            display_name=api_key_db.display_name,
            is_active=bool(api_key_db.is_active),
            created_at=api_key_db.created_at,
            updated_at=api_key_db.updated_at,
            metadata=deserialize_json_field(api_key_db.key_metadata)
        )
        
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/api-keys", response_model=List[APIKey])
async def get_api_keys(db: AsyncSession = Depends(get_db)):
    """Get all API keys (with masked keys)"""
    try:
        stmt = select(APIKeyDB).order_by(APIKeyDB.created_at.desc())
        result = await db.execute(stmt)
        api_keys_db = result.scalars().all()
        
        # Convert to response models (mask the keys)
        api_keys = []
        for key_db in api_keys_db:
            api_key = APIKey(
                id=key_db.id,
                provider=key_db.provider,
                api_key="*" * 20 + key_db.api_key[-4:] if len(key_db.api_key) > 4 else "*" * len(key_db.api_key),
                display_name=key_db.display_name,
                is_active=bool(key_db.is_active),
                created_at=key_db.created_at,
                updated_at=key_db.updated_at,
                metadata=deserialize_json_field(key_db.key_metadata)
            )
            api_keys.append(api_key)
        
        return api_keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/api-keys/{key_id}", response_model=APIKey)
async def get_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific API key (with masked key)"""
    try:
        stmt = select(APIKeyDB).where(APIKeyDB.id == key_id)
        result = await db.execute(stmt)
        key_db = result.scalar_one_or_none()
        
        if not key_db:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Convert to response model (mask the key)
        api_key = APIKey(
            id=key_db.id,
            provider=key_db.provider,
            api_key="*" * 20 + key_db.api_key[-4:] if len(key_db.api_key) > 4 else "*" * len(key_db.api_key),
            display_name=key_db.display_name,
            is_active=bool(key_db.is_active),
            created_at=key_db.created_at,
            updated_at=key_db.updated_at,
            metadata=deserialize_json_field(key_db.key_metadata)
        )
        
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/api-keys/{key_id}", response_model=APIKey)
async def update_api_key(key_id: str, request: UpdateAPIKeyRequest, db: AsyncSession = Depends(get_db)):
    """Update an API key"""
    try:
        stmt = select(APIKeyDB).where(APIKeyDB.id == key_id)
        result = await db.execute(stmt)
        key_db = result.scalar_one_or_none()
        
        if not key_db:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Update fields
        update_data = {}
        if request.api_key is not None:
            update_data["api_key"] = request.api_key
        if request.display_name is not None:
            update_data["display_name"] = request.display_name
        if request.is_active is not None:
            update_data["is_active"] = int(request.is_active)
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            stmt = update(APIKeyDB).where(APIKeyDB.id == key_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            
            # Refresh the object
            stmt = select(APIKeyDB).where(APIKeyDB.id == key_id)
            result = await db.execute(stmt)
            key_db = result.scalar_one()
        
        # Convert to response model (mask the key)
        api_key = APIKey(
            id=key_db.id,
            provider=key_db.provider,
            api_key="*" * 20 + key_db.api_key[-4:] if len(key_db.api_key) > 4 else "*" * len(key_db.api_key),
            display_name=key_db.display_name,
            is_active=bool(key_db.is_active),
            created_at=key_db.created_at,
            updated_at=key_db.updated_at,
            metadata=deserialize_json_field(key_db.key_metadata)
        )
        
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an API key"""
    try:
        stmt = select(APIKeyDB).where(APIKeyDB.id == key_id)
        result = await db.execute(stmt)
        key_db = result.scalar_one_or_none()
        
        if not key_db:
            raise HTTPException(status_code=404, detail="API key not found")
        
        stmt = delete(APIKeyDB).where(APIKeyDB.id == key_id)
        await db.execute(stmt)
        await db.commit()
        
        return {"message": f"API key for {key_db.provider} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent Collaboration endpoints
@api_router.post("/collaboration/create")
async def create_collaboration(
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent collaboration session"""
    try:
        collaboration = collaboration_manager.create_collaboration(
            project_id=request["project_id"],
            session_id=request["session_id"],
            user_request=request["user_request"]
        )
        
        return {
            "collaboration_id": collaboration.id,
            "project_id": collaboration.project_id,
            "session_id": collaboration.session_id,
            "current_phase": collaboration.current_phase,
            "active_agents": collaboration.active_agents,
            "initial_task": collaboration.agent_tasks[0] if collaboration.agent_tasks else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/collaboration/{session_id}/status")
async def get_collaboration_status(session_id: str):
    """Get detailed status of collaboration session"""
    try:
        status = collaboration_manager.get_collaboration_status(session_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/collaboration/{session_id}/tasks")
async def get_collaboration_tasks(session_id: str):
    """Get all tasks for a collaboration session"""
    try:
        tasks = collaboration_manager.get_active_tasks(session_id)
        return {
            "session_id": session_id,
            "active_tasks": len(tasks),
            "tasks": [
                {
                    "id": task.id,
                    "agent_type": task.agent_type,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "estimated_duration": task.estimated_duration,
                    "deliverables": task.deliverables,
                    "handoff_to": task.handoff_to
                }
                for task in tasks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/collaboration/task/{task_id}/update")
async def update_task_status(
    task_id: str,
    request: dict
):
    """Update task status"""
    try:
        from models import AgentStatus
        
        status = request.get("status")
        message = request.get("message", "")
        
        # Convert string to AgentStatus enum
        try:
            agent_status = AgentStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status: {status}. Valid statuses: {[s.value for s in AgentStatus]}"
            )
        
        success = collaboration_manager.update_task_status(
            task_id=task_id,
            status=agent_status,
            message=message
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"success": True, "task_id": task_id, "new_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/collaboration/handoff")
async def create_handoff(
    from_agent: str,
    to_agent: str,
    collaboration_id: str,
    message: str,
    context: Optional[dict] = None
):
    """Create a handoff task from one agent to another"""
    try:
        from models import AgentType
        
        # Convert strings to AgentType enums
        try:
            from_agent_type = AgentType(from_agent)
            to_agent_type = AgentType(to_agent)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {e}")
        
        task = collaboration_manager.create_handoff_task(
            from_agent=from_agent_type,
            to_agent=to_agent_type,
            collaboration_id=collaboration_id,
            message=message,
            context=context or {}
        )
        
        return {
            "handoff_created": True,
            "task_id": task.id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_title": task.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/collaboration/{session_id}/agents")
async def get_collaboration_agents(session_id: str):
    """Get information about active agents in collaboration"""
    try:
        collaboration = collaboration_manager.get_collaboration(session_id)
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        agents_info = []
        for agent_type in collaboration.active_agents:
            agent_info = agent_manager.get_agent(agent_type)
            if agent_info:
                agents_info.append({
                    "type": agent_info.type,
                    "name": agent_info.name,
                    "description": agent_info.description,
                    "specialization": agent_info.specialization,
                    "status": agent_info.status,
                    "current_task": agent_info.current_task,
                    "typical_handoff_agents": agent_info.typical_handoff_agents,
                    "typical_duration": agent_info.typical_duration
                })
        
        return {
            "session_id": session_id,
            "active_agents": agents_info,
            "total_agents": len(agents_info)
        }
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
            "database": "sqlite_connected",
            "ai_service": "active",
            "agents": len(agent_manager.get_all_agents())
        }
    }


# Add CORS middleware first (before including router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kodix.netlify.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the router in the main app
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create tables on startup
@app.on_event("startup")
async def startup_event():
    await create_tables()
    logger.info("Database tables created successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
