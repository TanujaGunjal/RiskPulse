"""
seed_db Django Management Command
==================================

A comprehensive Django management command for seeding the healthcare fraud
detection database from CSV files.

QUICK START
-----------

1. Install dependencies:
   pip install pandas

2. Run with default settings:
   python manage.py seed_db

3. Run with custom CSV file:
   python manage.py seed_db --csv-path /path/to/hcfd_xai_final_results.csv

4. Clear and reload data:
   python manage.py seed_db --csv-path data.csv --clear

5. Load sample data (15 test records):
   python manage.py seed_db --csv-path api/management/commands/sample_data.csv

FEATURES
--------

✓ Reads CSV files using pandas
✓ Creates Transaction objects with all fields
✓ Automatically creates Alert objects for critical risk (final_risk > 0.75)
✓ Progress reporting every 1000 rows
✓ Idempotent - skips existing records to avoid duplicates
✓ Comprehensive error handling and reporting
✓ Database transaction atomicity
✓ Summary statistics at completion

REQUIREMENTS
------------

- Django (any recent version)
- pandas >= 0.23.0
- Python 3.6+
- Existing Transaction and Alert models in api/models.py

CSV FILE FORMAT
---------------

Required columns (case-sensitive):
- caseid: Unique case identifier
- age: Patient age
- wealth_idx: Wealth index (0-5)
- education: Education level
- residence: Residence type
- has_diabetes: Boolean
- has_htn: Boolean  
- DVS: Demographic Variability Score
- TNS: Testing/Screening Score
- ICS: Income/Wealth Score
- CCS: Consistency Check Score
- HCFD_score: Healthcare Fraud Detection Score
- rule_score: Rule-based fraud score
- anomaly_score: ML anomaly score
- final_risk: Final fraud risk score
- risk_tier: Risk tier (low/medium/high/critical)
- explanation: Risk assessment explanation

See sample_data.csv for example format.

COMMAND OPTIONS
---------------

--csv-path PATH
    Path to CSV file to load
    Default: hcfd_xai_final_results.csv
    
    Examples:
    --csv-path /home/user/data/results.csv
    --csv-path data/hcfd_xai_final_results.csv

--clear
    Clear all existing transactions and alerts before loading
    ⚠️  Use with caution in production!
    
    Example:
    python manage.py seed_db --csv-path data.csv --clear

--limit N
    Load only first N rows from CSV (useful for testing)
    
    Example:
    python manage.py seed_db --limit 100

USAGE EXAMPLES
--------------

Example 1: Load default file
    python manage.py seed_db

Example 2: Load from specific location
    python manage.py seed_db --csv-path /home/data/fraud_results.csv

Example 3: Load sample data (15 test records)
    python manage.py seed_db --csv-path api/management/commands/sample_data.csv

Example 4: Test with first 100 rows
    python manage.py seed_db --csv-path data.csv --limit 100

Example 5: Replace all data
    python manage.py seed_db --csv-path data.csv --clear

Example 6: Clear then load sample
    python manage.py seed_db \\
        --csv-path api/management/commands/sample_data.csv \\
        --clear

BEHAVIOR
--------

1. Idempotent Loading
   - Checks if caseid already exists before creating
   - Skips existing transactions automatically
   - Safe to run multiple times

2. Alert Creation
   - Creates Alert for each transaction with final_risk > 0.75
   - Alert status set to is_resolved=False
   - Includes risk_tier and final_risk in alert

3. Error Handling
   - Continues processing on row errors
   - Reports error with row number and caseid
   - Returns exit code 1 if any errors occur

4. Progress Reporting
   - Shows progress every 1000 rows
   - Displays: row count, created, skipped, alerts counts
   - Final summary with detailed statistics

SAMPLE OUTPUT
-------------

Reading CSV file: data/hcfd_xai_final_results.csv
CSV has 50000 rows

Progress: 1000/50000 (Created: 987, Skipped: 13, Alerts: 234)
Progress: 2000/50000 (Created: 1974, Skipped: 26, Alerts: 468)
...
Progress: 50000/50000 (Created: 49500, Skipped: 500, Alerts: 5200)

======================================================================
DATABASE SEEDING COMPLETE
======================================================================
Total rows in CSV:            50000
Transactions created:         49500
Transactions skipped:            500
Alerts created:               5200
======================================================================
Successfully loaded 49500 transactions and created 5200 alerts.

VERIFICATION
------------

After seeding, verify data was loaded correctly:

1. Using the verification script:
   python manage.py shell < api/management/commands/verify_seed.py

2. Using Django shell:
   python manage.py shell
   >>> from models import Transaction, Alert
   >>> Transaction.objects.count()
   49500
   >>> Alert.objects.count()
   5200

3. Check specific transactions:
   >>> Transaction.objects.filter(caseid='CASE001')
   >>> Alert.objects.filter(transaction__caseid='CASE001')

PERFORMANCE
-----------

For large CSV files:

Small files (< 1,000 rows):
- Usually completes in seconds
- No special optimization needed

Medium files (1,000 - 100,000 rows):
- Completes in minutes
- Consider using --limit for testing first

Large files (> 100,000 rows):
- May take 10+ minutes
- Monitor progress with output
- Consider splitting CSV and loading in batches

Performance tips:
- Use local database for faster operations
- Close unnecessary database connections
- Run on database server or same network
- Consider bulk_create() for even faster loading

DATABASE BACKUP
---------------

Before loading large datasets, backup your database:

SQLite:
    cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

PostgreSQL:
    pg_dump dbname > backup_$(date +%Y%m%d_%H%M%S).sql

MySQL:
    mysqldump -u user -p dbname > backup_$(date +%Y%m%d_%H%M%S).sql

Restore if needed:
    python manage.py loaddata backup.json
    # or restore from database backup

TROUBLESHOOTING
---------------

Problem: "CSV file not found"
Solution:
  1. Check file path is correct
  2. Use absolute path or path relative to project root
  3. Example: --csv-path /home/user/data/results.csv

Problem: "CSV missing required columns"
Solution:
  1. Verify all required columns present in CSV
  2. Check column names match exactly (case-sensitive)
  3. Ensure CSV header row exists

Problem: "Error processing row X"
Solution:
  1. Check data types in that row
  2. Ensure age is integer, risk scores are float
  3. Check for NULL or invalid values
  4. Test with --limit to isolate problem rows

Problem: "No new transactions were loaded"
Solution:
  1. Check if caseid values already in database
  2. Use --clear flag to remove old data
  3. Verify CSV file is not empty

Problem: Out of Memory
Solution:
  1. Use --limit to load in batches
  2. Split large CSV files
  3. Increase available memory to Python

Problem: Database locked (SQLite)
Solution:
  1. Close other Django processes
  2. Check no other connections to database
  3. Use --clear to recreate fresh database

ADVANCED USAGE
--------------

Load and verify in one command:
    python manage.py seed_db --csv-path data.csv && \\
    python manage.py shell < verify_seed.py

Backup, clear, and load:
    python manage.py dumpdata > backup.json && \\
    python manage.py seed_db --csv-path data.csv --clear

Load multiple files sequentially:
    python manage.py seed_db --csv-path data1.csv
    python manage.py seed_db --csv-path data2.csv
    # (Idempotent - won't duplicate data)

HELPER SCRIPTS
--------------

Bash script (Linux/Mac):
    bash api/management/commands/run_seed_db.sh --csv-path data.csv

Batch script (Windows):
    run_seed_db.bat --csv-path data.csv

Python verification:
    python manage.py shell < api/management/commands/verify_seed.py

DEVELOPMENT & TESTING
---------------------

Test with sample data (15 records):
    python manage.py seed_db \\
        --csv-path api/management/commands/sample_data.csv \\
        --clear

Debug single row:
    # Add print statements in seed_db.py _seed_transactions()
    # Use --limit 1 to process only first row
    python manage.py seed_db --csv-path data.csv --limit 1

Generate test data:
    python manage.py shell
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({
    ...     'caseid': [f'TEST{i:03d}' for i in range(100)],
    ...     'age': np.random.randint(20, 80, 100),
    ...     # ... other fields ...
    ... })
    >>> df.to_csv('test_data.csv', index=False)

DATABASE SCHEMA
---------------

Assumes these models exist in api/models.py:

Transaction:
    - caseid (CharField, unique)
    - age (IntegerField)
    - wealth_idx (FloatField)
    - education (CharField)
    - residence (CharField)
    - has_diabetes (BooleanField)
    - has_htn (BooleanField)
    - DVS (FloatField)
    - TNS (FloatField)
    - ICS (FloatField)
    - CCS (FloatField)
    - HCFD_score (FloatField)
    - rule_score (FloatField)
    - anomaly_score (FloatField)
    - final_risk (FloatField)
    - risk_tier (CharField)
    - explanation (TextField)
    - created_at (DateTimeField, auto_now_add)

Alert:
    - transaction (ForeignKey to Transaction)
    - risk_tier (CharField)
    - final_risk (FloatField)
    - message (TextField)
    - is_resolved (BooleanField, default False)
    - created_at (DateTimeField, auto_now_add)

REQUIREMENTS FILE
-----------------

Add to requirements.txt:
    pandas>=0.23.0
    Django>=2.2

Install with:
    pip install -r requirements.txt

SUPPORT & DOCUMENTATION
-----------------------

For more detailed information, see:
- SEED_DB_GUIDE.md - Complete documentation
- sample_data.csv - Example CSV format
- verify_seed.py - Database verification script
- run_seed_db.sh - Bash helper script (Linux/Mac)
- run_seed_db.bat - Batch helper script (Windows)

Django management command docs:
https://docs.djangoproject.com/en/stable/howto/custom-management-commands/

Pandas documentation:
https://pandas.pydata.org/docs/

COMMON WORKFLOWS
----------------

Workflow: Development/Testing
    python manage.py seed_db \\
        --csv-path api/management/commands/sample_data.csv \\
        --clear

Workflow: Add data to existing database
    python manage.py seed_db --csv-path data.csv

Workflow: Incremental loading
    python manage.py seed_db --csv-path batch1.csv
    python manage.py seed_db --csv-path batch2.csv

Workflow: Production deployment
    # Backup first
    python manage.py dumpdata > backup.json
    
    # Load data
    python manage.py seed_db --csv-path data.csv --clear
    
    # Verify
    python manage.py shell < verify_seed.py

Workflow: Large file processing
    # Split CSV
    split -l 50000 large.csv chunk_
    
    # Load chunks
    python manage.py seed_db --csv-path chunk_aa
    python manage.py seed_db --csv-path chunk_ab

VERSION & CHANGELOG
-------------------

Version 1.0.0
- Initial release
- CSV loading with pandas
- Progress reporting
- Alert creation for critical risk
- Idempotent loading
- Comprehensive error handling
- Verification script
- Helper scripts (bash and batch)
"""

# To use this documentation:
# 1. Place this file in api/management/commands/README.txt
# 2. Access it with: python manage.py help seed_db
# 3. Or read directly as reference

export __doc__ = """
Django management command to seed database from CSV file containing
healthcare fraud detection results.

Usage:
    python manage.py seed_db [options]

Options:
    --csv-path PATH     Path to CSV file
    --clear             Clear existing data before loading
    --limit N           Load only first N rows
    --help              Show this help message

For complete documentation, see SEED_DB_GUIDE.md
"""
