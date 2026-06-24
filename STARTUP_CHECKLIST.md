# RiskPulse Platform - Startup Checklist

Complete these steps in order to get your fraud detection platform running.

## Phase 1: Environment Setup ✅ (Already Done)

- [x] Python virtual environment created
- [x] Django 6.0.6 configured
- [x] `.env` file created with development defaults
- [x] `api/models.py` created with Transaction, Alert, AuditLog models
- [x] `api/serializers.py` created with serializers
- [x] `api/views.py` created with 6 API endpoints
- [x] `api/urls.py` created with URL routing
- [x] `api/ml/scorer.py` created with ML scoring logic
- [x] Django settings configured with PostgreSQL, JWT, CORS
- [x] Admin interface configured
- [x] Import statements fixed

## Phase 2: Django Database Setup (DO THIS NOW)

### Step 2.1: Activate Virtual Environment
```bash
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 2.2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Expected output**: All packages installed successfully

### Step 2.3: Create Database Migrations
```bash
python manage.py makemigrations
```

**Expected output**:
```
Migrations for 'api':
  api/migrations/0001_initial.py
    - Create model Transaction
    - Create model Alert
    - Create model AuditLog
```

- [ ] Migrations created successfully

### Step 2.4: Apply Migrations to Database
```bash
python manage.py migrate
```

**Expected output**:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying api.0001_initial... OK
```

- [ ] Migrations applied successfully

### Step 2.5: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

**Expected output**:
```
Found X static files to collect.
Copying files from staticfiles...
Copying other files (e.g. license files)
Post-processing 'admin/js/admin/...' files

X static files copied to 'staticfiles/'.
```

- [ ] Static files collected

### Step 2.6: Create Superuser
```bash
python manage.py createsuperuser
```

**Recommended credentials** (for local development):
- Username: `admin`
- Email: `admin@localhost`
- Password: `admin` (or your choice)

**Expected output**:
```
Superuser created successfully.
```

- [ ] Superuser created

## Phase 3: Load Sample Data (Optional)

### Step 3.1: Load Data
```bash
python manage.py seed_db --csv-path api/management/commands/sample_data.csv --clear
```

**Expected output**:
```
Loading CSV data from: api/management/commands/sample_data.csv
Processing X rows...
✓ Data loaded successfully!
```

- [ ] Sample data loaded (optional, for testing)

## Phase 4: Start Django Backend

### Step 4.1: Run Django Development Server
```bash
python manage.py runserver
```

**Expected output**:
```
Django version 6.0.6, using settings 'riskpulse_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**Keep this terminal running!**

- [ ] Django server running at `http://localhost:8000`

### Step 4.2: Test Backend

Open browser and visit:
- Admin panel: http://localhost:8000/admin/
  - Login with superuser credentials
  - Verify Transaction, Alert, AuditLog models visible
- API endpoints:
  - http://localhost:8000/api/transactions/
  - http://localhost:8000/api/dashboard/stats/
  - http://localhost:8000/api/alerts/

- [ ] Backend responding correctly

## Phase 5: Frontend Setup (New Terminal)

**IMPORTANT: Keep Django server running in previous terminal!**

### Step 5.1: Navigate to Frontend
```bash
cd frontend
```

### Step 5.2: Install React Dependencies
```bash
npm install
```

**Expected output**:
```
added XXX packages in XXXs
```

- [ ] Frontend dependencies installed

### Step 5.3: Create Frontend Environment File
Create `frontend/.env` with:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_API_TIMEOUT=10000
```

- [ ] Frontend `.env` created

### Step 5.4: Start React Development Server
```bash
npm start
```

**Expected output**:
```
Compiled successfully!

You can now view riskpulse in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

- [ ] React server running at `http://localhost:3000`

## Phase 6: Integration Testing

### Test 6.1: Access Dashboard
- [ ] Visit http://localhost:3000 in browser
- [ ] Dashboard loads without errors
- [ ] Stats visible (if sample data loaded)

### Test 6.2: Test API Connection
- [ ] Open browser DevTools (F12)
- [ ] Check Network tab for API calls
- [ ] Verify no CORS errors
- [ ] Verify requests return 200 status

### Test 6.3: Score a Transaction
- [ ] Navigate to "Risk Scorer" tab
- [ ] Fill in form fields
- [ ] Click "Score Transaction"
- [ ] See result with risk score and components

### Test 6.4: View Transactions
- [ ] Navigate to "Dashboard" tab
- [ ] See transaction list
- [ ] Filter by risk tier
- [ ] Pagination works

### Test 6.5: Check Alerts
- [ ] Navigate to "Alerts" tab
- [ ] See high-risk alerts
- [ ] Mark alert as resolved
- [ ] Alert disappears

## Phase 7: Verification Checklist

- [ ] Django migrations completed
- [ ] Database tables created
- [ ] Superuser account created
- [ ] Django server starts without errors
- [ ] React frontend installs without errors
- [ ] Frontend can access backend API
- [ ] Dashboard loads and displays stats
- [ ] Can score new transactions
- [ ] Can view transaction list
- [ ] Can see alerts
- [ ] Admin panel accessible at `/admin/`

## Phase 8: File Structure Verification

Verify these files exist:

- [x] `d:\riskpulse\manage.py`
- [x] `d:\riskpulse\.env`
- [x] `d:\riskpulse\requirements.txt`
- [x] `d:\riskpulse\riskpulse_project\settings.py`
- [x] `d:\riskpulse\riskpulse_project\urls.py`
- [x] `d:\riskpulse\api\models.py`
- [x] `d:\riskpulse\api\views.py`
- [x] `d:\riskpulse\api\serializers.py`
- [x] `d:\riskpulse\api\urls.py`
- [x] `d:\riskpulse\api\admin.py`
- [x] `d:\riskpulse\api\apps.py`
- [x] `d:\riskpulse\api\ml\scorer.py`
- [x] `d:\riskpulse\api\management\commands\seed_db.py`
- [x] `d:\riskpulse\frontend\src\components\Dashboard\Dashboard.jsx`
- [x] `d:\riskpulse\frontend\src\components\RiskScorer\RiskScorer.jsx`
- [x] `d:\riskpulse\frontend\src\utils\api.js`

## 🚀 Quick Start Commands

**Terminal 1 (Backend):**
```bash
cd d:\riskpulse
venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Terminal 2 (Frontend):**
```bash
cd d:\riskpulse\frontend
npm install
npm start
```

Then open: http://localhost:3000

## 📊 Default Credentials

For local development:

**Django Admin:**
- URL: http://localhost:8000/admin/
- Username: `admin`
- Password: (whatever you set during `createsuperuser`)

**Sample Data:**
- Can be loaded with: `python manage.py seed_db --csv-path api/management/commands/sample_data.csv --clear`

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution:** Install requirements with `pip install -r requirements.txt`

### Issue: "Port 8000 already in use"
**Solution:** Use different port: `python manage.py runserver 8001`

### Issue: "Port 3000 already in use"
**Solution:** Use different port: `npm start -- --port 3001`

### Issue: CORS errors in console
**Solution:** Check `FRONTEND_URL` in `.env` and `CORS_ALLOWED_ORIGINS` in settings.py

### Issue: React not connecting to API
**Solution:** Verify `REACT_APP_API_URL` in `frontend/.env` is set correctly

### Issue: Database locked
**Solution:** Delete `db.sqlite3` and run migrations again

### Issue: "No such table: api_transaction"
**Solution:** Run `python manage.py migrate` to create tables

## 📚 Documentation Files

- `QUICK_START.md` - Quick start guide
- `DJANGO_SETTINGS_GUIDE.md` - Django configuration details
- `SETUP_GUIDE.md` - Comprehensive setup guide
- `CONFIGURATION_SUMMARY.md` - Configuration overview
- `STARTUP_CHECKLIST.md` - This file

## ✨ Next Steps After Setup

1. **Test with API endpoints** using Postman or cURL
2. **Load sample data** with seed_db command
3. **Create real users** in Django admin
4. **Configure PostgreSQL** for production
5. **Deploy to Azure** using deployment guide

## 📞 Support

If you encounter issues:
1. Check error message carefully
2. Review troubleshooting section above
3. Check browser console for errors (F12)
4. Check Django logs in terminal
5. Verify all environment variables in `.env`

---

**Status**: Ready to start setup! Begin with Phase 2, Step 2.1
