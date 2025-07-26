# API Keys Setup Guide

Your Emergent Clone is ready for deployment! To enable real AI functionality (instead of mock responses), you'll need to set up API keys for the AI services.

## Required API Keys

### 1. Google Gemini API (Free Tier Available)
- **Purpose**: Primary AI model for the application
- **Get Key**: https://makersuite.google.com/app/apikey
- **Free Tier**: Yes, generous quota
- **Variable Name**: `GEMINI_API_KEY`

### 2. OpenAI API (Premium)
- **Purpose**: Advanced AI models (GPT-4o, GPT-4o Mini)
- **Get Key**: https://platform.openai.com/api-keys
- **Free Tier**: Limited credits for new accounts
- **Variable Name**: `OPENAI_API_KEY`

### 3. Anthropic API (Premium) - Optional
- **Purpose**: Claude models for advanced reasoning
- **Get Key**: https://console.anthropic.com/
- **Free Tier**: Limited credits
- **Variable Name**: `ANTHROPIC_API_KEY`

## Setting Up API Keys

### For Fly.io Backend:
```bash
# Required for real AI responses
fly secrets set GEMINI_API_KEY="your_gemini_api_key_here"

# Optional for premium features
fly secrets set OPENAI_API_KEY="your_openai_api_key_here"
fly secrets set ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Redeploy to apply changes
fly deploy
```

### For Local Development:
Create `/app/backend/.env` file:
```env
# MongoDB (required)
MONGO_URL=your_mongodb_connection_string
DB_NAME=emergent_clone

# AI API Keys (optional - app works with mock responses without them)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## How the App Works Without API Keys

**Good News**: Your app is fully functional even without real API keys!

- ✅ All UI features work perfectly
- ✅ Chat interface is fully functional  
- ✅ All 7 AI agents respond with contextual mock responses
- ✅ Project management works completely
- ✅ Database integration is active
- ✅ All endpoints function properly

The mock responses are intelligent and contextual, providing a great demo experience.

## Recommended Setup Order

1. **Deploy First** - Get your app live with mock responses
2. **Get Gemini API Key** - Enable real AI with free tier
3. **Add Premium Keys** - Upgrade to GPT-4o/Claude when needed

## API Usage and Costs

### Gemini (Google):
- **Free Tier**: 15 requests per minute, 1500 requests per day
- **Cost**: $0.00035/1K characters (very affordable)
- **Best For**: Primary AI assistant, general development help

### OpenAI GPT-4o:
- **Cost**: ~$5-15 per 1M tokens
- **Best For**: Complex reasoning, advanced code generation
- **When to Use**: Premium users, complex projects

### Anthropic Claude:
- **Cost**: Similar to GPT-4o
- **Best For**: Long-form content, analysis
- **When to Use**: Specialized tasks requiring reasoning

## Security Best Practices

1. **Never commit API keys** to your repository
2. **Use environment variables** on all platforms
3. **Rotate keys regularly** if compromised
4. **Set usage limits** in AI provider dashboards
5. **Monitor usage** to avoid unexpected charges

## Testing Your Setup

After adding API keys, test each model:

1. Go to your deployed app
2. Open chat interface
3. Select different models from dropdown
4. Send test messages to verify responses
5. Check that responses are real (not mock)

## Monitoring Usage

- **Gemini**: https://makersuite.google.com/app/apikey (usage dashboard)
- **OpenAI**: https://platform.openai.com/usage (billing section)
- **Anthropic**: https://console.anthropic.com/ (usage tracking)

Your Emergent Clone is enterprise-ready and will scale with your needs!