@echo off
REM Django Project Setup Script for Windows
REM Run this after cloning the repository to set up the development environment

echo ==================================
echo RiskPulse Django Setup Script
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
python -c "import sys; assert sys.version_info >= (3, 8), 'Python 3.8+ required'"
echo OK - Python version compatible
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo OK - Virtual environment created
) else (
    echo OK - Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo OK - Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
echo OK - pip upgraded
echo.

REM Install dependencies
echo Installing Python dependencies from requirements.txt...
pip install -r requirements.txt
echo OK - Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo WARNING - Please edit .env with your configuration
) else (
    echo OK - .env file already exists
)
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "media\reports" mkdir media\reports
if not exist "staticfiles" mkdir staticfiles
if not exist "api\ml\models" mkdir api\ml\models
echo OK - Directories created
echo.

REM Run migrations
echo Running Django migrations...
python manage.py migrate
echo OK - Migrations complete
echo.

REM Ask about creating superuser
set /p create_su="Create superuser account? (y/n): "
if /i "%create_su%"=="y" (
    python manage.py createsuperuser
)
echo.

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput
echo OK - Static files collected
echo.

echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Verify .env configuration
echo 2. Run: python manage.py runserver
echo 3. Visit: http://localhost:8000
echo 4. Admin panel: http://localhost:8000/admin
echo.
pause
