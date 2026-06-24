"""
Healthcare Fraud Detection API Endpoints Documentation

This module provides comprehensive API endpoints for healthcare fraud detection.
All endpoints include automatic audit logging.
"""


"""
=============================================================================
1. POST /api/score/
=============================================================================

Score a healthcare transaction and detect fraud risk.

Request Body (JSON):
{
    "caseid": "CASE001",
    "age": 45,
    "wealth_idx": 2.5,
    "education": "High School",
    "residence": "Urban",
    "has_diabetes": true,
    "has_htn": false,
    "screening_count": 2,
    "told_high_gluc": true,
    "told_high_bp": false,
    "tx_diabetes": true,
    "tx_htn": false
}

Response (201 Created):
{
    "transaction_id": 1,
    "caseid": "CASE001",
    "final_risk": 0.523,
    "risk_tier": "high",
    "alert_id": 5,
    "scores": {
        "DVS": 0.5625,
        "TNS": 0.667,
        "ICS": 0.5,
        "CCS": 0.75,
        "HCFD": 0.012,
        "rule_score": 0.25,
        "anomaly_score": 0.401
    },
    "explanation": "Risk Assessment: High Risk\nFinal Risk Score: 0.523\n...",
    "rule_violations": ["R1: Young age with chronic condition treatment"]
}

Error Response (400 Bad Request):
{
    "error": "caseid is required"
}

Notes:
- Alert is automatically created if final_risk > 0.75
- All scores are clipped to 0-1 range
- Audit log entry created automatically
"""


"""
=============================================================================
2. GET /api/transactions/
=============================================================================

Retrieve paginated list of transactions with optional filtering.

Query Parameters:
- page: Page number (default: 1)
- page_size: Items per page (default: 20, max: 100)
- risk_tier: Filter by risk tier (low, medium, high, critical)
- min_risk: Filter by minimum final_risk (0-1)
- max_risk: Filter by maximum final_risk (0-1)
- search: Search by caseid (partial match, case-insensitive)

Examples:
GET /api/transactions/?page=1&page_size=20
GET /api/transactions/?risk_tier=high
GET /api/transactions/?min_risk=0.5&max_risk=1.0
GET /api/transactions/?search=CASE
GET /api/transactions/?risk_tier=critical&min_risk=0.75

Response (200 OK):
{
    "count": 150,
    "next": "http://api.example.com/api/transactions/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "caseid": "CASE001",
            "age": 45,
            "final_risk": 0.523,
            "risk_tier": "high",
            "created_at": "2026-06-24T10:30:00Z",
            "has_alerts": true
        },
        ...
    ]
}

Error Response (500 Internal Server Error):
{
    "error": "Error retrieving transactions"
}

Notes:
- Supports multiple filters in combination
- Results ordered by created_at descending (see Meta.ordering)
- Audit log entry created automatically
"""


"""
=============================================================================
3. GET /api/dashboard/stats/
=============================================================================

Retrieve dashboard statistics and fraud detection metrics.

Query Parameters: None

Response (200 OK):
{
    "total_transactions": 1250,
    "risk_tier_counts": {
        "low": 800,
        "medium": 300,
        "high": 100,
        "critical": 50
    },
    "average_risk": 0.342,
    "total_flagged": 150,
    "monthly_counts": [
        {
            "month": "2026-01",
            "count": 180
        },
        {
            "month": "2026-02",
            "count": 210
        },
        ...
    ],
    "top_risk_records": [
        {
            "id": 42,
            "caseid": "CASE042",
            "final_risk": 0.987,
            "risk_tier": "critical",
            "created_at": "2026-06-24T09:15:00Z"
        },
        ...
    ]
}

Error Response (500 Internal Server Error):
{
    "error": "Error retrieving statistics"
}

Notes:
- Monthly counts cover last 6 months
- Top risk records: top 5 by final_risk score
- total_flagged counts transactions with final_risk > 0.5
- Audit log entry created automatically
"""


"""
=============================================================================
4. GET /api/alerts/
=============================================================================

Retrieve list of unresolved alerts, ordered by risk severity.

Query Parameters: None

Response (200 OK):
{
    "count": 25,
    "alerts": [
        {
            "id": 5,
            "transaction_id": 1,
            "caseid": "CASE001",
            "risk_tier": "critical",
            "final_risk": 0.856,
            "message": "Critical fraud risk detected: 0.856",
            "created_at": "2026-06-24T10:30:00Z"
        },
        {
            "id": 4,
            "transaction_id": 2,
            "caseid": "CASE002",
            "risk_tier": "high",
            "final_risk": 0.623,
            "message": "Critical fraud risk detected: 0.623",
            "created_at": "2026-06-24T09:45:00Z"
        },
        ...
    ]
}

Error Response (500 Internal Server Error):
{
    "error": "Error retrieving alerts"
}

Notes:
- Only returns is_resolved=False alerts
- Ordered by final_risk descending
- Audit log entry created automatically
"""


"""
=============================================================================
5. PATCH /api/alerts/<id>/resolve/
=============================================================================

Mark an alert as resolved.

URL Parameter:
- id: Alert ID (integer)

Request Body: None (empty JSON object {} is acceptable)

Examples:
PATCH /api/alerts/5/resolve/
PATCH /api/alerts/10/resolve/

Response (200 OK):
{
    "id": 5,
    "is_resolved": true,
    "message": "Alert resolved successfully"
}

Error Response (404 Not Found):
{
    "error": "Alert not found"
}

Error Response (500 Internal Server Error):
{
    "error": "Error resolving alert"
}

Notes:
- Sets is_resolved=True
- Audit log entry created automatically
- Returns updated alert object
"""


"""
=============================================================================
6. POST /api/reports/generate/
=============================================================================

Generate PDF report with transaction statistics and fraud metrics.

Request Body (JSON):
{
    "report_type": "daily"
}

Report Types:
- "daily": Last 24 hours
- "weekly": Last 7 days
- "monthly": Last 30 days

Examples:
POST /api/reports/generate/
{
    "report_type": "daily"
}

POST /api/reports/generate/
{
    "report_type": "weekly"
}

POST /api/reports/generate/
{
    "report_type": "monthly"
}

Response (200 OK):
- Returns PDF file as attachment
- Content-Type: application/pdf
- Filename: fraud_detection_{report_type}_{YYYYMMDD}.pdf

Example Filenames:
- fraud_detection_daily_20260624.pdf
- fraud_detection_weekly_20260624.pdf
- fraud_detection_monthly_20260624.pdf

Error Response (400 Bad Request):
{
    "error": "Invalid report_type. Use: daily, weekly, monthly"
}

Error Response (500 Internal Server Error):
{
    "error": "Error generating report"
}

PDF Report Contents:
- Title with date range
- Summary Statistics:
  * Total Transactions
  * Average Risk Score
  * Critical Risk Count
  * High Risk Count
- Risk Tier Distribution:
  * Count and percentage for each tier
- Top Risk Records:
  * Top 10 transactions by final_risk
  * Includes Case ID, Risk Score, Risk Tier, Date

Notes:
- PDF uses reportlab library
- Audit log entry created automatically
- File is returned as downloadable attachment
"""


"""
=============================================================================
AUDIT LOGGING
=============================================================================

Every API request automatically creates an AuditLog entry with:
- action: Description of the action performed
- user: Username (or 'anonymous' if not authenticated)
- endpoint: API endpoint path
- ip_address: Client IP address (extracted from request)
- timestamp: Automatic timestamp (auto_now_add=True)

Audit Actions:
- SCORE_TRANSACTION: When /api/score/ endpoint is called
- ALERT_CREATED: When an alert is automatically created from critical risk
- LIST_TRANSACTIONS: When /api/transactions/ is called
- VIEW_DASHBOARD: When /api/dashboard/stats/ is called
- LIST_ALERTS: When /api/alerts/ is called
- RESOLVE_ALERT: When /api/alerts/<id>/resolve/ is called
- GENERATE_REPORT: When /api/reports/generate/ is called
"""


"""
=============================================================================
AUTHENTICATION & PERMISSIONS
=============================================================================

Current Status: No authentication/permission required for any endpoints
(modify as needed for your security requirements)

To add authentication, update views to inherit from appropriate DRF classes:
- from rest_framework.permissions import IsAuthenticated
- Add permission_classes = [IsAuthenticated] to view classes

For token authentication, add:
- from rest_framework.authentication import TokenAuthentication
- authentication_classes = [TokenAuthentication]
"""


"""
=============================================================================
EXAMPLE USAGE WITH CURL
=============================================================================

1. Score a Transaction:
curl -X POST http://localhost:8000/api/score/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "caseid": "CASE001",
    "age": 45,
    "wealth_idx": 2.5,
    "education": "High School",
    "residence": "Urban",
    "has_diabetes": true,
    "has_htn": false,
    "screening_count": 2,
    "told_high_gluc": true,
    "told_high_bp": false,
    "tx_diabetes": true,
    "tx_htn": false
  }'

2. Get Transactions (with filters):
curl "http://localhost:8000/api/transactions/?risk_tier=high&page_size=20"

3. Get Dashboard Stats:
curl http://localhost:8000/api/dashboard/stats/

4. Get Unresolved Alerts:
curl http://localhost:8000/api/alerts/

5. Resolve an Alert:
curl -X PATCH http://localhost:8000/api/alerts/5/resolve/

6. Generate Daily Report:
curl -X POST http://localhost:8000/api/reports/generate/ \\
  -H "Content-Type: application/json" \\
  -d '{"report_type": "daily"}' \\
  -o fraud_detection_daily.pdf
"""


"""
=============================================================================
INSTALLATION & CONFIGURATION
=============================================================================

1. Add to Django urls.py:
from django.urls import path, include

urlpatterns = [
    ...
    path('api/', include('api.urls')),
    ...
]

2. Ensure models are registered in Django admin (optional):
from models import Transaction, Alert, AuditLog

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('caseid', 'final_risk', 'risk_tier', 'created_at')
    list_filter = ('risk_tier', 'created_at')
    search_fields = ('caseid',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'final_risk', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'risk_tier', 'created_at')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'endpoint', 'timestamp')
    list_filter = ('action', 'user', 'timestamp')
    readonly_fields = ('timestamp',)

3. Run migrations:
python manage.py makemigrations
python manage.py migrate

4. Required packages in requirements.txt:
djangorestframework>=3.14.0
reportlab>=4.0.0
joblib>=1.3.0
"""
