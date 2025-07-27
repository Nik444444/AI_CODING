from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class AgentType(str, Enum):
    MAIN_ASSISTANT = "main_assistant"
    PROJECT_PLANNER = "project_planner"
    DESIGN_AGENT = "design_agent"
    FRONTEND_DEVELOPER = "frontend_developer"
    BACKEND_DEVELOPER = "backend_developer"
    FULLSTACK_DEVELOPER = "fullstack_developer"
    INTEGRATION_AGENT = "integration_agent"
    VERSION_CONTROL_AGENT = "version_control_agent"
    TESTING_EXPERT = "testing_expert"
    DEPLOYMENT_ENGINEER = "deployment_engineer"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    BUILDING = "building"
    COMPLETED = "completed"
    DEPLOYED = "deployed"
    FAILED = "failed"


# Chat Models
class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    active_agent: AgentType = AgentType.MAIN_ASSISTANT
    model_provider: str = "gemini"
    model_name: str = "gemini-2.0-flash"
    context: Dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: MessageRole
    content: str
    agent_type: Optional[AgentType] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    suggested_actions: List[str] = Field(default_factory=list)


# Project Models
class AppTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str
    color: str
    category: str
    prompt: str
    tech_stack: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    status: ProjectStatus = ProjectStatus.PLANNING
    template_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    progress: int = 0
    tech_stack: List[str] = Field(default_factory=list)
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None
    chat_session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# API Request/Response Models
class SendMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    agent_type: Optional[AgentType] = None
    template_id: Optional[str] = None
    model_provider: str = "gemini"
    model_name: str = "gemini-2.0-flash"


class SendMessageResponse(BaseModel):
    session_id: str
    message: ChatMessage
    suggested_actions: List[str] = Field(default_factory=list)


class CreateProjectRequest(BaseModel):
    name: str
    description: str
    template_id: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    progress: Optional[int] = None
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None


class AgentInfo(BaseModel):
    type: AgentType
    name: str
    description: str
    specialization: str
    system_prompt: str
    capabilities: List[str]


class ModelInfo(BaseModel):
    provider: str
    name: str
    display_name: str
    is_free: bool
    description: str


# API Key Models
class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str  # "gemini", "openai", "anthropic"
    api_key: str
    display_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateAPIKeyRequest(BaseModel):
    provider: str
    api_key: str
    display_name: Optional[str] = None


class UpdateAPIKeyRequest(BaseModel):
    api_key: Optional[str] = None
    display_name: Optional[str] = None
    is_active: Optional[bool] = None