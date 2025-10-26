#!/bin/bash

# Wellness Tracker Backend Startup Script

echo "🏃‍♂️ Starting Wellness Tracker Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the application"
fi

# Initialize Alembic if not already done
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
    echo "🗄️ Initializing database migrations..."
    python setup_migrations.py
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "⚠️  Database migration failed, but continuing with startup..."
    echo "   You may need to run 'alembic upgrade head' manually"
fi

# Start the application
echo "🚀 Starting FastAPI application..."
echo "📖 API Documentation will be available at: http://localhost:8001/docs"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

python run.py
