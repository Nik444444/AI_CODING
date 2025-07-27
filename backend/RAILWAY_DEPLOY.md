# Backend Deployment на Railway

## Быстрый деплой

1. **Зайди на Railway.app**
2. **Подключи GitHub репозиторий** 
3. **Выбери папку `backend`** как root directory
4. **Railway автоматически определит Python и запустит деплой**

## Переменные окружения (опционально)

В Railway dashboard добавь переменные:

```
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here  
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## URL после деплоя

Railway даст тебе URL типа: `https://your-app-name.up.railway.app`

Этот URL нужно будет добавить в CORS настройки и в frontend `.env`:

```
REACT_APP_BACKEND_URL=https://your-app-name.up.railway.app
```

## API endpoints

- Health: `https://your-app-name.up.railway.app/api/health`
- Docs: `https://your-app-name.up.railway.app/docs`
- Chat: `https://your-app-name.up.railway.app/api/chat/send`

## База данных

SQLite файл создается автоматически. Данные сохраняются между деплоями.

## Логи

В Railway dashboard можно смотреть логи в реальном времени.