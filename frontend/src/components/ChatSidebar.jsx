import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Clock, 
  Search,
  MoreVertical,
  Trash2,
  Edit2,
  Settings,
  User
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { chatAPI } from '../services/api';

const ChatSidebar = ({ 
  currentSessionId, 
  onSessionSelect, 
  onNewChat, 
  isOpen,
  onToggle 
}) => {
  const [sessions, setSessions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadSessions();
    }
  }, [isOpen]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const sessionsData = await chatAPI.getSessions();
      setSessions(sessionsData || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Только что';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} мин назад`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} ч назад`;
    if (diffInSeconds < 7 * 86400) return `${Math.floor(diffInSeconds / 86400)} дн назад`;
    return date.toLocaleDateString('ru-RU');
  };

  const getSessionTitle = (session) => {
    if (session.title && session.title !== 'New Chat') {
      return session.title;
    }
    return `Чат ${new Date(session.created_at).toLocaleDateString('ru-RU')}`;
  };

  const filteredSessions = sessions.filter(session =>
    getSessionTitle(session).toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupSessionsByDate = (sessions) => {
    const groups = {
      today: [],
      yesterday: [],
      week: [],
      older: []
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    sessions.forEach(session => {
      const sessionDate = new Date(session.updated_at);
      
      if (sessionDate >= today) {
        groups.today.push(session);
      } else if (sessionDate >= yesterday) {
        groups.yesterday.push(session);
      } else if (sessionDate >= weekAgo) {
        groups.week.push(session);
      } else {
        groups.older.push(session);
      }
    });

    return groups;
  };

  const sessionGroups = groupSessionsByDate(filteredSessions);

  const SessionGroup = ({ title, sessions, showDivider = true }) => {
    if (sessions.length === 0) return null;

    return (
      <>
        {showDivider && <div className="px-4 py-2">
          <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider">
            {title}
          </h3>
        </div>}
        <div className="space-y-1 px-2">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onSessionSelect(session.id)}
              className={`
                flex items-center space-x-3 px-3 py-2 rounded-lg cursor-pointer transition-colors group
                ${currentSessionId === session.id 
                  ? 'bg-cyan-900/30 border border-cyan-500/50' 
                  : 'hover:bg-gray-800/50'
                }
              `}
            >
              <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">
                  {getSessionTitle(session)}
                </p>
                <p className="text-xs text-gray-500">
                  {formatTimeAgo(session.updated_at)}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0"
              >
                <MoreVertical className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </div>
      </>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="w-80 bg-gray-950 border-r border-gray-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Чаты</h2>
          <Button
            onClick={onNewChat}
            size="sm"
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Новый чат
          </Button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Поиск чатов..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-gray-900 border-gray-700 text-white"
          />
        </div>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <MessageSquare className="w-12 h-12 text-gray-600 mb-4" />
            <p className="text-gray-400 mb-2">
              {searchTerm ? 'Чаты не найдены' : 'Нет чатов'}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              {searchTerm ? 'Попробуйте другой поисковый запрос' : 'Начните новый разговор'}
            </p>
            {!searchTerm && (
              <Button onClick={onNewChat} size="sm" variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                Создать чат
              </Button>
            )}
          </div>
        ) : (
          <div className="py-4">
            <SessionGroup title="Сегодня" sessions={sessionGroups.today} showDivider={false} />
            <SessionGroup title="Вчера" sessions={sessionGroups.yesterday} />
            <SessionGroup title="На этой неделе" sessions={sessionGroups.week} />
            <SessionGroup title="Старые" sessions={sessionGroups.older} />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center space-x-3 text-sm text-gray-400">
          <User className="w-4 h-4" />
          <span>Разработчик</span>
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;