#!/usr/bin/env python3
"""
Setup script for database migrations
This script initializes Alembic and creates the initial migration
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🗄️ Setting up database migrations...")
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if alembic is already initialized
    if os.path.exists("alembic/versions") and os.listdir("alembic/versions"):
        print("✅ Alembic is already initialized")
        return
    
    # Initialize Alembic
    if not run_command("alembic init alembic", "Initializing Alembic"):
        sys.exit(1)
    
    # Create initial migration
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        print("⚠️  Migration creation failed, but Alembic is initialized")
        print("   You can create migrations manually with: alembic revision --autogenerate -m 'Your message'")
    
    print("✅ Database migration setup completed!")
    print("📝 To create new migrations: alembic revision --autogenerate -m 'Your message'")
    print("📝 To apply migrations: alembic upgrade head")

if __name__ == "__main__":
    main()
