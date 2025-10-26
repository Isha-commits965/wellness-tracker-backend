#!/bin/bash

# Wellness Tracker Backend Stop Script

echo "🛑 Stopping Wellness Tracker Backend..."

# Find and kill processes running on port 8001
echo "🔍 Looking for processes on port 8001..."
PIDS=$(lsof -ti:8001 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "ℹ️  No processes found running on port 8001"
else
    echo "🔪 Killing processes: $PIDS"
    echo $PIDS | xargs kill -9 2>/dev/null
    echo "✅ Processes stopped successfully"
fi

# Also check for any uvicorn processes
echo "🔍 Looking for uvicorn processes..."
UVICORN_PIDS=$(pgrep -f "uvicorn.*wellness" 2>/dev/null)

if [ -n "$UVICORN_PIDS" ]; then
    echo "🔪 Killing uvicorn processes: $UVICORN_PIDS"
    echo $UVICORN_PIDS | xargs kill -9 2>/dev/null
    echo "✅ Uvicorn processes stopped"
fi

echo "🏁 Wellness Tracker Backend stopped"
