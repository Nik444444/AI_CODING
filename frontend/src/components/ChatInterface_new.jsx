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
  TestTube,
  Menu,
  X,
  Upload,
  Paperclip,
  Image as ImageIcon,
  FileText,
  Download
} from 'lucide-react';
import { chatAPI, agentAPI } from '../services/api';
import MessageFormatter from './MessageFormatter';
import TypingIndicator from './TypingIndicator';
import ChatSidebar from './ChatSidebar';
import FilePreview from './FilePreview';

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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

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
        content: `🎯 **Отличный выбор!** Давайте создадим ${template.name}.

${template.description}

Я помогу вам создать это приложение пошагово. Вот что мы можем включить:

${template.features ? template.features.map(f => `• ${f}`).join('\n') : ''}

**Технологический стек:**
${template.tech_stack ? template.tech_stack.map(t => `• ${t}`).join('\n') : ''}

Какие конкретные функции вы хотели бы добавить или с чего начнем?`,
        timestamp: new Date().toLocaleTimeString(),
        agent_type: 'project_planner',
        suggested_actions: [
          "Показать техническое задание",
          "Создать структуру проекта", 
          "Начать с frontend",
          "Спланировать базу данных"
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
        content: `👋 **Привет! Я ваш AI-ассистент разработчика.**

Я помогу вам:
• 🏗️ **Создавать приложения** - от идеи до деплоя
• 🔍 **Анализировать веб-сайты** - понимать структуру и функциональность  
• 💻 **Писать код** - на любых языках и фреймворках
• 🎨 **Проектировать интерфейсы** - современные и удобные
• 🚀 **Оптимизировать проекты** - производительность и качество

**Что бы вы хотели создать или изучить сегодня?**`,
        timestamp: new Date().toLocaleTimeString(),
        agent_type: 'main_assistant',
        suggested_actions: [
          "Создать новое приложение",
          "Проанализировать веб-сайт", 
          "Помочь с кодом",
          "Показать возможности"
        ]
      };
      setMessages([welcomeMessage]);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if ((!inputValue.trim() && uploadedFiles.length === 0) || isLoading) return;

    let messageContent = inputValue.trim();
    
    // Add file information to message if files are uploaded
    if (uploadedFiles.length > 0) {
      const fileInfo = uploadedFiles.map(file => 
        `📎 **Файл:** ${file.name} (${file.type}, ${(file.size / 1024).toFixed(1)} KB)`
      ).join('\n');
      messageContent = messageContent ? `${messageContent}\n\n${fileInfo}` : fileInfo;
    }

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date().toLocaleTimeString(),
      files: uploadedFiles.length > 0 ? uploadedFiles : undefined
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue('');
    setUploadedFiles([]);
    setIsLoading(true);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

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
        suggested_actions: response.suggested_actions || [],
        metadata: response.message.metadata || {},
        created_files: response.message.metadata?.created_files || []
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
        content: `❌ **Извините, произошла ошибка при обработке вашего сообщения.**

${error.message || 'Неизвестная ошибка'}

Пожалуйста, попробуйте снова или обратитесь к поддержке.`,
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
    // Auto focus textarea
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleModelChange = (value) => {
    const [provider, model] = value.split('/');
    setSelectedProvider(provider);
    setSelectedModel(model);
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const validFiles = files.filter(file => {
      // Allow text files, images, and code files
      const allowedTypes = [
        'text/', 'image/', 'application/json', 'application/javascript',
        '.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.css', '.md', '.txt'
      ];
      
      return allowedTypes.some(type => 
        file.type.startsWith(type) || file.name.toLowerCase().endsWith(type)
      );
    });

    if (validFiles.length !== files.length) {
      alert('Некоторые файлы не поддерживаются. Разрешены: текстовые файлы, изображения, код.');
    }

    setUploadedFiles(prev => [...prev, ...validFiles]);
  };

  const removeUploadedFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setInputValue('');
    setUploadedFiles([]);
    setSidebarOpen(false);
    initializeChat();
  };

  const handleSessionSelect = (newSessionId) => {
    // Load messages for selected session
    setSessionId(newSessionId);
    setSidebarOpen(false);
    // TODO: Implement loading messages from selected session
  };

  // Auto-resize textarea
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    
    // Auto-resize
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
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
    return agent ? agent.name : 'AI Ассистент';
  };

  const getModelDisplayName = (provider, model) => {
    const modelInfo = availableModels.find(m => m.provider === provider && m.name === model);
    return modelInfo ? modelInfo.display_name : `${provider}/${model}`;
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex">
      {/* Sidebar */}
      <ChatSidebar 
        currentSessionId={sessionId}
        onSessionSelect={handleSessionSelect}
        onNewChat={handleNewChat}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-gray-800 p-4 flex-shrink-0 bg-gray-950/80 backdrop-blur supports-[backdrop-filter]:bg-gray-950/60">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-400 hover:text-white lg:hidden"
              >
                <Menu className="w-4 h-4" />
              </Button>
              
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/')}
                className="text-gray-400 hover:text-white hidden lg:flex"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                На главную
              </Button>
              
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-400 hover:text-white hidden lg:flex"
              >
                <Menu className="w-4 h-4 mr-2" />
                Чаты
              </Button>
              
              <Separator orientation="vertical" className="h-6" />
              
              <h1 className="text-lg font-semibold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                AI Ассистент
              </h1>
              
              {selectedAgent && (
                <>
                  <Separator orientation="vertical" className="h-6" />
                  <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
                    {getAgentName(selectedAgent)}
                  </Badge>
                </>
              )}
            </div>

            <div className="flex items-center space-x-4">
              <Select value={`${selectedProvider}/${selectedModel}`} onValueChange={handleModelChange}>
                <SelectTrigger className="w-48 bg-gray-900 border-gray-700 hover:border-gray-600 transition-colors">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-gray-900 border-gray-700">
                  {availableModels.map((model) => (
                    <SelectItem 
                      key={`${model.provider}/${model.name}`} 
                      value={`${model.provider}/${model.name}`}
                      className="text-white hover:bg-gray-800 focus:bg-gray-800"
                    >
                      <div className="flex items-center">
                        {model.provider === 'gemini' && <Sparkles className="w-4 h-4 mr-2 text-green-400" />}
                        {model.provider === 'openai' && <Zap className="w-4 h-4 mr-2 text-blue-400" />}
                        {model.provider === 'anthropic' && <Brain className="w-4 h-4 mr-2 text-purple-400" />}
                        <span>{model.display_name}</span>
                        {model.is_free && (
                          <Badge variant="secondary" className="ml-2 text-xs bg-green-900 text-green-300">
                            Бесплатно
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/api-keys')}
                className="text-gray-400 hover:text-white"
                title="Настройки API ключей"
              >
                <Settings className="w-5 h-5" />
              </Button>
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
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
                        message.role === 'user' 
                          ? 'bg-gradient-to-br from-cyan-500 to-blue-600' 
                          : 'bg-gradient-to-br from-gray-600 to-gray-700'
                      }`}>
                        <AgentIcon className="w-5 h-5 text-white" />
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <Card className={`shadow-lg transition-all duration-200 hover:shadow-xl ${
                        message.role === 'user' 
                          ? 'bg-gradient-to-br from-cyan-900/50 to-blue-900/30 border-cyan-700/50' 
                          : 'bg-gray-900/80 border-gray-700/50 backdrop-blur supports-[backdrop-filter]:bg-gray-900/60'
                      }`}>
                        <CardContent className="p-6">
                          {message.agent_type && message.role === 'assistant' && (
                            <div className="flex items-center justify-between mb-4">
                              <Badge variant="outline" className="border-cyan-500/30 text-cyan-400 bg-cyan-500/10">
                                {getAgentName(message.agent_type)}
                              </Badge>
                              <span className="text-xs text-gray-500">{message.timestamp}</span>
                            </div>
                          )}
                          
                          <MessageFormatter content={message.content} />
                          
                          {/* File Preview */}
                          {message.created_files && message.created_files.length > 0 && (
                            <div className="mt-6">
                              <FilePreview files={message.created_files} />
                            </div>
                          )}
                          
                          {message.suggested_actions && message.suggested_actions.length > 0 && (
                            <div className="mt-6 flex flex-wrap gap-2">
                              {message.suggested_actions.map((action, idx) => (
                                <Button 
                                  key={idx}
                                  variant="outline" 
                                  size="sm"
                                  className="bg-gray-800/50 border-gray-600 hover:bg-gray-700 hover:border-gray-500 transition-all duration-200"
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
              <TypingIndicator agentName={getAgentName(selectedAgent)} />
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 p-4 flex-shrink-0 bg-gray-950/80 backdrop-blur supports-[backdrop-filter]:bg-gray-950/60">
          <div className="max-w-4xl mx-auto">
            {/* Uploaded Files Preview */}
            {uploadedFiles.length > 0 && (
              <div className="mb-4 p-3 bg-gray-900/50 rounded-lg border border-gray-700">
                <div className="flex flex-wrap gap-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center space-x-2 bg-gray-800 rounded px-3 py-1">
                      <FileText className="w-4 h-4 text-cyan-400" />
                      <span className="text-sm text-gray-300">{file.name}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeUploadedFile(index)}
                        className="h-5 w-5 p-0 hover:bg-red-600/20"
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder="Расскажите, что хотите создать или спросите что-то..."
                    className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 pr-12 text-white placeholder-gray-500 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 resize-none transition-all duration-200 min-h-[52px] max-h-[200px]"
                    rows="1"
                    disabled={isLoading}
                  />
                  
                  {/* File Upload Button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute right-2 bottom-2 h-8 w-8 p-0 hover:bg-gray-700"
                    disabled={isLoading}
                    title="Прикрепить файл"
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    className="hidden"
                    onChange={handleFileUpload}
                    accept=".txt,.md,.js,.jsx,.ts,.tsx,.py,.html,.css,.json,image/*"
                  />
                </div>
              </div>
              
              <Button 
                onClick={handleSendMessage}
                disabled={isLoading || (!inputValue.trim() && uploadedFiles.length === 0)}
                className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white px-6 py-3 rounded-xl shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                size="lg"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            
            <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                <span>
                  Модель: <span className="text-cyan-400 font-medium">{getModelDisplayName(selectedProvider, selectedModel)}</span>
                  {availableModels.find(m => m.provider === selectedProvider && m.name === selectedModel)?.is_free && (
                    <Badge variant="secondary" className="ml-2 text-xs bg-green-900 text-green-300">
                      Бесплатно
                    </Badge>
                  )}
                </span>
              </div>
              <div>Enter для отправки, Shift+Enter для новой строки</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;