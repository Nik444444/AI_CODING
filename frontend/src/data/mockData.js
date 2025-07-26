export const mockData = {
  templates: [
    {
      id: 1,
      name: "Clone Spotify",
      description: "Music streaming app",
      icon: "Music",
      color: "bg-green-600",
      prompt: "Create a Spotify clone with music streaming, playlists, search functionality, and user profiles"
    },
    {
      id: 2,
      name: "Task Manager",
      description: "Productivity tool",
      icon: "CheckSquare", 
      color: "bg-yellow-600",
      prompt: "Build a task management app with project organization, deadlines, team collaboration, and progress tracking"
    },
    {
      id: 3,
      name: "AI Pen",
      description: "Writing assistant",
      icon: "PenTool",
      color: "bg-blue-600",
      prompt: "Develop an AI-powered writing assistant with grammar checking, style suggestions, and content generation"
    },
    {
      id: 4,
      name: "Surprise Me",
      description: "Random app idea",
      icon: "Wand2",
      color: "bg-purple-600",
      prompt: "Generate a unique and innovative app idea based on current trends and user needs"
    }
  ],

  recentTasks: [
    {
      id: "task-1",
      name: "E-commerce Platform",
      description: "Full-stack online store with payment integration",
      status: "completed",
      timestamp: "2 hours ago",
      progress: 100
    },
    {
      id: "task-2", 
      name: "Social Media Dashboard",
      description: "Analytics dashboard for social media metrics",
      status: "building",
      timestamp: "1 day ago",
      progress: 75
    },
    {
      id: "task-3",
      name: "Recipe Finder App",
      description: "AI-powered recipe recommendations",
      status: "in_progress",
      timestamp: "3 days ago", 
      progress: 45
    },
    {
      id: "task-4",
      name: "Weather Forecast Widget",
      description: "Real-time weather updates with maps",
      status: "completed",
      timestamp: "1 week ago",
      progress: 100
    }
  ],

  deployedApps: [
    {
      id: "app-1",
      name: "Portfolio Website",
      description: "Personal portfolio with blog and contact form",
      url: "https://portfolio-demo.emergent.dev",
      domain: "portfolio-demo.emergent.dev",
      status: "live",
      deployedAt: "2 days ago"
    },
    {
      id: "app-2",
      name: "Inventory Tracker", 
      description: "Small business inventory management system",
      url: "https://inventory-app.emergent.dev",
      domain: "inventory-app.emergent.dev",
      status: "live",
      deployedAt: "1 week ago"
    },
    {
      id: "app-3",
      name: "Event Planner",
      description: "Event planning and guest management tool",
      url: "https://events-planner.emergent.dev", 
      domain: "events-planner.emergent.dev",
      status: "live",
      deployedAt: "2 weeks ago"
    }
  ],

  aiResponses: [
    {
      agent: "Project Planner",
      content: "Great! I'll help you analyze and clone the Emergent platform. Let me break this down into key components:\n\n1. **Dashboard Interface** - Dark theme with welcome screen\n2. **Chat System** - Real-time AI conversation interface\n3. **AI Agents** - Multiple specialized bots for different tasks\n4. **Project Management** - Task tracking and deployment\n5. **Template System** - Pre-built app starters\n\nShould I start by creating the main dashboard layout, or would you prefer to begin with a specific component?",
      actions: ["Start with dashboard layout", "Create chat interface first", "Set up AI agent system", "Build template gallery"]
    },
    {
      agent: "Frontend Developer", 
      content: "I can help you create the React components! Based on the Emergent interface, I'll need to build:\n\n**Core Components:**\n- Dashboard with dark theme\n- Responsive chat interface\n- Template cards with hover effects\n- Project status tracking\n- Model selection dropdown\n\n**Styling approach:**\n- Tailwind CSS for utility classes\n- Custom animations and transitions\n- Glass morphism effects\n- Responsive grid layouts\n\nWhich component should I prioritize first?",
      actions: ["Build main dashboard", "Create chat UI", "Design template cards", "Set up navigation"]
    },
    {
      agent: "Backend Developer",
      content: "For the backend architecture, I recommend:\n\n**API Structure:**\n- FastAPI with async endpoints\n- MongoDB for data persistence\n- WebSocket for real-time chat\n- Session management for conversations\n\n**AI Integration:**\n- Gemini API for free tier\n- Model switching capability\n- Response streaming\n- Context management\n\n**Key Endpoints:**\n- `/api/chat` - Send messages to AI\n- `/api/projects` - Project CRUD operations\n- `/api/templates` - Template management\n\nShall I start implementing the chat API?",
      actions: ["Set up chat endpoints", "Create project management API", "Implement AI model switching", "Build template system"]
    },
    {
      agent: "Full-Stack Developer",
      content: "Perfect! I'll help you build a complete Emergent clone. Here's my recommended development approach:\n\n**Phase 1: Foundation**\n- Dashboard with dark theme ✓\n- Basic chat interface ✓\n- Template system ✓\n\n**Phase 2: AI Integration**\n- Gemini API integration\n- Model selection (Gemini, GPT, Grok)\n- Context-aware responses\n\n**Phase 3: Advanced Features**\n- Project persistence\n- Code generation\n- Deployment simulation\n\nI can handle both frontend and backend. What's your priority?",
      actions: ["Integrate Gemini API", "Add GPT support", "Build project system", "Create deployment features"]
    },
    {
      agent: "Main Assistant",
      content: "I understand you want to create a complete clone of the Emergent platform! This is an exciting project. Let me help you build:\n\n**Core Features:**\n- AI-powered chat interface\n- Multiple AI model support (Gemini, GPT, Grok)\n- Project template system\n- Real-time development assistance\n- Dark theme UI matching Emergent's design\n\nI can start with any component you'd like. What aspect interests you most?",
      actions: ["Show me the dashboard", "Start coding the chat", "Set up AI models", "Create project templates"]
    }
  ]
};