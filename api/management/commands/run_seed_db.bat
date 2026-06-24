@echo off
REM Quick start script for seed_db command (Windows)
REM Usage: run_seed_db.bat [options]

setlocal enabledelayedexpansion

echo Healthcare Fraud Detection - Database Seeding Script (Windows)
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check if manage.py exists
if not exist "manage.py" (
    echo Error: manage.py not found
    echo Run this script from your Django project root directory
    exit /b 1
)

echo.
echo Testing dependencies...

REM Check Django
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo Error: Django is not installed
    echo Install with: pip install django
    exit /b 1
)

REM Check pandas
python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo Error: pandas is not installed
    echo Install with: pip install pandas
    exit /b 1
)

echo OK - All dependencies available
echo.

REM Set defaults
set "CSV_PATH=hcfd_xai_final_results.csv"
set "CLEAR_FLAG="
set "LIMIT_FLAG="

REM Parse arguments
:parse_args
if "%~1"=="" goto run_seed
if "%~1"=="--csv-path" (
    set "CSV_PATH=%~2"
    shift
    shift
    goto parse_args
)
if "%~1"=="--clear" (
    set "CLEAR_FLAG=--clear"
    shift
    goto parse_args
)
if "%~1"=="--limit" (
    set "LIMIT_FLAG=--limit %~2"
    shift
    shift
    goto parse_args
)
if "%~1"=="--help" (
    echo Usage: run_seed_db.bat [options]
    echo.
    echo Options:
    echo   --csv-path PATH    Path to CSV file (default: hcfd_xai_final_results.csv)
    echo   --clear            Clear existing data before loading
    echo   --limit N          Load only first N rows
    echo   --help             Show this help message
    echo.
    echo Examples:
    echo   run_seed_db.bat
    echo   run_seed_db.bat --csv-path data\results.csv
    echo   run_seed_db.bat --csv-path data\results.csv --clear
    echo   run_seed_db.bat --limit 1000
    exit /b 0
)

:run_seed
REM Verify CSV file exists
if not exist "%CSV_PATH%" (
    echo Error: CSV file not found: %CSV_PATH%
    exit /b 1
)

echo CSV file: %CSV_PATH%
echo.
echo Starting database seeding...
echo.

REM Run the seed command
python manage.py seed_db --csv-path %CSV_PATH% %CLEAR_FLAG% %LIMIT_FLAG%

REM Capture exit code
set EXIT_CODE=%errorlevel%

echo.

if %EXIT_CODE% equ 0 (
    echo OK - Database seeding completed successfully
    echo.
    echo Running verification...
    echo.
    python manage.py shell < api\management\commands\verify_seed.py
) else (
    echo Error - Database seeding failed with exit code %EXIT_CODE%
    exit /b %EXIT_CODE%
)

endlocal
