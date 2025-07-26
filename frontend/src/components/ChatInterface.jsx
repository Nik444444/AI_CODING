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
import { mockData } from '../data/mockData';

const ChatInterface = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedModel, setSelectedModel] = useState('gemini-2.0-flash');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize with template or initial prompt
    const { template, initialPrompt } = location.state || {};
    
    if (template) {
      const welcomeMessage = {
        id: 1,
        type: 'assistant',
        content: `Great choice! Let's build a ${template.name}. ${template.description}\n\nI'll help you create this step by step. What specific features would you like to include?`,
        timestamp: new Date().toLocaleTimeString(),
        agent: 'Project Planner'
      };
      setMessages([welcomeMessage]);
    } else if (initialPrompt) {
      setInputValue(initialPrompt);
    } else {
      const welcomeMessage = {
        id: 1,
        type: 'assistant',
        content: `Hi! I'm your AI development assistant. I can help you build full-stack applications, analyze websites, create components, and much more.\n\nWhat would you like to build today?`,
        timestamp: new Date().toLocaleTimeString(),
        agent: 'Main Assistant'
      };
      setMessages([welcomeMessage]);
    }
  }, [location.state]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = mockData.aiResponses;
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      const assistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: randomResponse.content,
        timestamp: new Date().toLocaleTimeString(),
        agent: randomResponse.agent,
        actions: randomResponse.actions
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getAgentIcon = (agent) => {
    const icons = {
      'Main Assistant': Bot,
      'Project Planner': Brain,
      'Frontend Developer': Palette,
      'Backend Developer': Database,
      'Full-Stack Developer': Code,
      'Deployment Engineer': Globe,
      'Testing Expert': TestTube
    };
    return icons[agent] || Bot;
  };

  const getModelInfo = (model) => {
    const models = {
      'gemini-2.0-flash': { name: 'Gemini 2.0 Flash', provider: 'Google', free: true },
      'gpt-4o': { name: 'GPT-4o', provider: 'OpenAI', free: false },
      'grok-beta': { name: 'Grok Beta', provider: 'xAI', free: false }
    };
    return models[model];
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
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-48 bg-gray-900 border-gray-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-700">
                <SelectItem value="gemini-2.0-flash" className="text-white">
                  <div className="flex items-center">
                    <Sparkles className="w-4 h-4 mr-2 text-green-400" />
                    Gemini 2.0 Flash (Free)
                  </div>
                </SelectItem>
                <SelectItem value="gpt-4o" className="text-white">
                  <div className="flex items-center">
                    <Zap className="w-4 h-4 mr-2 text-blue-400" />
                    GPT-4o (Premium)
                  </div>
                </SelectItem>
                <SelectItem value="grok-beta" className="text-white">
                  <div className="flex items-center">
                    <Brain className="w-4 h-4 mr-2 text-purple-400" />
                    Grok Beta (Premium)
                  </div>
                </SelectItem>
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
            const AgentIcon = message.agent ? getAgentIcon(message.agent) : User;
            
            return (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-4xl ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`flex-shrink-0 ${message.type === 'user' ? 'ml-4' : 'mr-4'}`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      message.type === 'user' ? 'bg-cyan-600' : 'bg-gray-700'
                    }`}>
                      <AgentIcon className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  
                  <div className="flex-1">
                    <Card className={`${
                      message.type === 'user' 
                        ? 'bg-cyan-900 border-cyan-700' 
                        : 'bg-gray-900 border-gray-700'
                    }`}>
                      <CardContent className="p-4">
                        {message.agent && (
                          <div className="flex items-center mb-2">
                            <Badge variant="secondary" className="text-xs bg-gray-800 text-gray-300">
                              {message.agent}
                            </Badge>
                            <span className="text-xs text-gray-500 ml-2">{message.timestamp}</span>
                          </div>
                        )}
                        <div className="prose prose-invert max-w-none">
                          <p className="text-gray-100 whitespace-pre-wrap leading-relaxed">
                            {message.content}
                          </p>
                        </div>
                        
                        {message.actions && (
                          <div className="mt-4 flex flex-wrap gap-2">
                            {message.actions.map((action, idx) => (
                              <Button 
                                key={idx}
                                variant="outline" 
                                size="sm"
                                className="bg-gray-800 border-gray-600 hover:bg-gray-700"
                                onClick={() => setInputValue(action)}
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
              Model: <span className="text-cyan-400">{getModelInfo(selectedModel)?.name}</span>
              {getModelInfo(selectedModel)?.free && (
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