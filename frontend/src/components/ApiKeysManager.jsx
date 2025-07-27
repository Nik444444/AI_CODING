import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { 
  ArrowLeft, 
  Plus, 
  Key, 
  Eye, 
  EyeOff, 
  Trash2, 
  Edit, 
  Check,
  X,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { apiKeysAPI } from '../services/api';
import URLDebugger from './URLDebugger';

const ApiKeysManager = () => {
  const navigate = useNavigate();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingKey, setEditingKey] = useState(null);
  const [formData, setFormData] = useState({
    provider: '',
    api_key: '',
    display_name: ''
  });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const providers = [
    { id: 'gemini', name: 'Google Gemini', icon: '🤖', description: 'Бесплатный AI сервис от Google' },
    { id: 'openai', name: 'OpenAI', icon: '🚀', description: 'GPT-4o и GPT-4o Mini модели' },
    { id: 'anthropic', name: 'Anthropic', icon: '🎯', description: 'Claude AI модели' }
  ];

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const data = await apiKeysAPI.getAPIKeys();
      setApiKeys(data);
    } catch (error) {
      console.error('Ошибка загрузки API ключей:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.provider) {
      newErrors.provider = 'Выберите провайдера';
    }
    
    if (!formData.api_key.trim()) {
      newErrors.api_key = 'Введите API ключ';
    } else if (formData.api_key.trim().length < 10) {
      newErrors.api_key = 'API ключ слишком короткий';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      setSaving(true);
      
      if (editingKey) {
        await apiKeysAPI.updateAPIKey(editingKey.id, {
          api_key: formData.api_key,
          display_name: formData.display_name || null
        });
      } else {
        await apiKeysAPI.createAPIKey(
          formData.provider,
          formData.api_key,
          formData.display_name || null
        );
      }
      
      await loadApiKeys();
      resetForm();
    } catch (error) {
      console.error('Ошибка сохранения API ключа:', error);
      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      } else {
        setErrors({ general: 'Произошла ошибка при сохранении ключа' });
      }
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (apiKey) => {
    setEditingKey(apiKey);
    setFormData({
      provider: apiKey.provider,
      api_key: '',
      display_name: apiKey.display_name || ''
    });
    setShowAddForm(true);
    setErrors({});
  };

  const handleDelete = async (apiKey) => {
    if (!window.confirm(`Вы уверены, что хотите удалить ключ для ${getProviderName(apiKey.provider)}?`)) {
      return;
    }

    try {
      await apiKeysAPI.deleteAPIKey(apiKey.id);
      await loadApiKeys();
    } catch (error) {
      console.error('Ошибка удаления API ключа:', error);
    }
  };

  const resetForm = () => {
    setFormData({ provider: '', api_key: '', display_name: '' });
    setShowAddForm(false);
    setEditingKey(null);
    setErrors({});
  };

  const getProviderName = (providerId) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.name : providerId;
  };

  const getProviderIcon = (providerId) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.icon : '🔑';
  };

  const getProviderDescription = (providerId) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.description : '';
  };

  const hasProviderKey = (providerId) => {
    return apiKeys.some(key => key.provider === providerId && key.is_active);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/')}
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center">
                <Key className="h-8 w-8 mr-3 text-blue-500" />
                Управление API Ключами
              </h1>
              <p className="text-gray-400 mt-2">
                Добавьте свои API ключи для доступа к различным LLM провайдерам
              </p>
            </div>
          </div>
          
          {!showAddForm && (
            <Button 
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Добавить ключ
            </Button>
          )}
        </div>

        {/* Add/Edit Form */}
        {showAddForm && (
          <Card className="bg-gray-800 border-gray-700 mb-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Key className="h-5 w-5 mr-2" />
                {editingKey ? 'Редактировать API ключ' : 'Добавить новый API ключ'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {errors.general && (
                  <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 flex items-center">
                    <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0" />
                    <span className="text-red-300">{errors.general}</span>
                  </div>
                )}

                {/* Provider Selection */}
                {!editingKey && (
                  <div className="space-y-3">
                    <Label className="text-gray-300">Провайдер</Label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {providers.map((provider) => (
                        <div
                          key={provider.id}
                          className={`p-4 rounded-lg border cursor-pointer transition-all ${
                            formData.provider === provider.id
                              ? 'border-blue-500 bg-blue-900/20'
                              : hasProviderKey(provider.id)
                              ? 'border-gray-600 bg-gray-800/50 opacity-50 cursor-not-allowed'
                              : 'border-gray-600 bg-gray-800/30 hover:border-gray-500'
                          }`}
                          onClick={() => {
                            if (!hasProviderKey(provider.id)) {
                              setFormData({ ...formData, provider: provider.id });
                              setErrors({ ...errors, provider: null });
                            }
                          }}
                        >
                          <div className="text-center">
                            <div className="text-2xl mb-2">{provider.icon}</div>
                            <div className="font-semibold text-white">{provider.name}</div>
                            <div className="text-sm text-gray-400">{provider.description}</div>
                            {hasProviderKey(provider.id) && (
                              <Badge className="mt-2 bg-green-600">Уже добавлен</Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                    {errors.provider && (
                      <span className="text-red-400 text-sm">{errors.provider}</span>
                    )}
                  </div>
                )}

                {/* API Key Input */}
                <div className="space-y-2">
                  <Label className="text-gray-300">
                    API Ключ {editingKey && <span className="text-gray-500">(оставьте пустым, если не хотите менять)</span>}
                  </Label>
                  <Input
                    type="password"
                    value={formData.api_key}
                    onChange={(e) => {
                      setFormData({ ...formData, api_key: e.target.value });
                      setErrors({ ...errors, api_key: null });
                    }}
                    placeholder="Введите ваш API ключ"
                    className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                  />
                  {errors.api_key && (
                    <span className="text-red-400 text-sm">{errors.api_key}</span>
                  )}
                </div>

                {/* Display Name */}
                <div className="space-y-2">
                  <Label className="text-gray-300">Название (необязательно)</Label>
                  <Input
                    type="text"
                    value={formData.display_name}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    placeholder="Например: Мой Gemini ключ"
                    className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end space-x-3">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={resetForm}
                    disabled={saving}
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Отмена
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={saving}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {saving ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    ) : (
                      <Check className="h-4 w-4 mr-2" />
                    )}
                    {editingKey ? 'Обновить' : 'Сохранить'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* API Keys List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold text-white">Ваши API ключи</h2>
          
          {apiKeys.length === 0 ? (
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-8 text-center">
                <Key className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Нет сохраненных ключей</h3>
                <p className="text-gray-400 mb-4">
                  Добавьте свои API ключи для начала работы с различными LLM провайдерами
                </p>
                <Button 
                  onClick={() => setShowAddForm(true)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Добавить первый ключ
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {apiKeys.map((apiKey) => (
                <Card key={apiKey.id} className="bg-gray-800 border-gray-700">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl">{getProviderIcon(apiKey.provider)}</div>
                        <div>
                          <h3 className="font-semibold text-white">
                            {apiKey.display_name || getProviderName(apiKey.provider)}
                          </h3>
                          <p className="text-sm text-gray-400">{getProviderName(apiKey.provider)}</p>
                        </div>
                      </div>
                      <Badge 
                        className={apiKey.is_active ? 'bg-green-600' : 'bg-gray-600'}
                      >
                        {apiKey.is_active ? 'Активен' : 'Неактивен'}
                      </Badge>
                    </div>

                    <div className="mb-4">
                      <Label className="text-gray-400 text-sm">API Ключ</Label>
                      <div className="text-white font-mono text-sm bg-gray-700 p-2 rounded mt-1">
                        {apiKey.api_key}
                      </div>
                    </div>

                    <div className="text-xs text-gray-500 mb-4">
                      Создан: {new Date(apiKey.created_at).toLocaleDateString('ru-RU')}
                    </div>

                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(apiKey)}
                        className="border-gray-600 text-gray-300 hover:bg-gray-700 flex-1"
                      >
                        <Edit className="h-3 w-3 mr-1" />
                        Изменить
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(apiKey)}
                        className="border-red-600 text-red-400 hover:bg-red-900/20"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Provider Status */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-white mb-4">Статус провайдеров</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {providers.map((provider) => {
              const hasKey = hasProviderKey(provider.id);
              return (
                <div
                  key={provider.id}
                  className={`p-4 rounded-lg border ${
                    hasKey 
                      ? 'border-green-600 bg-green-900/20' 
                      : 'border-gray-600 bg-gray-800/30'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="text-xl">{provider.icon}</div>
                      <div>
                        <div className="font-semibold text-white">{provider.name}</div>
                        <div className="text-sm text-gray-400">{provider.description}</div>
                      </div>
                    </div>
                    <div>
                      {hasKey ? (
                        <Badge className="bg-green-600">
                          <Check className="h-3 w-3 mr-1" />
                          Настроен
                        </Badge>
                      ) : (
                        <Badge className="bg-gray-600">
                          Не настроен
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiKeysManager;