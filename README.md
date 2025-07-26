# 🚀 Emergent Clone - AI Development Platform

A comprehensive clone of the Emergent AI development platform built with modern web technologies.

## ✨ Features

- **7 Specialized AI Agents**: Main Assistant, Project Planner, Frontend/Backend/Fullstack Developers, Deployment Engineer, and Testing Expert
- **Multi-Model AI Support**: Gemini (free), OpenAI GPT-4o (premium), and more
- **Project Management**: Full CRUD operations for development projects
- **Template System**: Pre-built templates for common app types
- **Real-time Chat**: Interactive conversations with AI agents
- **SQLite Database**: Lightweight, serverless database with automatic persistence
- **Modern UI**: Dark theme with Tailwind CSS
- **Production Ready**: Docker containers, health checks, and deployment configs

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite + SQLAlchemy** - Lightweight database with async ORM
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

### Frontend  
- **React 19** - Latest React with modern features
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon system
- **Axios** - HTTP client for API calls

### AI Integration
- **Google Gemini** - Free AI model for development
- **OpenAI GPT-4o** - Premium AI model (optional)
- **Emergent Integrations** - Custom AI service wrapper

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and Yarn
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd emergent-clone
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
```

3. **Frontend Setup**  
```bash
cd frontend
yarn install
yarn start
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

## 📁 Project Structure

```
emergent-clone/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main FastAPI application
│   ├── models.py           # Pydantic models
│   ├── database.py         # SQLite database setup
│   ├── agents.py           # AI agent management
│   ├── ai_service.py       # AI integration service
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Docker container config
│   └── fly.toml           # Fly.io deployment config
├── frontend/               # React frontend
│   ├── src/               # React source code
│   ├── package.json       # Node.js dependencies
│   ├── tailwind.config.js # Tailwind CSS config
│   └── netlify.toml       # Netlify deployment config
├── tests/                 # Test files
└── README.md             # This file
```

## 🗄 Database Schema

The application uses SQLite with the following main tables:

- **chat_sessions** - User chat sessions with AI agents
- **chat_messages** - Individual messages in conversations
- **projects** - Development projects created by users
- **app_templates** - Pre-built project templates

All tables are created automatically on first run.

## 🔧 Configuration

### Environment Variables

**Backend (.env)**:
```env
# Optional AI API Keys (app works with mock responses if not provided)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

**Frontend (.env)**:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🚀 Deployment

### Quick Deploy Commands

**Backend (Fly.io)**:
```bash
cd backend
fly launch --no-deploy
fly deploy
```

**Frontend (Netlify)**:
```bash
cd frontend  
npm run build
# Upload build/ folder to Netlify
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Backend tests
cd backend
python backend_test.py

# Frontend tests (if available)
cd frontend
yarn test
```

## 🔮 AI Agents

The platform includes 7 specialized AI agents:

1. **Main Assistant** - General-purpose conversational AI
2. **Project Planner** - Helps plan and structure projects
3. **Frontend Developer** - Specializes in React, CSS, and UI/UX
4. **Backend Developer** - Focuses on APIs, databases, and server logic
5. **Fullstack Developer** - Combines frontend and backend expertise
6. **Deployment Engineer** - Handles deployment and DevOps tasks
7. **Testing Expert** - Focuses on testing strategies and quality assurance

## 📊 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/agents` - List all AI agents
- `GET /api/models` - List available AI models

### Chat System
- `POST /api/chat/send` - Send message to AI agent
- `GET /api/chat/sessions` - Get all chat sessions
- `GET /api/chat/session/{id}/messages` - Get session messages

### Project Management
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get specific project
- `PUT /api/projects/{id}` - Update project

### Templates
- `GET /api/templates` - List all templates
- `GET /api/templates/{id}` - Get specific template

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment issues
- Review [API_KEYS_SETUP.md](API_KEYS_SETUP.md) for AI integration help
- Open an issue for bugs or feature requests

---

**Built with ❤️ using modern web technologies**
