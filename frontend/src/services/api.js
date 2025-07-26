import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API
export const chatAPI = {
  sendMessage: async (sessionId, message, agentType = null, modelProvider = 'gemini', modelName = 'gemini-2.0-flash') => {
    const response = await apiClient.post('/chat/send', {
      session_id: sessionId,
      message,
      agent_type: agentType,
      model_provider: modelProvider,
      model_name: modelName
    });
    return response.data;
  },

  getSessionMessages: async (sessionId) => {
    const response = await apiClient.get(`/chat/session/${sessionId}/messages`);
    return response.data;
  },

  getChatSessions: async () => {
    const response = await apiClient.get('/chat/sessions');
    return response.data;
  }
};

// Project API
export const projectAPI = {
  createProject: async (name, description, templateId = null, techStack = []) => {
    const response = await apiClient.post('/projects', {
      name,
      description,
      template_id: templateId,
      tech_stack: techStack
    });
    return response.data;
  },

  getProjects: async () => {
    const response = await apiClient.get('/projects');
    return response.data;
  },

  getProject: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}`);
    return response.data;
  },

  updateProject: async (projectId, updates) => {
    const response = await apiClient.put(`/projects/${projectId}`, updates);
    return response.data;
  }
};

// Template API
export const templateAPI = {
  getTemplates: async () => {
    const response = await apiClient.get('/templates');
    return response.data;
  },

  getTemplate: async (templateId) => {
    const response = await apiClient.get(`/templates/${templateId}`);
    return response.data;
  }
};

// Agent API
export const agentAPI = {
  getAgents: async () => {
    const response = await apiClient.get('/agents');
    return response.data;
  },

  getModels: async () => {
    const response = await apiClient.get('/models');
    return response.data;
  }
};

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;