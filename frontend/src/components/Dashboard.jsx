import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  Sparkles, 
  Music, 
  CheckSquare, 
  PenTool, 
  Wand2,
  Github,
  Settings,
  RefreshCw,
  Globe,
  MessageSquare,
  Monitor
} from 'lucide-react';
import { templateAPI, projectAPI } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [userPrompt, setUserPrompt] = useState('');
  const [templates, setTemplates] = useState([]);
  const [recentTasks, setRecentTasks] = useState([]);
  const [deployedApps, setDeployedApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load templates
      const templatesData = await templateAPI.getTemplates();
      setTemplates(templatesData);
      
      // Load projects
      const projectsData = await projectAPI.getProjects();
      
      // Separate into recent tasks and deployed apps
      const tasks = projectsData.filter(p => p.status !== 'deployed');
      const deployed = projectsData.filter(p => p.status === 'deployed');
      
      setRecentTasks(tasks.slice(0, 4)); // Show latest 4
      setDeployedApps(deployed.slice(0, 3)); // Show latest 3
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Fallback to empty arrays on error
      setTemplates([]);
      setRecentTasks([]);
      setDeployedApps([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStartChat = () => {
    if (userPrompt.trim()) {
      navigate('/chat', { state: { initialPrompt: userPrompt } });
    } else {
      navigate('/chat');
    }
  };

  const handleTemplateClick = (template) => {
    navigate('/chat', { state: { template } });
  };

  const handleProjectClick = (project) => {
    navigate(`/project/${project.id}`);
  };

  const getIconComponent = (iconName) => {
    const icons = {
      Music,
      CheckSquare,
      PenTool,
      Wand2
    };
    return icons[iconName] || Monitor;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge className="text-xs bg-green-900 text-green-300">Completed</Badge>;
      case 'building':
        return <Badge className="text-xs bg-blue-900 text-blue-300">Building</Badge>;
      case 'deployed':
        return <Badge className="text-xs bg-green-900 text-green-300">Live</Badge>;
      default:
        return <Badge className="text-xs bg-yellow-900 text-yellow-300">In Progress</Badge>;
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return `${Math.floor(diffInSeconds / 86400)} days ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center">
              <Monitor className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold">Home</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
              <Github className="w-4 h-4 mr-2" />
              Connect GitHub
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/collaboration/demo-session')}
              className="text-gray-400 hover:text-white"
              title="Сотрудничество агентов"
            >
              <Users className="w-5 h-5" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/api-keys')}
              className="text-gray-400 hover:text-white"
              title="Управление API ключами"
            >
              <Settings className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <div className="mb-6">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-300 mb-4">
              Welcome, Developer
            </h1>
            <h2 className="text-3xl md:text-4xl font-bold text-cyan-400 mb-8">
              What will you build today?
            </h2>
          </div>

          {/* Free AI Notice */}
          <div className="mb-8">
            <div className="inline-flex items-center space-x-4 bg-gray-900 rounded-full px-6 py-3 border border-gray-700">
              <div className="flex items-center space-x-2 text-green-400">
                <Sparkles className="w-4 h-4" />
                <span className="font-medium">Free Gemini AI</span>
              </div>
              <span className="text-gray-400">•</span>
              <span className="text-gray-300 text-sm">
                Unlimited usage with community models
              </span>
            </div>
          </div>

          {/* Main Prompt Input */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="relative">
              <textarea
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                placeholder="проанализируй сайт https://app.emergent.sh/ ,сделай идентичный полностью по функционалу ,ботам и прочим алгоритмам приложение..."
                className="w-full h-32 bg-gray-900 border border-gray-700 rounded-xl px-4 py-4 text-white placeholder-gray-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 resize-none"
              />
              <div className="absolute bottom-4 right-4 flex items-center space-x-3">
                <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                  <MessageSquare className="w-4 h-4" />
                </Button>
                <Button 
                  onClick={handleStartChat}
                  className="bg-white text-black hover:bg-gray-200 rounded-full px-6"
                >
                  <span className="mr-2">→</span>
                  Start Building
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* App Templates */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">Quick Start Templates</h3>
            <RefreshCw 
              className="w-5 h-5 text-gray-400 cursor-pointer hover:text-white" 
              onClick={loadData}
            />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {templates.map((template) => {
              const IconComponent = getIconComponent(template.icon);

              return (
                <Card 
                  key={template.id}
                  className="bg-gray-900 border-gray-700 hover:border-gray-600 cursor-pointer transition-all duration-200 hover:transform hover:scale-105"
                  onClick={() => handleTemplateClick(template)}
                >
                  <CardContent className="p-6 text-center">
                    <div className={`w-12 h-12 ${template.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{template.name}</h4>
                    <p className="text-sm text-gray-400">{template.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Tasks */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold flex items-center">
                <div className="w-5 h-5 bg-gray-700 rounded mr-3"></div>
                Recent Tasks
              </h3>
              <RefreshCw 
                className="w-5 h-5 text-gray-400 cursor-pointer hover:text-white"
                onClick={loadData}
              />
            </div>
            
            <div className="space-y-3">
              {recentTasks.length > 0 ? recentTasks.map((task) => (
                <Card 
                  key={task.id}
                  className="bg-gray-900 border-gray-700 hover:border-gray-600 cursor-pointer transition-colors"
                  onClick={() => handleProjectClick(task)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h5 className="font-medium text-white mb-1">{task.name}</h5>
                        <p className="text-sm text-gray-400 mb-2">{task.description}</p>
                        <div className="flex items-center space-x-2">
                          {getStatusBadge(task.status)}
                          <span className="text-xs text-gray-500">{formatTimeAgo(task.updated_at)}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No recent tasks found</p>
                  <p className="text-sm">Start building something amazing!</p>
                </div>
              )}
            </div>
          </div>

          {/* Deployed Apps */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold flex items-center">
                <Globe className="w-5 h-5 mr-3" />
                Deployed Apps
              </h3>
              <RefreshCw 
                className="w-5 h-5 text-gray-400 cursor-pointer hover:text-white"
                onClick={loadData}
              />
            </div>
            
            <div className="space-y-3">
              {deployedApps.length > 0 ? deployedApps.map((app) => (
                <Card 
                  key={app.id}
                  className="bg-gray-900 border-gray-700 hover:border-gray-600 cursor-pointer transition-colors"
                  onClick={() => window.open(app.deployment_url, '_blank')}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h5 className="font-medium text-white mb-1">{app.name}</h5>
                        <p className="text-sm text-gray-400 mb-2">{app.description}</p>
                        <div className="flex items-center space-x-2">
                          <Badge className="text-xs bg-green-900 text-green-300">
                            Live
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {app.deployment_url?.replace('https://', '')}
                          </span>
                        </div>
                      </div>
                      <Globe className="w-5 h-5 text-gray-400" />
                    </div>
                  </CardContent>
                </Card>
              )) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No deployed apps yet</p>
                  <p className="text-sm">Deploy your first project!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;