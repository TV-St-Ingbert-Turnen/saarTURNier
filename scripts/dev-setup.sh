#!/bin/bash
# Local development environment setup script

set -e

echo "=== saarTURNier Local Development Setup ==="

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

echo "✓ All prerequisites installed"

# Create .env files from templates
echo ""
echo "Creating environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
else
    echo "  backend/.env already exists"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.local.example frontend/.env.local
    echo "✓ Created frontend/.env.local"
else
    echo "  frontend/.env.local already exists"
fi

# Install backend dependencies
echo ""
echo "Setting up backend..."
cd backend
if [ ! -d venv ]; then
    python3 -m venv venv
    echo "✓ Created Python virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Backend dependencies installed"
cd ..

# Install frontend dependencies
echo ""
echo "Setting up frontend..."
cd frontend
npm ci
echo "✓ Frontend dependencies installed"
cd ..

# Start Docker services
echo ""
echo "Starting Docker services..."
docker-compose up -d
echo "✓ Docker services started"

# Run database migrations
echo ""
echo "Running database migrations..."
sleep 5  # Wait for database to be ready
cd backend
source venv/bin/activate
alembic upgrade head
echo "✓ Database migrations completed"
cd ..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up"
