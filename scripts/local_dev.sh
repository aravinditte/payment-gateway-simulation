#!/bin/bash
# Local development setup script

set -e

echo "🚀 Payment Gateway Simulator - Local Development Setup"
echo "========================================================"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "\n📝 Creating .env file..."
    cp .env.example .env
    echo "✓ .env created. Please update with your configuration."
fi

# Create virtual environment
if [ ! -d venv ]; then
    echo "\n📦 Creating virtual environment..."
    python3.11 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created."
else
    source venv/bin/activate
    echo "✓ Virtual environment activated."
fi

# Install dependencies
echo "\n📚 Installing dependencies..."
pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"
echo "✓ Dependencies installed."

# Start Docker services
echo "\n🐳 Starting Docker services..."
docker-compose up -d postgres redis
echo "✓ Docker services started."

# Wait for services to be ready
echo "\n⏳ Waiting for services to be ready..."
sleep 5

# Run migrations
echo "\n🗄️  Running database migrations..."
alembic upgrade head
echo "✓ Database migrations completed."

# Seed data
echo "\n🌱 Seeding demo data..."
python -m app.scripts.seed_data
echo "✓ Demo data seeded."

echo "\n✅ Setup complete! Start the server with:\n"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📊 ReDoc: http://localhost:8000/redoc"
echo ""
