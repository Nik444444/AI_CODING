# Backend Deployment Guide - Fly.io

## Prerequisites
1. Install fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Create fly.io account: https://fly.io/app/sign-up
3. Login: `fly auth login`

## MongoDB Setup
You'll need a MongoDB database. Options:
1. **MongoDB Atlas** (recommended): https://www.mongodb.com/atlas
2. **Fly.io Postgres + MongoDB compatible**: https://fly.io/docs/reference/postgres/

### MongoDB Atlas Setup:
1. Create free cluster at https://cloud.mongodb.com/
2. Create database user
3. Whitelist all IPs (0.0.0.0/0) for Fly.io
4. Get connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

## Deployment Steps

### 1. Initialize Fly App
```bash
cd /app/backend
fly launch --no-deploy --copy-config
```

### 2. Set Environment Variables
```bash
# Required - MongoDB connection
fly secrets set MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/"
fly secrets set DB_NAME="emergent_clone"

# Optional - AI API Keys (for production use)
fly secrets set GEMINI_API_KEY="your_gemini_api_key"
fly secrets set OPENAI_API_KEY="your_openai_api_key"
fly secrets set ANTHROPIC_API_KEY="your_anthropic_api_key"
```

### 3. Deploy
```bash
fly deploy
```

### 4. Verify Deployment
```bash
# Check app status
fly status

# View logs
fly logs

# Open in browser
fly open /api/health
```

## Important Notes

1. **CORS Configuration**: The backend is configured to allow all origins for development. For production, update the CORS settings in `server.py` to only allow your frontend domain.

2. **AI API Keys**: Without real API keys, the app will use mock responses for demonstration. Add real keys for production use.

3. **Database**: Make sure your MongoDB instance allows connections from Fly.io IPs.

4. **Health Checks**: The app includes health checks at `/api/health`

5. **Scaling**: The current configuration uses minimal resources. Scale up as needed:
   ```bash
   fly scale memory 512
   fly scale count 2
   ```

## Troubleshooting

- **Connection Issues**: Check `fly logs` for detailed error messages
- **Database Connection**: Verify MONGO_URL is correct and accessible
- **Health Check Failures**: Ensure `/api/health` endpoint is responding
- **Memory Issues**: Scale up memory if needed: `fly scale memory 512`

## Post-Deployment
After successful deployment, your backend will be available at:
`https://ai-coding.fly.dev`

Make note of this URL - you'll need it for frontend deployment.