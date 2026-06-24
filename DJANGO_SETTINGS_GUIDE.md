# Django Settings Configuration Guide

## Overview

This guide explains the Django settings configuration for the RiskPulse healthcare fraud detection platform. All sensitive data (database credentials, API keys, secrets) are managed through environment variables for security.

## Quick Start

### 1. Install Dependencies

```bash
pip install python-decouple
pip install psycopg2-binary  # PostgreSQL adapter
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install django-cors-headers
```

### 2. Environment Variables Setup

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your configuration values:
```bash
# Security
SECRET_KEY=your-production-secret-key
DEBUG=False  # Set to False in production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DB_NAME=riskpulse_db
DB_USER=riskpulse_user
DB_PASSWORD=your-secure-password
DB_HOST=your-postgres-host
DB_PORT=5432

# Frontend
FRONTEND_URL=https://yourdomain.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb riskpulse_db
createuser riskpulse_user

# Or use Django migrations
python manage.py migrate
```

### 4. Run Development Server

```bash
python manage.py runserver
```

---

## Configuration Sections

### 1. Database Configuration

**Using PostgreSQL (Recommended for Production)**

Environment Variables:
- `DB_NAME`: Database name (default: `riskpulse_db`)
- `DB_USER`: Database user (default: `riskpulse_user`)
- `DB_PASSWORD`: Database password (required for production)
- `DB_HOST`: Database host (default: `localhost`)
- `DB_PORT`: Database port (default: `5432`)

Settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='riskpulse_db'),
        'USER': config('DB_USER', default='riskpulse_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

**Connection Pooling**

- `CONN_MAX_AGE`: Reuse connections for 600 seconds (10 minutes)
- Connection timeouts: 10 seconds
- Better performance with many concurrent users

**Using SQLite (Development Only)**

Uncomment in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. CORS Configuration

**CORS Headers Middleware**

Allows cross-origin requests from specified origins:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Development
    "http://127.0.0.1:3000",      # Localhost alternative
    config('FRONTEND_URL', default='http://localhost:3000'),
]
```

**Allowed Methods**
- GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers**
- Content-Type, Authorization, X-CSRF-Token, etc.

**Credentials**
- `CORS_ALLOW_CREDENTIALS = True` allows cookies/auth headers

**Configuration by Environment**

Development:
```python
CORS_ALLOWED_ORIGINS = ['*']  # Allow all origins
```

Production:
```python
CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']  # Specific origin only
CORS_ALLOW_CREDENTIALS = True
```

### 3. REST Framework Configuration

**Default Authentication: JWT**

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

**Permissions**

- `IsAuthenticated`: All endpoints require login/JWT token
- Can override per-view with `permission_classes`

**Pagination**

```python
'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 20,
```

Customize per-view:
```python
class MyViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination  # Override default
```

**Throttling (Rate Limiting)**

```python
'DEFAULT_THROTTLE_CLASSES': (
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
),
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',      # Anonymous users: 100 requests/hour
    'user': '1000/hour',     # Authenticated: 1000 requests/hour
}
```

### 4. SIMPLE JWT Configuration

**Token Lifetimes**

- `ACCESS_TOKEN_LIFETIME`: 1 day (24 hours)
- `REFRESH_TOKEN_LIFETIME`: 7 days
- Refresh tokens can generate new access tokens

**Token Features**

- `ROTATE_REFRESH_TOKENS`: True - generates new refresh token on each refresh
- `BLACKLIST_AFTER_ROTATION`: True - invalidates old tokens
- `JTI_CLAIM`: Unique token identifier (prevents reuse)

**Obtaining Tokens**

POST `/api/token/`
```json
{
    "username": "user@example.com",
    "password": "password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Using Access Token**

Header: `Authorization: Bearer <access_token>`

**Refreshing Token**

POST `/api/token/refresh/`
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Token Claims**

Default claims in token:
- `user_id`: User's ID
- `username`: Username
- `email`: User's email
- `exp`: Expiration time
- `iat`: Issued at time
- `jti`: JWT ID (unique identifier)

**Customizing Token Content**

Override `TokenObtainPairSerializer`:
```python
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = getattr(user, 'profile').role
        
        return token
```

### 5. Media Files Configuration

**Purpose**

Stores generated reports, uploads, and other user-generated content.

**Configuration**

```python
MEDIA_URL = '/media/'              # URL prefix
MEDIA_ROOT = BASE_DIR / 'media'    # File system path
```

**Directory Structure**

```
media/
├── reports/          # Generated PDF reports
├── uploads/         # User uploads
└── cache/          # Temporary files
```

**Automatic Creation**

Directories are created automatically:
```python
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT / 'reports', exist_ok=True)
```

**Serving Files in Development**

Added to `urls.py`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Production**

Use web server (nginx, Apache) or cloud storage (S3):
```python
# settings.py (optional - S3)
if not DEBUG:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
    }
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
```

**Report Generation**

Reports stored at: `media/reports/`

Example:
```python
report_path = settings.MEDIA_ROOT / 'reports' / f'report_{uuid4()}.pdf'
```

---

## Security Settings

### Development vs Production

**Development** (`DEBUG=True`)

- HTTPS disabled
- CSRF checks disabled
- Debug toolbar enabled
- All hosts allowed
- CORS allows all origins

**Production** (`DEBUG=False`)

```python
SECURE_SSL_REDIRECT = True              # Force HTTPS
SESSION_COOKIE_SECURE = True            # HTTPS only cookies
CSRF_COOKIE_SECURE = True               # HTTPS only CSRF

SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Environment Variables Security

**Never commit secrets to git:**

```bash
# .gitignore
.env
.env.local
.env.*.local
```

**Secure Secret Management**

1. Generate strong SECRET_KEY:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

2. Store in environment (.env file or deployment platform):
```
SECRET_KEY=django-insecure-a_secure_random_string_here
```

3. Use in development only:
```python
SECRET_KEY = config('SECRET_KEY', default='dev-key-only')
```

### CSRF Protection

- `CSRF_TRUSTED_ORIGINS`: Allowed hosts for CSRF validation
- `CSRF_COOKIE_HTTPONLY`: Prevents JavaScript access to CSRF token

---

## Logging Configuration

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Log Handlers

1. **Console**: Real-time logs in terminal
2. **File**: Persistent logs to file
3. **Rotating File**: Automatic log rotation

### Log Files

Located in `logs/` directory:
- `django.log`: Django framework logs
- `api.log`: API application logs

### Log Rotation

- Max file size: 10MB
- Keep: 5 backup files
- Auto-rotates when size exceeded

### Customizing Logging

```python
# Change log level
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Add more specific logging
LOGGING['loggers']['my_app'] = {
    'handlers': ['console', 'file'],
    'level': 'INFO',
}
```

---

## Common Tasks

### Creating Superuser

```bash
python manage.py createsuperuser
# Enter username, email, password
```

### Database Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

### Loading Fixture Data

```bash
python manage.py loaddata data.json
```

### Dumping Data

```bash
python manage.py dumpdata > data.json
```

---

## Deployment

### Heroku

```bash
# Set environment variables
heroku config:set SECRET_KEY='your-secret-key'
heroku config:set DEBUG=False
heroku config:set DB_HOST='your-postgres-host'

# Deploy
git push heroku main
```

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "riskpulse_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### AWS EC2

1. Launch EC2 instance
2. Install Python, PostgreSQL
3. Clone repository
4. Set environment variables
5. Run migrations
6. Start server with Gunicorn + Nginx

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'decouple'"

**Solution:**
```bash
pip install python-decouple
```

### Issue: "DATABASES is improperly configured"

**Solution:** Ensure `DB_PASSWORD` is set:
```bash
export DB_PASSWORD='your-password'
```

### Issue: "CORS errors in browser console"

**Solution:** Verify `CORS_ALLOWED_ORIGINS` includes frontend URL:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

### Issue: "JWT token expired"

**Solution:** Refresh token:
```bash
POST /api/token/refresh/
{
    "refresh": "your-refresh-token"
}
```

### Issue: "Permission denied" errors

**Solution:** Check `DEFAULT_PERMISSION_CLASSES`:
```python
# Allow unauthenticated access to specific views
class PublicView(APIView):
    permission_classes = [permissions.AllowAny]
```

---

## References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Python Decouple](https://github.com/henriquebastos/python-decouple)

---

## Environment Variables Reference

### Required
- `SECRET_KEY`: Django secret key
- `DB_PASSWORD`: PostgreSQL password (if using PostgreSQL)

### Optional with Defaults
- `DEBUG`: False (set explicitly for production)
- `ALLOWED_HOSTS`: localhost,127.0.0.1
- `DB_NAME`: riskpulse_db
- `DB_USER`: riskpulse_user
- `DB_HOST`: localhost
- `DB_PORT`: 5432
- `FRONTEND_URL`: http://localhost:3000
- `CACHE_BACKEND`: django.core.cache.backends.locmem.LocMemCache
- `EMAIL_BACKEND`: django.core.mail.backends.console.EmailBackend

### JWT Settings (configured in code)
- `ACCESS_TOKEN_LIFETIME`: 1 day
- `REFRESH_TOKEN_LIFETIME`: 7 days
- Algorithm: HS256 (HMAC with SHA-256)

---

## Support

For issues or questions, refer to:
1. This guide
2. settings.py comments
3. Official Django/DRF documentation
4. Project GitHub issues
