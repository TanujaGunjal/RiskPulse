#!/bin/bash
# Quick start script for seed_db command
# Usage: bash run_seed_db.sh [options]

echo "Healthcare Fraud Detection - Database Seeding Script"
echo "====================================================="
echo ""

# Check if Django project is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if Django is available
if ! python -c "import django" 2>/dev/null; then
    echo "Error: Django is not installed"
    echo "Install with: pip install django"
    exit 1
fi

# Check if pandas is available
if ! python -c "import pandas" 2>/dev/null; then
    echo "Error: pandas is not installed"
    echo "Install with: pip install pandas"
    exit 1
fi

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found"
    echo "Run this script from your Django project root directory"
    exit 1
fi

echo "✓ All dependencies available"
echo ""

# Parse command line arguments
CSV_PATH="hcfd_xai_final_results.csv"
CLEAR_FLAG=""
LIMIT_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --csv-path)
            CSV_PATH="$2"
            shift 2
            ;;
        --clear)
            CLEAR_FLAG="--clear"
            shift
            ;;
        --limit)
            LIMIT_FLAG="--limit $2"
            shift 2
            ;;
        --help)
            echo "Usage: bash run_seed_db.sh [options]"
            echo ""
            echo "Options:"
            echo "  --csv-path PATH    Path to CSV file (default: hcfd_xai_final_results.csv)"
            echo "  --clear            Clear existing data before loading"
            echo "  --limit N          Load only first N rows"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  bash run_seed_db.sh"
            echo "  bash run_seed_db.sh --csv-path data/results.csv"
            echo "  bash run_seed_db.sh --csv-path data/results.csv --clear"
            echo "  bash run_seed_db.sh --limit 1000"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Verify CSV file exists
if [ ! -f "$CSV_PATH" ]; then
    echo "Error: CSV file not found: $CSV_PATH"
    exit 1
fi

echo "CSV file: $CSV_PATH"
echo "File size: $(du -h "$CSV_PATH" | cut -f1)"
echo "Row count: $(tail -n +2 "$CSV_PATH" | wc -l)"
echo ""

# Run the seed command
echo "Starting database seeding..."
echo ""

python manage.py seed_db --csv-path "$CSV_PATH" $CLEAR_FLAG $LIMIT_FLAG

# Capture exit code
EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Database seeding completed successfully"
    
    # Run verification
    echo ""
    echo "Running verification..."
    echo ""
    python manage.py shell < api/management/commands/verify_seed.py
else
    echo "✗ Database seeding failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
