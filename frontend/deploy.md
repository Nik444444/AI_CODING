# Frontend Deployment Guide - Netlify

## Prerequisites
1. GitHub account (to connect repository)
2. Netlify account: https://www.netlify.com/
3. Your backend deployed on fly.io first

## Deployment Methods

### Method 1: Git-based Deployment (Recommended)

#### 1. Push Code to GitHub
```bash
# Initialize git repository (if not already done)
cd /app
git init
git add .
git commit -m "Initial commit: Emergent Clone"

# Create repository on GitHub and push
git remote add origin https://github.com/yourusername/emergent-clone.git
git branch -M main
git push -u origin main
```

#### 2. Connect to Netlify
1. Go to https://app.netlify.com/
2. Click "New site from Git"
3. Choose GitHub and authorize
4. Select your repository
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`

#### 3. Environment Variables
In Netlify dashboard → Site settings → Environment variables:
```
REACT_APP_BACKEND_URL = https://ai-coding.fly.dev
GENERATE_SOURCEMAP = false
```

#### 4. Deploy
Click "Deploy site" - Netlify will automatically build and deploy.

### Method 2: Manual Upload

#### 1. Build Locally
```bash
cd /app/frontend

# Set production backend URL
export REACT_APP_BACKEND_URL=https://ai-coding.fly.dev

# Build the app
npm run build
```

#### 2. Deploy to Netlify
1. Go to https://app.netlify.com/
2. Drag and drop the `build` folder onto Netlify dashboard
3. Your site will be deployed instantly

## Post-Deployment Configuration

### 1. Custom Domain (Optional)
1. In Netlify dashboard → Domain settings
2. Add custom domain
3. Configure DNS settings

### 2. HTTPS
- Netlify provides automatic HTTPS
- Force HTTPS redirect is enabled by default

### 3. Form Handling (If needed later)
```html
<!-- Example for contact forms -->
<form name="contact" method="POST" data-netlify="true">
  <!-- form fields -->
</form>
```

## Important Notes

1. **Backend URL**: Make sure `REACT_APP_BACKEND_URL` points to your deployed backend on fly.io

2. **CORS**: Ensure your backend allows requests from your Netlify domain. Update `server.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-site.netlify.app"],  # Add your domain
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Build Time**: First build might take 2-3 minutes due to dependencies

4. **SPA Routing**: `_redirects` file handles React Router navigation

## Troubleshooting

### Build Errors
- Check build logs in Netlify dashboard
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

### API Connection Issues
- Verify `REACT_APP_BACKEND_URL` is correct
- Check backend is accessible from browser
- Review CORS settings in backend

### 404 Errors on Refresh
- Ensure `_redirects` file is in `public` folder
- Check netlify.toml redirect configuration

## Performance Optimization

1. **Image Optimization**: Use WebP format for images
2. **Code Splitting**: Already implemented with React lazy loading
3. **Caching**: Static assets cached for 1 year via headers
4. **Bundle Analysis**: Run `npm run build --analyze` to check bundle size

## Monitoring
- Netlify provides built-in analytics
- Monitor Core Web Vitals in deployment dashboard
- Set up uptime monitoring for your backend

## Custom Build Commands
If you need custom build process:
```toml
# netlify.toml
[build]
  command = """
    npm ci &&
    npm run build &&
    echo 'Build completed successfully'
  """
```

After successful deployment, your frontend will be available at:
`https://your-site-name.netlify.app`