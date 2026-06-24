"""
Django Management Command: seed_db
==================================

Comprehensive guide for the seed_db management command.

PURPOSE
-------
Seed the healthcare fraud detection database from a CSV file containing
historical fraud detection results. The command creates Transaction and Alert
objects from CSV rows, with built-in progress tracking and error handling.

INSTALLATION
------------

1. Ensure the directory structure exists:
   
   api/
   ├── management/
   │   ├── __init__.py
   │   └── commands/
   │       ├── __init__.py
   │       └── seed_db.py

2. Install required dependencies:
   
   pip install pandas

3. Verify Django app is in INSTALLED_APPS in settings.py:
   
   INSTALLED_APPS = [
       ...
       'api',
       ...
   ]

USAGE
-----

Basic Usage (default CSV file):

    python manage.py seed_db

With custom CSV file path:

    python manage.py seed_db --csv-path /full/path/to/hcfd_xai_final_results.csv

With relative path from project root:

    python manage.py seed_db --csv-path data/hcfd_xai_final_results.csv

Clear existing data before loading:

    python manage.py seed_db --clear

Limit rows for testing:

    python manage.py seed_db --limit 100

Combine options:

    python manage.py seed_db --csv-path data/results.csv --clear --limit 1000

CSV FILE FORMAT
---------------

Required columns in CSV:
- caseid: Unique case identifier (string)
- age: Patient age (integer, 0-150)
- wealth_idx: Wealth index (float, 0-5)
- education: Education level (string)
- residence: Residence type (string, e.g., "Urban", "Rural")
- has_diabetes: Diabetes diagnosis (boolean: true/false, 0/1, yes/no, etc.)
- has_htn: Hypertension diagnosis (boolean)
- DVS: Demographic Variability Score (float, 0-1)
- TNS: Testing/Screening Score (float, 0-1)
- ICS: Income/Wealth Score (float, 0-1)
- CCS: Consistency Check Score (float, 0-1)
- HCFD_score: Healthcare Fraud Detection Score (float, 0-1)
- rule_score: Rule-based fraud score (float, 0-1)
- anomaly_score: ML anomaly score (float, 0-1)
- final_risk: Final fraud risk score (float, 0-1)
- risk_tier: Risk tier (string: low/medium/high/critical or variants)
- explanation: Risk assessment explanation (string, optional)

Example CSV header:
caseid,age,wealth_idx,education,residence,has_diabetes,has_htn,DVS,TNS,ICS,CCS,HCFD_score,rule_score,anomaly_score,final_risk,risk_tier,explanation
CASE001,45,2.5,High School,Urban,true,false,0.5625,0.667,0.5,0.75,0.012,0.25,0.401,0.523,high,"Risk Assessment: High Risk..."

COMMAND OPTIONS
---------------

--csv-path PATH
    Path to the CSV file to load
    Default: hcfd_xai_final_results.csv
    Can be absolute path or relative to Django project root
    
    Examples:
    --csv-path /home/user/data/results.csv
    --csv-path data/hcfd_xai_final_results.csv
    --csv-path ./results.csv

--clear
    Clear all existing Transaction and Alert records before loading
    WARNING: Use with caution in production!
    Useful for:
    - Starting fresh with new data
    - Replacing entire database
    - Testing on clean database
    
    Usage:
    python manage.py seed_db --csv-path data.csv --clear

--limit N
    Load only the first N rows from the CSV file
    Useful for:
    - Testing with small dataset
    - Incremental loading
    - Validating CSV format
    
    Examples:
    --limit 100    # Load first 100 rows
    --limit 10000  # Load first 10,000 rows

OUTPUT & PROGRESS
-----------------

The command provides detailed output including:

1. Progress messages every 1000 rows:
   Progress: 1000/50000 (Created: 987, Skipped: 13, Alerts: 234)

2. Error messages for problematic rows with context:
   Error processing row 2345 (caseid=CASE002345): Invalid age value

3. Summary at completion:
   ======================================================================
   DATABASE SEEDING COMPLETE
   ======================================================================
   Total rows in CSV:            50000
   Transactions created:         49500
   Transactions skipped:            500
   Alerts created:               5200
   ======================================================================
   Successfully loaded 49500 transactions and created 5200 alerts.

BEHAVIOR & LOGIC
----------------

1. Idempotent Loading:
   - Checks if caseid already exists before creating
   - Skips existing transactions to avoid duplicates
   - Safe to run multiple times

2. Alert Creation:
   - Automatically creates Alert if final_risk > 0.75
   - Alert includes: risk_tier, final_risk, critical risk message
   - Links to Transaction via ForeignKey

3. Boolean Parsing:
   - Accepts: true/false, 1/0, yes/no, on/off (case-insensitive)
   - Converts to Python boolean

4. Risk Tier Normalization:
   - Accepts: "low", "medium", "high", "critical"
   - Also accepts: "Low Risk", "Medium Risk", etc.
   - Normalizes to lowercase single word

5. Transaction Atomicity:
   - All database operations wrapped in transaction
   - If error occurs, database rolled back
   - Ensures data consistency

6. Error Recovery:
   - Continues processing even if row fails
   - Records error count
   - Doesn't stop entire seeding process

PERFORMANCE CONSIDERATIONS
---------------------------

For large CSV files (100,000+ rows):

1. Memory Usage:
   - Pandas loads entire CSV into memory
   - For 500K+ rows, consider splitting CSV
   - Can pre-process CSV with other tools

2. Database Performance:
   - Bulk operations are atomic (slower but safer)
   - Consider increasing Django transaction buffer
   - Use database in same network for faster operations

3. Progress Tracking:
   - Reports progress every 1000 rows
   - Allows monitoring long-running seeds

Example for processing large files:
    
    # Split CSV and load incrementally
    python manage.py seed_db --csv-path part1.csv --limit 100000
    python manage.py seed_db --csv-path part2.csv --limit 100000

TROUBLESHOOTING
---------------

Issue: "CSV file not found"
Solution: Check file path is correct and file exists
  - Use absolute path: --csv-path /full/path/to/file.csv
  - Or relative from project root: --csv-path data/file.csv

Issue: "CSV missing required columns"
Solution: Verify all required columns are in CSV
  - Check column names match exactly (case-sensitive)
  - Open CSV in Excel/text editor to verify headers

Issue: "Error processing row X: Invalid age value"
Solution: Check data type for that row
  - Age must be integer
  - Other numeric fields must be float
  - Check for NULL or invalid values in CSV

Issue: "No new transactions were loaded"
Solution: Check if all records already exist
  - Use --clear flag to remove old records: --clear
  - Check caseid values for duplicates

Issue: Out of Memory error
Solution: Reduce load size
  - Use --limit flag: --limit 50000
  - Process CSV in multiple batches
  - Increase available memory to Python process

Issue: Transactions created but alerts not appearing
Solution: Check final_risk values
  - Alerts only created if final_risk > 0.75
  - Check threshold in seed_db.py if needed

DATABASE STATE
--------------

Before seeding:
- Empty or existing database

After seeding (example):
- 49,500 Transaction records created
- 5,200 Alert records created (from critical risk transactions)
- Related audit logs created if using audit logging

To verify:

    # In Django shell
    from models import Transaction, Alert
    
    # Count records
    print(Transaction.objects.count())  # 49500
    print(Alert.objects.count())        # 5200
    
    # Check recent transactions
    print(Transaction.objects.order_by('-created_at')[:5])
    
    # Check alerts
    print(Alert.objects.filter(is_resolved=False).count())

EXAMPLE WORKFLOWS
-----------------

Workflow 1: Fresh database setup
    
    python manage.py migrate
    python manage.py seed_db --csv-path data/hcfd_results.csv

Workflow 2: Replace existing data
    
    python manage.py seed_db --csv-path data/new_results.csv --clear

Workflow 3: Test with small dataset
    
    python manage.py seed_db --csv-path data/hcfd_results.csv --limit 1000

Workflow 4: Incremental loading
    
    python manage.py seed_db --csv-path data/batch1.csv
    python manage.py seed_db --csv-path data/batch2.csv
    # (Idempotent - won't duplicate data)

Workflow 5: Production reload
    
    # Backup database first
    python manage.py dumpdata > backup.json
    
    # Load new data
    python manage.py seed_db --csv-path data/prod_results.csv --clear
    
    # Verify data loaded
    python manage.py shell < verify.py

MONITORING & DEBUGGING
----------------------

Enable verbose output:
    
    python manage.py seed_db -v 2

Get list of all caseids:
    
    python manage.py shell
    >>> from models import Transaction
    >>> list(Transaction.objects.values_list('caseid', flat=True)[:10])

Check for duplicate caseids:
    
    >>> from django.db.models import Count
    >>> duplicates = (
    ...     Transaction.objects
    ...     .values('caseid')
    ...     .annotate(count=Count('id'))
    ...     .filter(count__gt=1)
    ... )
    >>> list(duplicates)

Find high-risk transactions:
    
    >>> Transaction.objects.filter(final_risk__gte=0.75).count()
    5200

Check alerts:
    
    >>> Alert.objects.filter(is_resolved=False).count()
    5200

MIGRATION & BACKUP
------------------

Before large seed operation:

    # Backup database
    python manage.py dumpdata > backup_$(date +%Y%m%d).json
    
    # Or use native database backup
    # For SQLite:
    cp db.sqlite3 db.sqlite3.backup

After seeding:

    # Verify data
    python manage.py shell < verification_script.py
    
    # If needed, restore
    python manage.py flush
    python manage.py loaddata backup.json

ADVANCED USAGE
--------------

Custom data processing before loading:

    # Clean CSV before loading
    import pandas as pd
    df = pd.read_csv('raw_data.csv')
    df = df.dropna()  # Remove rows with NULL
    df = df.drop_duplicates(subset=['caseid'])  # Remove duplicate caseids
    df.to_csv('cleaned_data.csv', index=False)
    
    # Then seed
    python manage.py seed_db --csv-path cleaned_data.csv

Extend the command:

    # Create custom version of seed_db with additional logic
    # Edit api/management/commands/seed_db.py
    # Add your custom processing in _seed_transactions()

SUPPORT & DOCUMENTATION
-----------------------

Command help:
    
    python manage.py seed_db --help

Django documentation:
    
    https://docs.djangoproject.com/en/stable/howto/custom-management-commands/

Pandas documentation:
    
    https://pandas.pydata.org/docs/

Related Django models:
    - Transaction (api/models.py)
    - Alert (api/models.py)
    - AuditLog (api/models.py)
"""

# For reference, here are sample test files you might want to create:

# test_data.csv
"""
caseid,age,wealth_idx,education,residence,has_diabetes,has_htn,DVS,TNS,ICS,CCS,HCFD_score,rule_score,anomaly_score,final_risk,risk_tier,explanation
CASE001,45,2.5,High School,Urban,true,false,0.5625,0.667,0.5,0.75,0.012,0.25,0.401,0.523,high,Risk: High Risk
CASE002,55,1.5,Elementary,Rural,true,true,0.6875,0.333,0.3,0.5,0.024,0.5,0.650,0.823,critical,Risk: Critical Risk
CASE003,35,3.5,College,Urban,false,false,0.4375,0.667,0.7,0.75,0.010,0.0,0.150,0.185,low,Risk: Low Risk
"""

# verify.py
"""
from models import Transaction, Alert
from django.db.models import Avg, Count

print("Database Verification Report")
print("=" * 50)

total_transactions = Transaction.objects.count()
total_alerts = Alert.objects.count()
avg_risk = Transaction.objects.aggregate(avg=Avg('final_risk'))['avg']

print(f"Total Transactions: {total_transactions}")
print(f"Total Alerts: {total_alerts}")
print(f"Average Risk Score: {avg_risk:.3f}")

risk_distribution = Transaction.objects.values('risk_tier').annotate(count=Count('id'))
for item in risk_distribution:
    print(f"  {item['risk_tier']}: {item['count']}")

print("\nVerification complete!")
"""
