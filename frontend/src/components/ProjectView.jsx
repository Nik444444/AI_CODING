import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { 
  ArrowLeft, 
  Play, 
  Code, 
  Globe, 
  Download, 
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  Eye
} from 'lucide-react';
import { mockData } from '../data/mockData';

const ProjectView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Find project in mock data
    const foundProject = mockData.recentTasks.find(task => task.id === id) ||
                         mockData.deployedApps.find(app => app.id === id);
    
    if (foundProject) {
      setProject(foundProject);
      // Simulate build logs
      setLogs([
        { time: '10:30:15', level: 'info', message: 'Starting project build...' },
        { time: '10:30:16', level: 'info', message: 'Installing dependencies...' },
        { time: '10:30:45', level: 'success', message: 'Dependencies installed successfully' },
        { time: '10:31:02', level: 'info', message: 'Running frontend build...' },
        { time: '10:31:30', level: 'info', message: 'Running backend setup...' },
        { time: '10:31:45', level: 'success', message: 'Build completed successfully!' },
        { time: '10:31:46', level: 'info', message: 'Deploying to production...' },
        { time: '10:32:00', level: 'success', message: 'Deployment successful!' }
      ]);
    }
  }, [id]);

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-400 mb-4">Project Not Found</h2>
          <Button onClick={() => navigate('/')} className="bg-cyan-600 hover:bg-cyan-700">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-900 text-green-300';
      case 'building': return 'bg-blue-900 text-blue-300'; 
      case 'live': return 'bg-green-900 text-green-300';
      default: return 'bg-yellow-900 text-yellow-300';
    }
  };

  const getLogIcon = (level) => {
    switch (level) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />;
      default: return <Clock className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 p-4">
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
            <div>
              <h1 className="text-xl font-bold">{project.name}</h1>
              <p className="text-sm text-gray-400">{project.description}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Badge className={getStatusColor(project.status)}>
              {project.status === 'live' ? 'Live' : 
               project.status === 'completed' ? 'Completed' :
               project.status === 'building' ? 'Building' : 'In Progress'}
            </Badge>
            {project.url && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.open(project.url, '_blank')}
                className="border-gray-600 hover:bg-gray-800"
              >
                <Eye className="w-4 h-4 mr-2" />
                View Live
              </Button>
            )}
            <Settings className="w-5 h-5 text-gray-400 cursor-pointer hover:text-white" />
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Project Overview */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Code className="w-5 h-5 mr-2" />
                  Project Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Created</h4>
                    <p className="text-white">{project.timestamp}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Status</h4>
                    <Badge className={getStatusColor(project.status)}>
                      {project.status === 'live' ? 'Live' : 
                       project.status === 'completed' ? 'Completed' :
                       project.status === 'building' ? 'Building' : 'In Progress'}
                    </Badge>
                  </div>
                </div>
                
                {project.progress !== undefined && (
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Progress</span>
                      <span className="text-white">{project.progress}%</span>
                    </div>
                    <Progress value={project.progress} className="w-full" />
                  </div>
                )}

                {project.url && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Live URL</h4>
                    <div className="flex items-center space-x-2">
                      <Globe className="w-4 h-4 text-cyan-400" />
                      <a 
                        href={project.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 underline"
                      >
                        {project.domain || project.url}
                      </a>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Build Logs */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>Build Logs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-950 rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
                  {logs.map((log, index) => (
                    <div key={index} className="flex items-start space-x-3 mb-2">
                      <span className="text-gray-500 text-xs">{log.time}</span>
                      {getLogIcon(log.level)}
                      <span className={`flex-1 ${
                        log.level === 'success' ? 'text-green-400' :
                        log.level === 'error' ? 'text-red-400' : 'text-gray-300'
                      }`}>
                        {log.message}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-cyan-600 hover:bg-cyan-700" size="sm">
                  <Play className="w-4 h-4 mr-2" />
                  Redeploy
                </Button>
                <Button variant="outline" className="w-full border-gray-600 hover:bg-gray-800" size="sm">
                  <Code className="w-4 h-4 mr-2" />
                  View Code
                </Button>
                <Button variant="outline" className="w-full border-gray-600 hover:bg-gray-800" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </CardContent>
            </Card>

            {/* Tech Stack */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>Tech Stack</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Badge variant="secondary" className="mr-2 mb-2">React</Badge>
                  <Badge variant="secondary" className="mr-2 mb-2">FastAPI</Badge>
                  <Badge variant="secondary" className="mr-2 mb-2">MongoDB</Badge>
                  <Badge variant="secondary" className="mr-2 mb-2">Tailwind CSS</Badge>
                  <Badge variant="secondary" className="mr-2 mb-2">Gemini AI</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Statistics */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Build Time</span>
                  <span className="text-white">1m 45s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Bundle Size</span>
                  <span className="text-white">2.3 MB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Uptime</span>
                  <span className="text-green-400">99.9%</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectView;