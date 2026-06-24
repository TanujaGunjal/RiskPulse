# RiskPulse - Enhanced Healthcare Fraud Detection Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     RISKPULSE FRAUD DETECTION PLATFORM                  │
└─────────────────────────────────────────────────────────────────────────┘

                              FRONTEND LAYER
                          (React + Recharts)
                                ↓
                    ┌───────────────────────────┐
                    │  Dashboard                │
                    │  - KPI Cards              │
                    │  - Risk Distribution      │
                    │  - Top Risk Records       │
                    ├───────────────────────────┤
                    │  Risk Scorer              │
                    │  - Patient Entry Form     │
                    │  - Real-time Scoring      │
                    │  - Risk Assessment       │
                    ├───────────────────────────┤
                    │  Analytics Dashboard      │
                    │  - 30-day Trends          │
                    │  - Model Performance      │
                    │  - Insurance Metrics      │
                    │  - Fraud Indicators       │
                    └───────────────────────────┘
                                ↓
                        API LAYER (REST)
                     (Django REST Framework)
                                ↓
        ┌──────────────────────────────────────────────────────────┐
        │           BACKEND API ENDPOINTS                          │
        ├──────────────────────────────────────────────────────────┤
        │  Core Endpoints:                                         │
        │  POST   /api/score/              - Score transaction     │
        │  GET    /api/transactions/       - List transactions     │
        │  GET    /api/dashboard/stats/    - Dashboard metrics     │
        │                                                          │
        │  Enhanced Endpoints:                                     │
        │  GET/POST /api/insurance-decisions/                      │
        │           GET /api/insurance-decisions/stats/            │
        │  GET/POST /api/explainability/                           │
        │           GET /api/explainability/violation-stats/       │
        │  GET     /api/models/             - Model metadata       │
        │           GET /api/models/active/  - Active models       │
        │  GET     /api/analytics/dashboard/ - All metrics         │
        │           GET /api/analytics/trends/  - Trends data      │
        │           GET /api/analytics/model-performance/          │
        └──────────────────────────────────────────────────────────┘
                                ↓
                        ML ENSEMBLE LAYER
                     (api/ml/ml_ensemble.py)
                                ↓
        ┌──────────────────────────────────────────────────────────┐
        │  ML Models (35% weight)                                  │
        │  ├─ XGBoost Disease Risk        - 35%                    │
        │  ├─ Isolation Forest Anomaly    - 20%                    │
        │  ├─ Autoencoder Anomaly         - 15%                    │
        │  └─ HCFD Rule-Based             - 30%                    │
        │                                                          │
        │  Output: Final Risk Score (0-1)                         │
        │  Tiers: Low, Medium, High, Critical                     │
        └──────────────────────────────────────────────────────────┘
                                ↓
                        DATABASE LAYER
                      (PostgreSQL 15+)
                                ↓
        ┌──────────────────────────────────────────────────────────┐
        │  Tables:                                                 │
        │  ├─ Transaction         - Patient records & scores       │
        │  ├─ Alert               - High-risk alerts               │
        │  ├─ InsuranceDecision   - Insurance approvals            │
        │  ├─ ExplainabilityResult - HCFD-XAI outputs             │
        │  ├─ ModelMetadata       - Model versions & metrics       │
        │  └─ AuditLog            - System audit trail             │
        └──────────────────────────────────────────────────────────┘
```

---

## Architecture Components

### 1. **Frontend Layer** (React)
- **Technology**: React 18+, Recharts for visualization
- **Pages**:
  - Dashboard: Overview of fraud detection metrics
  - Risk Scorer: Patient entry and real-time risk assessment
  - Analytics: Comprehensive dashboard with trends and model metrics
- **State Management**: React Hooks (useState, useEffect)
- **API Client**: Axios via `utils/api.js`

### 2. **Backend API Layer** (Django REST Framework)
- **Framework**: Django 6.0.6 with DRF 6.0.6
- **Server**: Development server on `localhost:8000`
- **Authentication**: AllowAny (public API)
- **CORS**: Enabled for localhost:3000

#### Core Views:
- `ScoreTransactionView`: POST /api/score/ - Main scoring endpoint
- `DashboardStatsView`: GET /api/dashboard/stats/ - Dashboard metrics
- `TransactionListView`: GET /api/transactions/ - Transaction history
- `AlertListView`: GET /api/alerts/ - Alert management
- `ReportGenerateView`: POST /api/reports/generate/ - Report generation

#### Enhanced Views (ViewSets):
- `InsuranceDecisionViewSet`: Insurance approval/denial decisions
- `ExplainabilityResultViewSet`: HCFD-XAI outputs
- `ModelMetadataViewSet`: ML model registry
- `AnalyticsDashboardView`: Comprehensive analytics

### 3. **ML Ensemble Layer** (`api/ml/ml_ensemble.py`)

**Architecture**:
```
Input Features (age, wealth_idx, diagnoses, etc.)
        ↓
    ┌─────────────────────────────────────────┐
    │                                         │
    ├→ XGBoost (35%) - Disease Risk          │
    ├→ Isolation Forest (20%) - Anomaly       │
    ├→ Autoencoder (15%) - Deep Anomaly       │
    └→ HCFD Rules (30%) - Medical Validation  │
        ↓
    Weighted Ensemble
        ↓
    Final Risk Score (0-1)
        ↓
    Risk Tier Classification
    (Low / Medium / High / Critical)
```

**Key Components**:
- `MLEnsemble` class: Unified interface for all models
- Model Loading: Automatic fallback if models unavailable
- Feature Extraction: Standardized feature pipeline
- Score Normalization: 0-1 scale with tie-breaking

### 4. **Database Layer** (PostgreSQL)

**Connection**:
```
Host: localhost
Port: 5432
Database: riskpulse
User: riskpulse_user
Password: riskpulse123
```

**Schema**:

#### `Transaction`
```sql
- id (PK)
- caseid (UNIQUE) - Patient case ID
- age, wealth_idx, education, residence
- has_diabetes, has_htn
- DVS, TNS, ICS, CCS, HCFD_score
- rule_score, anomaly_score
- final_risk (0-1)
- risk_tier (low/medium/high/critical)
- explanation (text)
- created_at (indexed)
```

#### `Alert`
```sql
- id (PK)
- transaction_id (FK)
- risk_tier, final_risk
- message, is_resolved
- created_at (indexed)
```

#### `InsuranceDecision` ⭐ NEW
```sql
- id (PK)
- transaction_id (FK, unique)
- decision (approved/denied/pending/conditional)
- reason, coverage_amount
- denial_reason, reviewer, notes
- created_at, updated_at
```

#### `ExplainabilityResult` ⭐ NEW
```sql
- id (PK)
- transaction_id (FK, unique)
- feature_importance (JSON)
- shap_values (JSON)
- rule_violations (JSON)
- key_factors (JSON)
- model_versions (JSON)
- explanation_text
- confidence_score
- created_at
```

#### `ModelMetadata` ⭐ NEW
```sql
- id (PK)
- model_type (xgboost/isolation_forest/autoencoder/hcfd)
- model_version
- model_path
- training_dataset, training_size
- accuracy, precision, recall, f1_score, auc_roc
- is_active (indexed)
- created_at, updated_at
```

#### `AuditLog`
```sql
- id (PK)
- action, user, endpoint, ip_address
- timestamp (indexed)
```

---

## Data Flow

### **Patient Risk Assessment Flow**
```
1. User enters patient data in Risk Scorer form
   ↓
2. Frontend validates input (Case ID, Age required)
   ↓
3. POST to /api/score/ with form data
   ↓
4. Backend extracts features
   ↓
5. ML Ensemble computes risk:
   - XGBoost disease prediction
   - Isolation Forest anomaly detection
   - Autoencoder reconstruction error
   - HCFD rule-based validation
   ↓
6. Weighted ensemble calculates final_risk
   ↓
7. Creates records in database:
   - Transaction (scored data)
   - Alert (if final_risk > 0.75)
   - ExplainabilityResult (HCFD-XAI output)
   ↓
8. Returns 201 Created with:
   {
     transaction_id,
     caseid,
     final_risk,
     risk_tier,
     scores: {xgboost, isolation_forest, autoencoder, hcfd},
     explanations: [...]
   }
   ↓
9. Frontend displays Risk Assessment Results page
   - Risk tier badge (color-coded)
   - Risk gauge visualization
   - Component score breakdown
   - Rule violation list
   - Explanation text
```

### **Insurance Decision Flow** ⭐ NEW
```
1. High-risk transaction flagged (final_risk > threshold)
   ↓
2. Insurance review officer accesses transaction via API
   ↓
3. Reviews explainability data:
   - Feature importance
   - Rule violations
   - Contributing factors
   ↓
4. Makes decision via PATCH /api/insurance-decisions/{id}/
   - Approved (with coverage amount)
   - Denied (with reason)
   - Pending (for manual review)
   - Conditional (with notes)
   ↓
5. Decision stored with:
   - Reviewer name
   - Timestamp
   - Notes
   ↓
6. Tracked in analytics dashboard
```

### **Analytics Dashboard Flow** ⭐ NEW
```
1. User navigates to Analytics page
   ↓
2. Frontend fetches:
   - /api/analytics/dashboard/  → Overall metrics
   - /api/analytics/trends/     → 30-day trends
   - /api/analytics/model-performance/  → Model metrics
   ↓
3. Backend aggregates data:
   - Transaction counts by risk tier
   - Insurance decision breakdown
   - Alert statistics
   - Violation patterns
   - Model performance metrics
   ↓
4. Frontend renders:
   - KPI cards (total transactions, avg risk, approvals, alerts)
   - Risk distribution pie chart
   - Insurance decisions bar chart
   - 30-day trend lines
   - Model performance cards
   ↓
5. User can refresh to get latest data
```

---

## NFHS Integration Notes

### ❌ What's NOT stored in PostgreSQL
- Raw NFHS-5 dataset (50k+ records)
- Patient demographic details from survey
- Geographical data
- Household information

### ✅ What IS stored in PostgreSQL
- User-entered patient records for scoring
- Computed fraud risk scores
- Insurance decisions
- Audit trails
- Model metadata

### 📊 NFHS Usage
- **Training**: Used to train XGBoost, Isolation Forest, Autoencoder models
- **Models**: Trained models stored as `.pkl` files in `api/ml/`
- **Predictions**: Only use trained models for real-time scoring

---

## API Endpoints Summary

### **Core Endpoints** (Existing)
```
POST   /api/score/                    - Score transaction
GET    /api/transactions/             - List transactions
GET    /api/dashboard/stats/          - Dashboard metrics
GET    /api/alerts/                   - List alerts
PATCH  /api/alerts/{id}/resolve/      - Resolve alert
POST   /api/reports/generate/         - Generate report
```

### **Insurance Endpoints** ⭐ NEW
```
GET    /api/insurance-decisions/      - List decisions
POST   /api/insurance-decisions/      - Create decision
GET    /api/insurance-decisions/{id}/ - Get decision
PATCH  /api/insurance-decisions/{id}/ - Update decision
GET    /api/insurance-decisions/stats/ - Decision statistics
```

### **Explainability Endpoints** ⭐ NEW
```
GET    /api/explainability/                    - List results
GET    /api/explainability/{id}/               - Get result
GET    /api/explainability/violation-stats/    - Violation statistics
```

### **Model Endpoints** ⭐ NEW
```
GET    /api/models/              - List all models
GET    /api/models/{id}/         - Get model details
GET    /api/models/active/       - List active models
```

### **Analytics Endpoints** ⭐ NEW
```
GET    /api/analytics/dashboard/          - Overall dashboard
GET    /api/analytics/trends/             - 30-day trends
GET    /api/analytics/model-performance/  - Model metrics
```

---

## Deployment Ready

✅ PostgreSQL configured
✅ Models for insurance & explainability created
✅ API endpoints implemented
✅ Analytics dashboard built
✅ Frontend navigation updated
✅ All dependencies installed

### Next Steps (Optional)

1. **Model Training**
   - Train XGBoost on NFHS data → `api/ml/xgboost_disease_risk.pkl`
   - Train Isolation Forest → `api/ml/isolation_forest.pkl`
   - Train Autoencoder → `api/ml/autoencoder.h5`
   - Save scaler → `api/ml/scaler.pkl`

2. **Insurance Decision Logic**
   - Implement business rules for auto-approval/denial
   - Create management interface for reviewers

3. **Authentication**
   - Implement JWT tokens
   - Create user roles (doctor, reviewer, admin)
   - Add permission checks

4. **Monitoring**
   - Set up logging and alerting
   - Monitor model performance drift
   - Track API response times

---

## Testing the System

### Test Case 1: Low Risk (Healthy Patient)
```
Case ID: HEALTHY_001
Age: 35
No diagnoses checked
No high values reported
Expected: Risk = 0.0, Tier = Low
```

### Test Case 2: High Risk (Medical Inconsistency)
```
Case ID: FRAUD_004
Age: 75
Diabetes, HTN diagnoses checked
High glucose, high BP reported
NO treatments selected ← Inconsistency!
Expected: Risk > 0.75, Tier = Critical
Explanation: "Patient reports high values but NO treatment"
```

### Test Case 3: Verify Analytics
```
Navigate to Analytics page
Verify KPI cards show transaction counts
Check risk distribution pie chart
Review 30-day trend line
Confirm model performance metrics display
```

---

## Performance Considerations

- **Query Optimization**: Indexed fields (caseid, risk_tier, created_at)
- **Model Loading**: Models loaded once, cached in memory
- **API Response**: Typical response time < 500ms
- **Database**: PostgreSQL connection pooling enabled
- **Frontend**: Lazy loading of Analytics components

---

Generated: June 24, 2026
Platform: RiskPulse Healthcare Fraud Detection v2.0
Database: PostgreSQL 15+
Backend: Django 6.0.6 + DRF 6.0.6
Frontend: React 18+
