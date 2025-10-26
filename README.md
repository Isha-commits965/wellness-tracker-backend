# 🌟 Wellness Tracker Backend API

A comprehensive FastAPI backend for a wellness tracking application that helps users build better daily habits, track moods, and maintain an AI-powered journal for personal growth and mental wellness.

## 🎯 About the App

The Wellness Tracker is designed to help people build consistent daily habits and improve their mental well-being through:

- **🏃‍♂️ Habit Tracking**: Create, manage, and track personal habits with streak monitoring
- **😊 Mood Tracking**: Daily mood scoring with energy and stress level monitoring  
- **📝 AI-Powered Journal**: Write daily entries and receive empathetic AI responses
- **📊 Analytics & Insights**: Comprehensive dashboard with trends and progress visualization
- **🎯 Goal Management**: Set and track personal wellness goals
- **📅 Calendar View**: Visual progress tracking with completion rates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd wellness-tracker-backend
```

### 2. Start the Application
```bash
# One-command setup and start
./start.sh
```

### 3. Access the API
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Main Endpoint**: http://localhost:8001/

### 4. Stop the Application
```bash
./stop.sh
```

## ⚙️ Environment Setup

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///./wellness_tracker.db

# JWT Authentication (REQUIRED - Generate a secure key)
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI API (OPTIONAL - For AI journal features)
OPENAI_API_KEY=your-openai-api-key-here

# App Settings
APP_NAME=Wellness Tracker API
DEBUG=True
```

### Generate a Secure Secret Key
```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### OpenAI API Key (Optional)
- Get your API key from [OpenAI Platform](https://platform.openai.com/)
- Add it to your `.env` file
- Without it, journal features will show fallback responses

## 🏗️ What the start.sh Script Does

The `start.sh` script automatically handles:

1. **Virtual Environment**: Creates and activates `venv/`
2. **Dependencies**: Installs all required packages
3. **Environment Setup**: Creates `.env` from template if missing
4. **Database Migrations**: Runs Alembic migrations automatically
5. **Application Start**: Launches the FastAPI server on port 8001

## 📚 API Features

### 🔐 Authentication
- User registration and login
- JWT token-based authentication
- Secure password hashing

### 🏃‍♂️ Habit Management
- Create and manage personal habits
- Daily habit check-ins with notes
- Streak tracking and analytics
- Habit categories and frequency settings

### 😊 Mood Tracking
- Daily mood scoring (1-10 scale)
- Energy and stress level tracking
- Mood trends and weekly statistics
- Historical mood analysis

### 📝 AI-Powered Journal
- Write daily journal entries
- AI-generated empathetic responses
- Mood improvement tracking
- Contextual suggestions and support

### 📊 Analytics & Insights
- Comprehensive dashboard data
- Weekly and monthly statistics
- Calendar view with progress visualization
- Habit completion rates and streaks

### 🎯 Goal Management
- Set and track personal goals
- Goal completion tracking
- Due date management
- Progress overview

## 🛠️ Development

### Manual Setup (Alternative to start.sh)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start the application
python run.py
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "Your migration message"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Habits
- `POST /habits/` - Create a new habit
- `GET /habits/` - Get all user habits
- `POST /habits/check-ins/` - Create habit check-in
- `GET /habits/streaks/` - Get habit streaks

### Moods
- `POST /moods/` - Create mood entry
- `GET /moods/trends/` - Get mood trends
- `GET /moods/stats/weekly` - Get weekly mood stats

### Journal
- `POST /journal/` - Create journal entry with AI response
- `GET /journal/` - Get journal entries
- `POST /journal/{entry_id}/regenerate-ai` - Regenerate AI response

### Analytics
- `GET /analytics/dashboard` - Get comprehensive dashboard data
- `GET /analytics/calendar/{year}/{month}` - Get calendar data
- `GET /analytics/weekly-stats` - Get weekly statistics

### Goals
- `POST /goals/` - Create a new goal
- `GET /goals/` - Get all goals
- `POST /goals/{goal_id}/complete` - Mark goal as completed

## 🔧 Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Database (development)
- **PostgreSQL** - Database (production ready)
- **JWT** - Authentication and authorization
- **OpenAI API** - AI-powered journal responses
- **Pydantic** - Data validation and serialization
- **Alembic** - Database migrations

## 🚀 Production Deployment

### Environment Variables for Production
```env
# Database
DATABASE_URL=postgresql://username:password@localhost/wellness_tracker

# Security
SECRET_KEY=your-very-secure-secret-key
DEBUG=False

# OpenAI
OPENAI_API_KEY=your-openai-api-key
```

### Security Considerations
- Use strong, unique secret keys
- Set up proper CORS origins
- Use HTTPS in production
- Implement rate limiting
- Set up proper logging and monitoring

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository.

---

**Happy Wellness Tracking! 🌟**