# RiskPulse Platform - Quick Start Guide

## ✅ Fixed Issues
- Updated `config()` fallback function to support `cast` parameter
- Created `.env` file with development defaults
- Moved models to `api/models.py`
- Created Django app configuration files
- Fixed INSTALLED_APPS configuration

## 🚀 Getting Started

### Step 1: Install Required Dependencies

Run this command in your terminal (with venv activated):

```bash
pip install -r requirements.txt
```

This installs:
- Django & Django REST Framework
- JWT authentication
- CORS support
- PostgreSQL adapter
- Environment variable support
- And all other required packages

### Step 2: Database Setup

Run migrations to create database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Admin User

Create a superuser account to access the admin panel:

```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@localhost`
- Password: (your secure password)

### Step 4: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 5: Load Sample Data (Optional)

Load test data from CSV:

```bash
python manage.py seed_db --csv-path api/management/commands/sample_data.csv --clear
```

This loads 15 test fraud detection records.

### Step 6: Start Django Server

```bash
python manage.py runserver
```

Server will run at: **http://localhost:8000**

### Step 7: In a New Terminal, Start React Frontend

Navigate to frontend directory:

```bash
cd frontend
npm install
npm start
```

Frontend will run at: **http://localhost:3000**

## 📋 Next Steps

### Test the API

1. **Admin Panel**: http://localhost:8000/admin
   - Login with superuser credentials
   - View transactions, alerts, and audit logs

2. **API Endpoints**:
   - http://localhost:8000/api/transactions/
   - http://localhost:8000/api/dashboard/stats/
   - http://localhost:8000/api/alerts/

3. **React Dashboard**: http://localhost:3000
   - View fraud detection dashboard
   - Score new transactions
   - See alerts and risk trends

## 🔧 Configuration

### Environment Variables (.env)

Edit `.env` file to customize:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
FRONTEND_URL=http://localhost:3000
```

For PostgreSQL (production):

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=riskpulse_db
DB_USER=riskpulse_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
```

## 📂 Project Structure

```
d:\riskpulse/
├── manage.py                 # Django CLI
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies
│
├── riskpulse_project/        # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
│
├── api/                      # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── urls.py              # API routes
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── management/          # Management commands
│   │   └── commands/
│   │       └── seed_db.py   # Database seeding
│   ├── ml/                  # Machine learning
│   │   └── scorer.py        # Risk scoring
│   └── __init__.py
│
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── utils/           # Utilities
│   │   └── App.js
│   ├── package.json
│   └── public/
│
├── media/                   # Generated files
│   └── reports/             # PDF reports
├── logs/                    # Application logs
└── staticfiles/             # Collected static files
```

## 🐛 Troubleshooting

### Issue: "Django apps aren't loaded yet"

**Solution:** Make sure you:
1. Have Django installed
2. Run `python manage.py migrate` first
3. Environment variables are set

### Issue: "No module named 'rest_framework'"

**Solution:** Install requirements:
```bash
pip install -r requirements.txt
```

### Issue: "ModuleNotFoundError: No module named 'decouple'"

**Solution:** Already fixed! The fallback config() function now handles type casting.

### Issue: "Port 8000 already in use"

**Solution:** Use different port:
```bash
python manage.py runserver 8001
```

### Issue: React frontend not connecting to backend

**Solution:** Check `FRONTEND_URL` in `.env`:
```
FRONTEND_URL=http://localhost:3000
```

And verify `http://localhost:8000/api` is accessible from browser.

## 📊 API Endpoints

### Authentication
- `POST /api/token/` - Get access/refresh tokens
- `POST /api/token/refresh/` - Refresh access token

### Fraud Detection
- `POST /api/score/` - Score a transaction
- `GET /api/transactions/` - List transactions
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/alerts/` - List alerts
- `PATCH /api/alerts/<id>/resolve/` - Mark alert as resolved
- `POST /api/reports/generate/` - Generate PDF report

## 💡 Usage Examples

### Score a Transaction (cURL)

```bash
curl -X POST http://localhost:8000/api/score/ \
  -H "Content-Type: application/json" \
  -d '{
    "caseid": "CASE001",
    "age": 45,
    "wealth_idx": 2.5,
    "education": "High School",
    "residence": "Urban",
    "has_diabetes": true,
    "has_htn": false,
    "told_high_gluc": false,
    "told_high_bp": false,
    "tx_diabetes": true,
    "tx_htn": false,
    "screening_count": 2
  }'
```

### Get Transactions (cURL with Token)

```bash
# First get token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Use token to get transactions
curl http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer <access_token>"
```

## 📚 Documentation

- `DJANGO_SETTINGS_GUIDE.md` - Django configuration details
- `SETUP_GUIDE.md` - Comprehensive setup instructions
- `CONFIGURATION_SUMMARY.md` - Configuration overview
- `api/management/commands/SEED_DB_GUIDE.md` - Database seeding guide
- `api/API_DOCUMENTATION.py` - API endpoint documentation

## ✨ Features Configured

✅ PostgreSQL database (with SQLite dev fallback)
✅ JWT authentication (1-day access tokens)
✅ CORS headers (localhost:3000)
✅ REST Framework with rate limiting
✅ Admin panel with model management
✅ Media files for PDF reports
✅ Comprehensive logging
✅ Error handling and validation
✅ Production-ready security settings

## 🚢 Deployment

For production deployment:

1. Update `.env`:
   - Set `DEBUG=False`
   - Generate strong `SECRET_KEY`
   - Configure PostgreSQL
   - Update `ALLOWED_HOSTS`

2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

3. Run with Gunicorn:
   ```bash
   gunicorn riskpulse_project.wsgi:application --bind 0.0.0.0:8000
   ```

4. Configure Nginx as reverse proxy

See `SETUP_GUIDE.md` for detailed deployment instructions.

## 📞 Support

For issues:
1. Check error messages carefully
2. Review `.env` configuration
3. Check logs in `logs/` directory
4. Verify database connection
5. See troubleshooting section above

Ready to go! 🎉
