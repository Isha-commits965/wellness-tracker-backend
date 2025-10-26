# 🚀 Deploy Wellness Tracker Backend to Render

This guide will help you deploy the FastAPI backend to Render so it can work with your frontend.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your code to GitHub
3. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com)

## 🔧 Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: FastAPI wellness tracker backend"

# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/wellness-tracker-backend.git

# Push to GitHub
git push -u origin main
```

### 2. Create Render Web Service

1. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub Repository**:
   - Select your `wellness-tracker-backend` repository
   - Choose the main branch

### 3. Configure Service Settings

**Basic Settings:**
- **Name**: `wellness-tracker-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
- **Start Command**: `python start_production.py`
- **Health Check Path**: `/health`

### 4. Set Environment Variables

In the Render dashboard, go to **Environment** tab and add:

```
DATABASE_URL=postgresql://username:password@hostname:port/database
SECRET_KEY=your-super-secret-jwt-key-here
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
DEBUG=False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Wellness Tracker API
```

**Important Notes:**
- **DATABASE_URL**: Render will provide this when you create a PostgreSQL database
- **SECRET_KEY**: Generate a strong random string (32+ characters)
- **OPENAI_API_KEY**: Your actual OpenAI API key

### 5. Create PostgreSQL Database

1. **Go to Render Dashboard** → **"New +"** → **"PostgreSQL"**
2. **Configure Database**:
   - **Name**: `wellness-tracker-db`
   - **Database**: `wellness_tracker`
   - **User**: `wellness_user`
   - **Region**: Same as your web service
3. **Copy the connection string** and use it as `DATABASE_URL`

### 6. Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Check logs** for any errors

## 🔗 Frontend Integration

Once deployed, your backend will be available at:
```
https://wellness-tracker-backend.onrender.com
```

### Update Frontend API Base URL

In your frontend code, change the API base URL from:
```javascript
// Local development
const API_BASE_URL = 'http://localhost:8001';

// Production
const API_BASE_URL = 'https://wellness-tracker-backend.onrender.com';
```

### CORS Configuration

The backend is already configured to allow CORS from any origin. If you need to restrict it:

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl https://wellness-tracker-backend.onrender.com/health
```

### 2. API Documentation
Visit: `https://wellness-tracker-backend.onrender.com/docs`

### 3. Test Registration
```bash
curl -X POST "https://wellness-tracker-backend.onrender.com/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123", "full_name": "Test User"}'
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check `requirements.txt` for all dependencies
   - Ensure Python version compatibility

2. **Database Connection Error**:
   - Verify `DATABASE_URL` is correct
   - Check if PostgreSQL service is running

3. **OpenAI API Error**:
   - Verify `OPENAI_API_KEY` is set correctly
   - Check API key has sufficient credits

4. **CORS Issues**:
   - Update CORS origins in `app/main.py`
   - Ensure frontend URL is whitelisted

### View Logs:
1. Go to your service in Render dashboard
2. Click on "Logs" tab
3. Check for error messages

## 📊 Monitoring

- **Uptime**: Render provides basic uptime monitoring
- **Logs**: Available in the dashboard
- **Metrics**: Basic performance metrics included

## 🔄 Updates

To update your deployment:
1. Push changes to GitHub
2. Render will automatically redeploy
3. Check logs for any issues

## 💰 Cost Considerations

- **Free Tier**: 750 hours/month (enough for small projects)
- **Paid Plans**: Start at $7/month for always-on service
- **Database**: PostgreSQL starts at $7/month

## 🎯 Next Steps

1. **Deploy your frontend** to Vercel, Netlify, or similar
2. **Update frontend API URLs** to point to Render
3. **Test the complete flow** end-to-end
4. **Set up monitoring** and alerts
5. **Configure custom domain** (optional)

## 📞 Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **GitHub Issues**: Create an issue in your repository

---

**🎉 Congratulations!** Your wellness tracker backend is now live and ready to serve your frontend!