#!/bin/bash

echo "🍽️ FoodVision AI - Starting Application"
echo "====================================="

echo ""
echo "🐍 Starting Backend Server..."
cd "$(dirname "$0")"
source venv/bin/activate
python backend/app_simple.py &
BACKEND_PID=$!

echo ""
echo "⚛️ Starting Frontend Server..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "🌐 Application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "📋 Press Ctrl+C to stop both servers"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait