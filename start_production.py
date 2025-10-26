#!/usr/bin/env python3
"""
Production startup script for Wellness Tracker Backend
"""
import os
import subprocess
import sys
from app.config import settings

def run_migrations():
    """Run database migrations"""
    try:
        print("🔄 Running database migrations...")
        result = subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        print("✅ Database migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def start_server():
    """Start the production server"""
    print("🚀 Starting production server...")
    
    # Use gunicorn for production
    cmd = [
        "gunicorn",
        "app.main:app",
        "-w", "4",  # Number of workers
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", "0.0.0.0:8000",
        "--timeout", "120",
        "--keep-alive", "2",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "--preload"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🏃‍♂️ Starting Wellness Tracker Backend (Production)")
    print(f"📊 Database: {settings.database_url}")
    print(f"🔧 Debug Mode: {settings.debug}")
    print(f"🤖 OpenAI API: {'Configured' if settings.openai_api_key else 'Not configured'}")
    
    # Run migrations first
    if not run_migrations():
        print("⚠️  Continuing without successful migration...")
    
    # Start the server
    start_server()
