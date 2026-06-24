#!/bin/bash
# Django Project Setup Script
# Run this after cloning the repository to set up the development environment

set -e  # Exit on error

echo "=================================="
echo "RiskPulse Django Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version
python -c "import sys; assert sys.version_info >= (3, 8), 'Python 3.8+ required'"
echo "✓ Python version OK"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p media/reports
mkdir -p staticfiles
mkdir -p api/ml/models
echo "✓ Directories created"
echo ""

# Run migrations
echo "Running Django migrations..."
python manage.py migrate
echo "✓ Migrations complete"
echo ""

# Create superuser (optional)
read -p "Create superuser account? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Verify .env configuration"
echo "2. Run: python manage.py runserver"
echo "3. Visit: http://localhost:8000"
echo "4. Admin panel: http://localhost:8000/admin"
echo ""
