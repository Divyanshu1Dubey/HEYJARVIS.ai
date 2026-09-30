#!/bin/bash
set -e

echo "========================================"
echo "  HeyJarvis Development Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.11+ required"
    exit 1
fi

echo "[1/4] Installing Python dependencies..."
pip install -e ".[dev]"

echo ""
echo "[2/4] Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

echo ""
echo "[3/4] Waiting for services to be ready..."
sleep 5

echo ""
echo "[4/4] Initializing database..."
python -c "from shared.database import init_db, seed_demo_data; init_db(); seed_demo_data(); print('Database ready!')"

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Start the API:"
echo "  uvicorn apps.api.main:app --reload"
echo ""
echo "Start the worker:"
echo "  celery -A apps.worker worker --loglevel=info -B"
echo ""
echo "API docs:"
echo "  http://localhost:8000/docs"
echo ""
echo "Demo login:"
echo "  Email: admin@brightsmile.example.com"
echo "  Any password"
echo ""
