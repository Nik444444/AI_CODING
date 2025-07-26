# 🚀 Deployment Fix Guide

## Current Issues Fixed:

### 1. Fly.io Issue: "Could not find Dockerfile"
**Solution**: Use the root-level fly.toml that points to backend/Dockerfile

### 2. Netlify Issue: Package.json not found
**Solution**: Updated netlify.toml to use frontend as base directory

## ✅ Corrected Deployment Steps

### Backend Deployment (Fly.io)

From the **ROOT** directory of your project:

```bash
# Make sure you're in the project root (where fly.toml is located)
cd /path/to/your/emergent-clone

# Initialize and deploy
fly auth login
fly launch --no-deploy

# Optional: Add AI API keys
fly secrets set GEMINI_API_KEY="your_gemini_api_key"

# Deploy
fly deploy
```

**Key Points:**
- Run commands from project root, not from backend folder
- The fly.toml in root points to backend/Dockerfile correctly
- No database secrets needed (SQLite is self-contained)

### Frontend Deployment (Netlify)

**Option A: Git-based (Recommended)**
```bash
# Push to GitHub
git add .
git commit -m "Deploy: Emergent clone with SQLite"
git push origin main

# In Netlify Dashboard:
# 1. New site from Git → Connect your repo
# 2. Build settings:
#    - Base directory: frontend
#    - Build command: npm run build
#    - Publish directory: frontend/build
# 3. Environment variables:
#    - REACT_APP_BACKEND_URL = https://your-app-name.fly.dev
```

**Option B: Manual Deploy**
```bash
cd frontend
export REACT_APP_BACKEND_URL=https://your-app-name.fly.dev
npm run build
# Drag & drop 'build' folder to Netlify
```

## 🎯 Expected Results

After successful deployment:

1. **Backend** at `https://your-app.fly.dev`
   - Health: `https://your-app.fly.dev/api/health`
   - Docs: `https://your-app.fly.dev/docs`

2. **Frontend** at `https://your-site.netlify.app`
   - Fully functional Emergent clone
   - Connected to your backend API

## 🆘 Troubleshooting

### Fly.io Issues
- ✅ Use root directory (where fly.toml is)
- ✅ Dockerfile path is configured correctly
- ✅ No database setup required (SQLite auto-creates)

### Netlify Issues  
- ✅ Base directory set to "frontend"
- ✅ Build command: `npm run build`
- ✅ Publish directory: `frontend/build`
- ✅ Environment variable: `REACT_APP_BACKEND_URL`

### Database
- ✅ SQLite file auto-creates on first run
- ✅ No external database setup needed
- ✅ Data persists in container volume

## 🎉 Success Checklist

- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Frontend loads without errors
- [ ] Chat interface works
- [ ] All 7 AI agents respond
- [ ] Templates load correctly
- [ ] Projects can be created

Your Emergent clone is now deployed with SQLite! 🚀