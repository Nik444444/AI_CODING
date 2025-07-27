from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import json
import os

# SQLite database URL - use /data for persistent storage in production
DATABASE_PATH = os.getenv("DATABASE_PATH", "./emergent_clone.db")
if not DATABASE_PATH.startswith("/"):
    # Ensure absolute path for persistent storage
    if os.path.exists("/data"):
        DATABASE_PATH = f"/data/{os.path.basename(DATABASE_PATH)}"

DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


# Database Models
class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    active_agent = Column(String, default="main_assistant")
    model_provider = Column(String, default="gemini")
    model_name = Column(String, default="gemini-2.0-flash")
    context = Column(Text, default="{}")  # JSON as text


class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    agent_type = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(Text, default="{}")  # JSON as text
    suggested_actions = Column(Text, default="[]")  # JSON array as text


class ProjectDB(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="planning")
    template_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Integer, default=0)
    tech_stack = Column(Text, default="[]")  # JSON array as text
    repository_url = Column(String, nullable=True)
    deployment_url = Column(String, nullable=True)
    chat_session_id = Column(String, nullable=True)
    project_metadata = Column(Text, default="{}")  # JSON as text


class AppTemplateDB(Base):
    __tablename__ = "app_templates"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False)
    color = Column(String, nullable=False)
    category = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    tech_stack = Column(Text, default="[]")  # JSON array as text
    features = Column(Text, default="[]")  # JSON array as text


class AgentTaskDB(Base):
    __tablename__ = "agent_tasks"
    
    id = Column(String, primary_key=True)
    agent_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="idle")
    priority = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    actual_duration = Column(Integer, nullable=True)
    dependencies = Column(Text, default="[]")  # JSON array as text
    deliverables = Column(Text, default="[]")  # JSON array as text
    handoff_to = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    task_metadata = Column(Text, default="{}")  # JSON as text


class AgentHandoffDB(Base):
    __tablename__ = "agent_handoffs"
    
    id = Column(String, primary_key=True)
    from_agent = Column(String, nullable=False)
    to_agent = Column(String, nullable=False)
    task_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    context = Column(Text, default="{}")  # JSON as text
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")


class AgentCollaborationDB(Base):
    __tablename__ = "agent_collaborations"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    active_agents = Column(Text, default="[]")  # JSON array as text
    current_phase = Column(String, default="planning")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class APIKeyDB(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True)
    provider = Column(String, nullable=False)  # "gemini", "openai", "anthropic"
    api_key = Column(Text, nullable=False)  # Store encrypted or plain text
    display_name = Column(String, nullable=True)
    is_active = Column(Integer, default=1)  # SQLite doesn't have boolean, use integer
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    key_metadata = Column(Text, default="{}")  # JSON as text


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Helper functions for JSON serialization
def serialize_json_field(value):
    """Convert Python object to JSON string"""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value or ("{}" if isinstance(value, dict) else "[]")


def deserialize_json_field(value, default_type="dict"):
    """Convert JSON string to Python object"""
    if not value:
        return {} if default_type == "dict" else []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {} if default_type == "dict" else []