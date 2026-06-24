# Django Setup & Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (for production) or SQLite (for development)
- Virtual environment manager (venv, virtualenv, or conda)
- Git (for version control)

## Installation Steps

### 1. Clone/Setup Repository

```bash
cd d:\riskpulse
```

### 2. Create Virtual Environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Or run automated setup:

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
bash setup.sh
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=riskpulse_db
DB_USER=riskpulse_user
DB_PASSWORD=your-password
DB_HOST=localhost
```

### 5. Database Setup

**PostgreSQL (Production):**

```bash
# Create database and user
createdb riskpulse_db
createuser riskpulse_user
psql -d riskpulse_db -c "ALTER USER riskpulse_user WITH PASSWORD 'your-password';"
psql -d riskpulse_db -c "GRANT ALL PRIVILEGES ON DATABASE riskpulse_db TO riskpulse_user;"
```

**SQLite (Development - Default):**

Change in `.env`:
```
DEBUG=True
# Leave PostgreSQL variables empty or use defaults
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@riskpulse.com`
- Password: (your secure password)

### 8. Create Necessary Directories

```bash
mkdir -p logs
mkdir -p media/reports
mkdir -p staticfiles
mkdir -p api/ml/models
```

### 9. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 10. Load Seed Data (Optional)

```bash
python manage.py seed_db --csv-path api/management/commands/sample_data.csv --clear
```

---

## Running the Server

### Development Server

```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`
Admin panel: `http://localhost:8000/admin`
API: `http://localhost:8000/api`

### Production Server (Gunicorn)

```bash
gunicorn riskpulse_project.wsgi:application --bind 0.0.0.0:8000
```

### With Nginx Proxy

```bash
gunicorn riskpulse_project.wsgi:application --bind 127.0.0.1:8000 --workers 4
```

Then configure Nginx to forward requests to `127.0.0.1:8000`.

---

## Testing the Setup

### Check Django Installation

```bash
python -c "import django; print(django.VERSION)"
```

### Run Tests

```bash
python manage.py test
pytest
```

### API Health Check

```bash
curl http://localhost:8000/api/
```

### Admin Panel

1. Visit `http://localhost:8000/admin`
2. Login with superuser credentials
3. Create test data

---

## Frontend Integration

### Start React Development Server

```bash
cd frontend
npm install
npm start
```

Runs at: `http://localhost:3000`

### Configure API URL

Frontend automatically connects to backend at:
- Development: `http://localhost:8000/api`
- Production: Set `REACT_APP_API_URL` environment variable

### CORS Configuration

Backend already configured to allow:
- `http://localhost:3000` (React dev server)
- `http://localhost:8000` (Django dev server)

---

## Common Commands

### Django Management Commands

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Load fixtures
python manage.py loaddata fixture.json

# Dump data
python manage.py dumpdata > data.json

# Shell
python manage.py shell

# Run tests
python manage.py test

# Database seed
python manage.py seed_db --csv-path data.csv
```

### Development Utilities

```bash
# Check project setup
python manage.py check

# Show database queries
python manage.py sqlshell

# Show installed packages
pip list

# Freeze requirements
pip freeze > requirements.txt
```

---

## API Endpoints

### Authentication

**Obtain Token:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Use Token:**
```bash
curl http://localhost:8000/api/ \
  -H "Authorization: Bearer <access_token>"
```

### Fraud Detection API

**Score Transaction:**
```bash
curl -X POST http://localhost:8000/api/score/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "caseid": "CASE001",
    "age": 45,
    "wealth_idx": 2.5,
    ...
  }'
```

**Get Transactions:**
```bash
curl http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer <access_token>"
```

**Get Dashboard Stats:**
```bash
curl http://localhost:8000/api/dashboard/stats/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | - | Django secret key (REQUIRED) |
| `DEBUG` | True | Debug mode (False in production) |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Allowed hosts |
| `DB_ENGINE` | postgresql | Database engine |
| `DB_NAME` | riskpulse_db | Database name |
| `DB_USER` | riskpulse_user | Database user |
| `DB_PASSWORD` | - | Database password |
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 5432 | Database port |
| `FRONTEND_URL` | http://localhost:3000 | Frontend URL for CORS |
| `EMAIL_BACKEND` | console | Email backend |
| `EMAIL_HOST` | smtp.gmail.com | SMTP host |
| `CACHE_BACKEND` | locmem | Cache backend |

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "DATABASES is improperly configured"

**Solution:** Check `.env` variables are set:
```bash
echo DB_PASSWORD  # Should not be empty
```

### Issue: "PostgreSQL connection refused"

**Solution:** Verify PostgreSQL is running:
```bash
# Windows
pg_ctl status

# Linux/Mac
psql -U postgres -d postgres -c "SELECT version();"
```

### Issue: "CORS errors in browser"

**Solution:** Verify frontend URL in `.env`:
```
FRONTEND_URL=http://localhost:3000
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
python manage.py runserver 8001  # Use different port
```

Or find and kill process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Issue: "Permission denied" when creating database

**Solution:** Run as superuser or use correct credentials:
```bash
# PostgreSQL
psql -U postgres
createdb riskpulse_db;
```

### Issue: "Static files not found (404)"

**Solution:**
```bash
python manage.py collectstatic --clear
```

### Issue: "JWT token expired"

**Solution:** Refresh token using refresh endpoint:
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

---

## Project Structure

```
d:\riskpulse/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── setup.sh / setup.bat         # Setup scripts
├── DJANGO_SETTINGS_GUIDE.md     # Settings documentation
├── SETUP_GUIDE.md              # This file
│
├── riskpulse_project/           # Django project
│   ├── settings.py              # Settings configuration
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI config
│   └── asgi.py                  # ASGI config
│
├── api/                         # Main app
│   ├── models.py                # Database models
│   ├── views.py                 # API views
│   ├── urls.py                  # API routes
│   ├── serializers.py           # DRF serializers
│   ├── ml/                      # ML module
│   │   └── scorer.py            # Scoring module
│   └── management/commands/     # Management commands
│       └── seed_db.py           # Database seeding
│
├── frontend/                    # React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   └── RiskScorer/
│   │   └── utils/
│   │       └── api.js           # API client
│   └── package.json
│
├── media/                       # User uploads, reports
│   └── reports/                 # Generated reports
├── logs/                        # Application logs
└── staticfiles/                 # Collected static files
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure environment
3. ✅ Setup database
4. ✅ Run migrations
5. ✅ Create superuser
6. ✅ Start dev server
7. → Load sample data
8. → Test API endpoints
9. → Run frontend
10. → Test integration

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## Support

For issues:
1. Check `.env` configuration
2. Review error messages in logs/
3. Check Django settings
4. Verify database connection
5. See DJANGO_SETTINGS_GUIDE.md

## Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set `ALLOWED_HOSTS` for your domain
- [ ] Update `FRONTEND_URL`
- [ ] Enable HTTPS
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Configure email backend
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser
- [ ] Set up monitoring/logging
- [ ] Configure backups
- [ ] Test all endpoints
