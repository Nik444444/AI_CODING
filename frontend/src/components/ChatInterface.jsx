import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Send, 
  ArrowLeft, 
  Bot, 
  User, 
  Settings, 
  Zap,
  Brain,
  Sparkles,
  Code,
  Palette,
  Database,
  Globe,
  TestTube
} from 'lucide-react';
import { chatAPI, agentAPI } from '../services/api';

const ChatInterface = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedModel, setSelectedModel] = useState('gemini-2.0-flash');
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [availableModels, setAvailableModels] = useState([]);
  const [availableAgents, setAvailableAgents] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadInitialData();
    initializeChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadInitialData = async () => {
    try {
      // Load available models and agents
      const [modelsData, agentsData] = await Promise.all([
        agentAPI.getModels(),
        agentAPI.getAgents()
      ]);
      
      setAvailableModels(modelsData);
      setAvailableAgents(agentsData);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const initializeChat = () => {
    const { template, initialPrompt } = location.state || {};
    
    if (template) {
      const welcomeMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `Great choice! Let's build a ${template.name}. ${template.description}\n\nI'll help you create this step by step. What specific features would you like to include?`,
        timestamp: new Date().toLocaleTimeString(),
        agent_type: 'project_planner',
        suggested_actions: [
          "Show me the tech stack",
          "Create project structure",
          "Start with frontend",
          "Plan the database"
        ]
      };
      setMessages([welcomeMessage]);
      setSelectedAgent('project_planner');
    } else if (initialPrompt) {
      setInputValue(initialPrompt);
    } else {
      const welcomeMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `Hi! I'm your AI development assistant. I can help you build full-stack applications, analyze websites, create components, and much more.\n\nWhat would you like to build today?`,
        timestamp: new Date().toLocaleTimeString(),
        agent_type: 'main_assistant'
      };
      setMessages([welcomeMessage]);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(
        sessionId,
        messageToSend,
        selectedAgent,
        selectedProvider,
        selectedModel
      );

      // Set session ID if it's new
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const assistantMessage = {
        id: response.message.id,
        role: 'assistant',
        content: response.message.content,
        timestamp: new Date(response.message.timestamp).toLocaleTimeString(),
        agent_type: response.message.agent_type,
        suggested_actions: response.suggested_actions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update selected agent if it changed
      if (response.message.agent_type && response.message.agent_type !== selectedAgent) {
        setSelectedAgent(response.message.agent_type);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Show error message
      const errorMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toLocaleTimeString(),
        agent_type: 'main_assistant'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedAction = (action) => {
    setInputValue(action);
  };

  const handleModelChange = (value) => {
    const [provider, model] = value.split('/');
    setSelectedProvider(provider);
    setSelectedModel(model);
  };

  const getAgentIcon = (agentType) => {
    const icons = {
      'main_assistant': Bot,
      'project_planner': Brain,
      'frontend_developer': Palette,
      'backend_developer': Database,
      'fullstack_developer': Code,
      'deployment_engineer': Globe,
      'testing_expert': TestTube
    };
    return icons[agentType] || Bot;
  };

  const getAgentName = (agentType) => {
    const agent = availableAgents.find(a => a.type === agentType);
    return agent ? agent.name : 'AI Assistant';
  };

  const getModelDisplayName = (provider, model) => {
    const modelInfo = availableModels.find(m => m.provider === provider && m.name === model);
    return modelInfo ? modelInfo.display_name : `${provider}/${model}`;
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 p-4 flex-shrink-0">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => navigate('/')}
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <h1 className="text-lg font-semibold">AI Development Chat</h1>
          </div>

          <div className="flex items-center space-x-4">
            <Select value={`${selectedProvider}/${selectedModel}`} onValueChange={handleModelChange}>
              <SelectTrigger className="w-48 bg-gray-900 border-gray-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-700">
                {availableModels.map((model) => (
                  <SelectItem 
                    key={`${model.provider}/${model.name}`} 
                    value={`${model.provider}/${model.name}`}
                    className="text-white"
                  >
                    <div className="flex items-center">
                      {model.provider === 'gemini' && <Sparkles className="w-4 h-4 mr-2 text-green-400" />}
                      {model.provider === 'openai' && <Zap className="w-4 h-4 mr-2 text-blue-400" />}
                      {model.provider === 'anthropic' && <Brain className="w-4 h-4 mr-2 text-purple-400" />}
                      <span>{model.display_name}</span>
                      {model.is_free && (
                        <Badge variant="secondary" className="ml-2 text-xs bg-green-900 text-green-300">
                          Free
                        </Badge>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Settings className="w-5 h-5 text-gray-400 cursor-pointer hover:text-white" />
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {messages.map((message) => {
            const AgentIcon = message.agent_type ? getAgentIcon(message.agent_type) : User;
            
            return (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-4xl ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`flex-shrink-0 ${message.role === 'user' ? 'ml-4' : 'mr-4'}`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      message.role === 'user' ? 'bg-cyan-600' : 'bg-gray-700'
                    }`}>
                      <AgentIcon className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  
                  <div className="flex-1">
                    <Card className={`${
                      message.role === 'user' 
                        ? 'bg-cyan-900 border-cyan-700' 
                        : 'bg-gray-900 border-gray-700'
                    }`}>
                      <CardContent className="p-4">
                        {message.agent_type && message.role === 'assistant' && (
                          <div className="flex items-center mb-2">
                            <Badge variant="secondary" className="text-xs bg-gray-800 text-gray-300">
                              {getAgentName(message.agent_type)}
                            </Badge>
                            <span className="text-xs text-gray-500 ml-2">{message.timestamp}</span>
                          </div>
                        )}
                        <div className="prose prose-invert max-w-none">
                          <p className="text-gray-100 whitespace-pre-wrap leading-relaxed">
                            {message.content}
                          </p>
                        </div>
                        
                        {message.suggested_actions && message.suggested_actions.length > 0 && (
                          <div className="mt-4 flex flex-wrap gap-2">
                            {message.suggested_actions.map((action, idx) => (
                              <Button 
                                key={idx}
                                variant="outline" 
                                size="sm"
                                className="bg-gray-800 border-gray-600 hover:bg-gray-700"
                                onClick={() => handleSuggestedAction(action)}
                              >
                                {action}
                              </Button>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            );
          })}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex max-w-4xl">
                <div className="flex-shrink-0 mr-4">
                  <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white animate-pulse" />
                  </div>
                </div>
                <Card className="bg-gray-900 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                      <span className="text-gray-400 text-sm">AI is thinking...</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 p-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe what you want to build or ask a question..."
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 resize-none"
                rows="3"
              />
            </div>
            <Button 
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <div>
              Model: <span className="text-cyan-400">{getModelDisplayName(selectedProvider, selectedModel)}</span>
              {availableModels.find(m => m.provider === selectedProvider && m.name === selectedModel)?.is_free && (
                <Badge variant="secondary" className="ml-2 text-xs bg-green-900 text-green-300">
                  Free
                </Badge>
              )}
            </div>
            <div>Press Enter to send, Shift+Enter for new line</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;