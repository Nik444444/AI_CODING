import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  Users, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  Pause, 
  ArrowRight,
  RefreshCw,
  ArrowLeft
} from 'lucide-react';

const AgentCollaboration = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [collaborationStatus, setCollaborationStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    if (sessionId) {
      loadCollaborationData();
      // Set up polling for real-time updates
      const interval = setInterval(loadCollaborationData, 3000);
      return () => clearInterval(interval);
    }
  }, [sessionId]);

  const loadCollaborationData = async () => {
    try {
      setLoading(true);
      
      // Load collaboration status
      const statusResponse = await fetch(`${baseUrl}/api/collaboration/${sessionId}/status`);
      if (!statusResponse.ok) {
        throw new Error('Failed to load collaboration status');
      }
      const statusData = await statusResponse.json();
      setCollaborationStatus(statusData);

      // Load tasks
      const tasksResponse = await fetch(`${baseUrl}/api/collaboration/${sessionId}/tasks`);
      if (!tasksResponse.ok) {
        throw new Error('Failed to load tasks');
      }
      const tasksData = await tasksResponse.json();
      setTasks(tasksData.tasks || []);

      // Load agents
      const agentsResponse = await fetch(`${baseUrl}/api/collaboration/${sessionId}/agents`);
      if (!agentsResponse.ok) {
        throw new Error('Failed to load agents');
      }
      const agentsData = await agentsResponse.json();
      setAgents(agentsData.active_agents || []);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      const response = await fetch(`${baseUrl}/api/collaboration/task/${taskId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          message: `Статус обновлен на: ${newStatus}`
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update task status');
      }

      // Reload data after update
      await loadCollaborationData();
    } catch (err) {
      console.error('Error updating task:', err);
      setError(err.message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'idle': return 'bg-gray-500';
      case 'working': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'waiting': return 'bg-yellow-500';
      case 'handoff': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'idle': return <Pause className="w-4 h-4" />;
      case 'working': return <Play className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      case 'waiting': return <Clock className="w-4 h-4" />;
      case 'handoff': return <ArrowRight className="w-4 h-4" />;
      default: return <Pause className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getAgentTypeLabel = (agentType) => {
    const labels = {
      'project_planner': 'Планировщик проектов',
      'design_agent': 'Дизайнер',
      'frontend_developer': 'Frontend разработчик',
      'backend_developer': 'Backend разработчик',
      'fullstack_developer': 'Fullstack разработчик',
      'integration_agent': 'Интеграционный агент',
      'testing_expert': 'Эксперт по тестированию',
      'version_control_agent': 'Агент контроля версий',
      'deployment_engineer': 'Инженер развертывания'
    };
    return labels[agentType] || agentType;
  };

  if (loading && !collaborationStatus) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Загрузка сотрудничества агентов...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Ошибка</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => navigate('/dashboard')}>
            Вернуться на главную
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className="p-2"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold">Сотрудничество агентов</h1>
              <p className="text-gray-600">Сессия: {sessionId}</p>
            </div>
          </div>
          <Button onClick={loadCollaborationData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Обновить
          </Button>
        </div>

        {/* Collaboration Overview */}
        {collaborationStatus && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Обзор сотрудничества
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Текущая фаза</div>
                  <div className="text-lg font-semibold">{collaborationStatus.current_phase}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Активные агенты</div>
                  <div className="text-lg font-semibold">{collaborationStatus.active_agents.length}</div>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Активные задачи</div>
                  <div className="text-lg font-semibold">{collaborationStatus.active_tasks}</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Завершенные задачи</div>
                  <div className="text-lg font-semibold">{collaborationStatus.completed_tasks}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Active Agents */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Активные агенты</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <div key={agent.type} className="border rounded-lg p-4 bg-white">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{agent.name}</h3>
                    <Badge className={`${getStatusColor(agent.status)} text-white`}>
                      <span className="flex items-center">
                        {getStatusIcon(agent.status)}
                        <span className="ml-1">{agent.status}</span>
                      </span>
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{agent.description}</p>
                  <div className="text-xs text-gray-500">
                    <strong>Специализация:</strong> {agent.specialization}
                  </div>
                  {agent.typical_duration && (
                    <div className="text-xs text-gray-500 mt-1">
                      <strong>Обычная длительность:</strong> {agent.typical_duration} мин
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Current Tasks */}
        <Card>
          <CardHeader>
            <CardTitle>Текущие задачи</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {tasks.length > 0 ? (
                tasks.map((task) => (
                  <div key={task.id} className="border rounded-lg p-4 bg-white">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Badge className={`${getStatusColor(task.status)} text-white`}>
                          <span className="flex items-center">
                            {getStatusIcon(task.status)}
                            <span className="ml-1">{task.status}</span>
                          </span>
                        </Badge>
                        <Badge className={getPriorityColor(task.priority)}>
                          {task.priority}
                        </Badge>
                        <span className="text-sm text-gray-600">
                          {getAgentTypeLabel(task.agent_type)}
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        {task.status === 'idle' && (
                          <Button
                            size="sm"
                            onClick={() => updateTaskStatus(task.id, 'working')}
                          >
                            <Play className="w-4 h-4 mr-1" />
                            Начать
                          </Button>
                        )}
                        {task.status === 'working' && (
                          <Button
                            size="sm"
                            onClick={() => updateTaskStatus(task.id, 'completed')}
                            variant="outline"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Завершить
                          </Button>
                        )}
                      </div>
                    </div>
                    
                    <h3 className="font-semibold mb-2">{task.title}</h3>
                    <p className="text-gray-600 mb-3">{task.description}</p>
                    
                    {task.deliverables && task.deliverables.length > 0 && (
                      <div className="mb-3">
                        <h4 className="text-sm font-medium mb-2">Ожидаемые результаты:</h4>
                        <div className="flex flex-wrap gap-2">
                          {task.deliverables.map((deliverable, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {deliverable}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>Создано: {new Date(task.created_at).toLocaleString('ru-RU')}</span>
                      {task.handoff_to && (
                        <span className="flex items-center">
                          Передать: {getAgentTypeLabel(task.handoff_to)}
                          <ArrowRight className="w-4 h-4 ml-1" />
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Нет активных задач</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Handoffs */}
        {collaborationStatus && collaborationStatus.recent_handoffs.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Недавние передачи задач</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {collaborationStatus.recent_handoffs.map((handoff) => (
                  <div key={handoff.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                      <span className="font-medium">{getAgentTypeLabel(handoff.from_agent)}</span>
                      <span className="text-gray-500">→</span>
                      <span className="font-medium">{getAgentTypeLabel(handoff.to_agent)}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(handoff.created_at).toLocaleString('ru-RU')}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AgentCollaboration;