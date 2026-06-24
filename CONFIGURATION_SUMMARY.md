# Django Configuration Summary

## What Was Added

### 1. Django Project Structure Created

Files created:
- `manage.py` - Django management script
- `riskpulse_project/__init__.py` - Package marker
- `riskpulse_project/settings.py` - **[MAIN SETTINGS FILE]**
- `riskpulse_project/urls.py` - URL routing configuration
- `riskpulse_project/wsgi.py` - WSGI application
- `riskpulse_project/asgi.py` - ASGI application (async support)

### 2. Configuration Files

- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `setup.sh` - Linux/Mac automated setup script
- `setup.bat` - Windows automated setup script
- `DJANGO_SETTINGS_GUIDE.md` - Comprehensive settings documentation
- `SETUP_GUIDE.md` - Quick start guide

### 3. Key Features Configured in settings.py

#### A. PostgreSQL Database Configuration ✅

```python
# Uses environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='riskpulse_db'),
        'USER': config('DB_USER', default='riskpulse_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
    }
}
```

Environment Variables Required:
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port

#### B. CORS Headers Configuration ✅

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React dev server
    "http://127.0.0.1:3000",      # Localhost alternative
    config('FRONTEND_URL', default='http://localhost:3000'),
]
```

**Configured:**
- Allows `http://localhost:3000` (React frontend)
- Allows credentials (cookies, auth headers)
- Allows all required HTTP methods
- CORS middleware added to MIDDLEWARE stack

#### C. REST Framework with JWT Authentication ✅

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}
```

**Features:**
- JWT as primary authentication method
- Session auth fallback
- All endpoints require authentication
- Pagination: 20 items per page
- Rate limiting: 100/hour for anonymous, 1000/hour for users

#### D. SIMPLE JWT Configuration ✅

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),     # 1 day
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # 7 days
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    ...
}
```

**Token Details:**
- **Access Token Lifetime**: 1 day (24 hours)
- **Refresh Token Lifetime**: 7 days
- **Token Type**: JWT with HS256 signing
- **Auto-rotation**: Generates new refresh token on each refresh
- **Token Blacklisting**: Old tokens invalidated after rotation

**API Endpoints for JWT:**
- `POST /api/token/` - Obtain tokens
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity

#### E. Media Files Configuration ✅

```python
MEDIA_URL = '/media/'              # URL prefix
MEDIA_ROOT = BASE_DIR / 'media'    # File system path

# Auto-created directories
media/
├── reports/          # Generated PDF reports
├── uploads/         # User uploads
└── cache/          # Temporary files
```

**Usage:**
- Reports saved to `media/reports/`
- Accessible via `/media/` URL (development)
- Directories auto-created on startup
- Ready for S3 integration in production

### 4. Security Configuration

**Development Mode** (`DEBUG=True`):
- HTTPS disabled
- CSRF checks relaxed
- All hosts allowed
- CORS allows all origins

**Production Mode** (`DEBUG=False`):
- HTTPS enforced
- HSTS headers (1 year)
- Secure cookies
- XSS protection
- Clickjacking protection
- Content Security Policy

### 5. Additional Features

**Logging:**
- Console logging for real-time output
- File logging with rotation (10MB max, 5 backups)
- Separate logs for Django and API
- Configurable log levels

**Caching:**
- Local memory cache by default
- Redis support available
- Connection pooling enabled

**Email:**
- Console backend for development
- SMTP support for production
- Gmail integration ready

---

## How to Use

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `django` - Web framework
- `djangorestframework` - REST API framework
- `djangorestframework-simplejwt` - JWT authentication
- `django-cors-headers` - CORS support
- `psycopg2-binary` - PostgreSQL adapter
- `python-decouple` - Environment configuration

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=riskpulse_db
DB_USER=riskpulse_user
DB_PASSWORD=your-secure-password
DB_HOST=your-postgres-host
DB_PORT=5432
FRONTEND_URL=https://yourdomain.com
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb riskpulse_db
createuser riskpulse_user

# Run migrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
# Development
python manage.py runserver

# Production
gunicorn riskpulse_project.wsgi:application
```

---

## Configuration Precedence

Settings are loaded in this order (first found wins):

1. **Environment Variables** (`.env` file via python-decouple)
2. **settings.py defaults** (config() fallback values)
3. **Hard-coded defaults** (commented in settings.py)

Example:
```python
# This checks: ENV['DB_NAME'] → falls back to 'riskpulse_db'
DB_NAME = config('DB_NAME', default='riskpulse_db')
```

---

## Installed Applications

INSTALLED_APPS includes:
- `django.contrib.admin` - Admin interface
- `django.contrib.auth` - Authentication
- `django.contrib.contenttypes` - Content types
- `django.contrib.sessions` - Sessions
- `django.contrib.messages` - Messages
- `django.contrib.staticfiles` - Static files
- `rest_framework` - Django REST Framework
- `rest_framework_simplejwt` - JWT authentication
- `corsheaders` - CORS support
- `api` - Your custom app

---

## Middleware Stack

Middleware processing order (request → response):
1. SecurityMiddleware - Security headers
2. CorsMiddleware - CORS handling
3. SessionMiddleware - Session management
4. CommonMiddleware - Security, encoding
5. CsrfViewMiddleware - CSRF protection
6. AuthenticationMiddleware - Authentication
7. MessageMiddleware - Messages framework
8. ClickjackingMiddleware - X-Frame-Options

---

## Database Schema Notes

PostgreSQL configuration:
- Connection pooling: 600 seconds (10 minutes)
- Connection timeout: 10 seconds
- Automatically created indexes on frequently queried fields
- Transactions handled by Django ORM

---

## API Authentication Flow

1. **Login** - POST `/api/token/`
   - Send: username & password
   - Receive: access & refresh tokens

2. **Request** - Include access token in header
   - Header: `Authorization: Bearer <access_token>`
   - Token valid for 1 day

3. **Refresh** - POST `/api/token/refresh/` when expired
   - Send: refresh token
   - Receive: new access token (valid 1 day)

4. **Logout** - Token expires after 1 day
   - Or manually blacklist token (if using blacklist app)

---

## Media Files & Reports

Generated reports stored in:
- Path: `MEDIA_ROOT/reports/`
- URL: `/media/reports/`
- File format: PDF
- Access: Authenticated users only

---

## Environment-Specific Overrides

### Development

```env
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=*
DB_ENGINE=django.db.backends.sqlite3
```

### Staging

```env
DEBUG=False
ALLOWED_HOSTS=staging.yourdomain.com
FRONTEND_URL=https://staging.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
SECURE_SSL_REDIRECT=False  # Behind load balancer
```

### Production

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FRONTEND_URL=https://yourdomain.com
DB_ENGINE=django.db.backends.postgresql
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
```

---

## Troubleshooting Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] Requirements installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` set in `.env`
- [ ] PostgreSQL running (or SQLite for dev)
- [ ] Database credentials in `.env`
- [ ] Migrations run: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] CORS_ALLOWED_ORIGINS includes frontend URL
- [ ] Static files collected: `python manage.py collectstatic`

---

## Next Steps

1. ✅ Review `DJANGO_SETTINGS_GUIDE.md` for detailed configuration
2. ✅ Follow `SETUP_GUIDE.md` for installation steps
3. ✅ Set environment variables in `.env`
4. ✅ Run database migrations
5. ✅ Create superuser account
6. ✅ Start development server
7. → Load seed data: `python manage.py seed_db`
8. → Test API endpoints
9. → Integrate React frontend
10. → Deploy to production

---

## Files Reference

| File | Purpose |
|------|---------|
| `settings.py` | Main Django configuration |
| `urls.py` | URL routing |
| `wsgi.py` | WSGI application entry point |
| `asgi.py` | ASGI application entry point |
| `manage.py` | Django CLI tool |
| `.env.example` | Environment template |
| `requirements.txt` | Python dependencies |
| `DJANGO_SETTINGS_GUIDE.md` | Comprehensive settings docs |
| `SETUP_GUIDE.md` | Quick start guide |

---

## Dependencies Added

### Core Django
- `Django` - Web framework
- `djangorestframework` - REST API
- `djangorestframework-simplejwt` - JWT auth
- `django-cors-headers` - CORS support

### Database
- `psycopg2-binary` - PostgreSQL adapter

### Configuration
- `python-decouple` - Environment variables

### Additional
- `gunicorn` - Production server
- `pandas`, `numpy`, `scikit-learn`, `joblib` - ML support
- `reportlab` - PDF generation
- `redis`, `django-redis` - Caching (optional)

---

## Support & Documentation

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **JWT Docs**: https://django-rest-framework-simplejwt.readthedocs.io/
- **CORS Docs**: https://github.com/adamchainz/django-cors-headers
- **Python-decouple**: https://github.com/henriquebastos/python-decouple

---

## Summary

✅ PostgreSQL database configuration with environment variables  
✅ CORS headers allowing http://localhost:3000  
✅ REST_FRAMEWORK with JWT as default authentication  
✅ SIMPLE_JWT with 1 day access token lifetime  
✅ MEDIA_ROOT configured for generated reports  
✅ All secrets use python-decouple or os.environ  
✅ Production-ready security settings  
✅ Development-friendly defaults  
✅ Complete documentation provided  
✅ Automated setup scripts included  

**Ready to deploy!** 🚀
