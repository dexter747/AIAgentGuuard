#!/bin/bash

# AgentGuard Development Environment Startup Script

echo "🚀 Starting AgentGuard Development Environment..."
echo ""

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL, Redis)..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d postgres redis
else
    docker compose up -d postgres redis
fi

# Wait for services to be healthy
echo "⏳ Waiting for database and cache to be ready..."
sleep 5

# Check if backend .env exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env from example..."
    cp backend/.env.example backend/.env
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed. Please install pnpm"
    exit 1
fi

# Install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start all services
echo ""
echo "✅ Starting services..."
echo ""
echo "📱 Frontend (Web): http://localhost:3000"
echo "🔧 Frontend (Admin): http://localhost:3001"
echo "� Documentation: http://localhost:3002"
echo "🔌 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""

# Run frontend services with pnpm
pnpm --parallel dev &
FRONTEND_PID=$!

# Wait a bit for frontends to start
sleep 3

# Run backend service
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

echo ""
echo "🎉 All services started!"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    echo "🐳 Stopping Docker services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    echo "✅ All services stopped"
    exit
}

trap cleanup INT

# Wait for processes
wait
