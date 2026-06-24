# RiskPulse - Healthcare Fraud Detection Platform

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Django 4.2+](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/)
[![React 18+](https://img.shields.io/badge/React-18%2B-61DAFB?logo=react)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A sophisticated healthcare fraud detection platform combining machine learning anomaly detection with explainable risk scoring and insurance decision management.

## 🎯 Key Features

### Fraud Detection Engine
- **7-Component Weighted Ensemble Scoring**: Combines demographic, medical, testing, and anomaly detection signals
- **Anomaly Detection**: Isolation Forest + Random Forest ensemble for sophisticated outlier detection
- **Rule-Based Validation**: Medical inconsistency detection with 4 rule types (R1-R4)
- **Explainability**: Full transparency into scoring decisions with feature importance and key factors

### Risk Tiers
- 🟢 **Low** (<0.25): Standard processing
- 🟡 **Medium** (0.25-0.50): Enhanced review
- 🟠 **High** (0.50-0.75): Escalated investigation
- 🔴 **Critical** (≥0.75): Immediate action required

### Core Modules

#### Backend (Django REST Framework)
- Transaction scoring with real-time risk assessment
- Transaction history and filtering
- Alert management and resolution tracking
- Explainability result storage and retrieval
- Insurance decision documentation
- Comprehensive analytics and reporting
- Model metadata and performance tracking

#### Frontend (React)
- **Dashboard**: Real-time overview of fraud metrics
- **Risk Scorer**: Interactive transaction scoring interface
- **Transactions**: Search, filter, and analyze transaction records
- **Alerts**: Manage high-risk transaction alerts
- **Reports**: Generate daily/weekly/monthly PDF reports
- **Analytics**: Comprehensive metrics and trend analysis

## 🏗️ Architecture

### Scoring Pipeline
```
Input Transaction
    ↓
Feature Extraction & Normalization
    ↓
┌─────────────────────────────────────┐
│  7-Component Scoring Engine         │
├─────────────────────────────────────┤
│ 1. DVS: Demographic Variability     │
│ 2. TNS: Testing Normalization       │
│ 3. ICS: Income/Wealth Clipping      │
│ 4. CCS: Consistency Checks          │
│ 5. HCFD: Healthcare Fraud Index     │
│ 6. Rule Score: Medical Rules        │
│ 7. Anomaly Score: ML Ensemble       │
└─────────────────────────────────────┘
    ↓
Risk Score Calculation (0-1)
    ↓
Risk Tier Assignment
    ↓
Explainability Generation
    ↓
Insurance Decision
    ↓
Database Persistence
```

### ML Models
- **Isolation Forest**: Detects anomalies in feature space (contamination: 10%)
- **Random Forest Classifier**: Binary fraud/legitimate classification
- **StandardScaler**: Feature normalization for model input

## 📊 Database Schema

### Core Tables
- **Transaction**: Case IDs, demographics, medical history, risk scores
- **ExplainabilityResult**: Feature importance, rule violations, confidence scores
- **InsuranceDecision**: Decision status, risk-aware reasoning, audit trails
- **Alert**: High-risk transaction notifications with resolution tracking
- **AuditLog**: Complete system activity tracking

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 16+
- PostgreSQL 12+ (or SQLite for development)
- pip, npm

### Backend Setup

```bash
# Navigate to project root
cd d:\riskpulse

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Generate ML models (development)
python create_models.py

# Start Django development server
python manage.py runserver
```

Server runs at: `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

Frontend runs at: `http://localhost:3000`

## 📡 API Endpoints

### Scoring
- `POST /api/score/` - Score a new transaction

### Transactions
- `GET /api/transactions/` - List transactions (supports filtering)
  - Query params: `search`, `risk_tier`, `min_risk`, `max_risk`, `page`, `page_size`

### Alerts
- `GET /api/alerts/` - List unresolved alerts
- `PATCH /api/alerts/{id}/resolve/` - Resolve an alert

### Analytics
- `GET /api/analytics/dashboard/` - Dashboard metrics
- `GET /api/analytics/trends/` - 30-day trends (param: `days`)
- `GET /api/analytics/model_performance/` - Model performance metrics

### Reporting
- `POST /api/reports/generate/` - Generate PDF report
  - Body: `{ "report_type": "daily|weekly|monthly" }`

### Explainability
- `GET /api/explainability/` - List scoring explanations
- `GET /api/explainability/{id}/` - Detailed explanation

### Insurance Decisions
- `GET /api/insurance-decisions/` - List insurance decisions
- `PATCH /api/insurance-decisions/{id}/mark_pending/` - Update decision status

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api
```

### Manual Testing via Browser
1. Navigate to `http://localhost:3000`
2. Use Dashboard to view system status
3. Use Risk Scorer to score sample transactions
4. Navigate through Transactions, Alerts, Reports, Analytics pages

### API Testing
```bash
# Test scoring endpoint
curl -X POST http://localhost:8000/api/score/ \
  -H "Content-Type: application/json" \
  -d '{"caseid": "TEST001", "age": 45, ...}'

# Test transactions list
curl http://localhost:8000/api/transactions/

# Test analytics
curl http://localhost:8000/api/analytics/dashboard/
```

## 📁 Project Structure

```
riskpulse/
├── api/                              # Django app
│   ├── models.py                    # Database models
│   ├── views.py                     # Core endpoints
│   ├── views_enhanced.py            # Extended endpoints
│   ├── serializers.py               # DRF serializers
│   ├── ml/                          # ML modules
│   │   ├── scorer.py               # Scoring logic
│   │   ├── ml_ensemble.py          # Ensemble models
│   │   └── models/                 # Trained models (pkl files)
│   └── migrations/                  # Database migrations
├── frontend/                        # React application
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── Dashboard/
│   │   │   ├── RiskScorer/
│   │   │   ├── Transactions/
│   │   │   ├── Alerts/
│   │   │   ├── Reports/
│   │   │   └── Analytics/
│   │   ├── utils/
│   │   │   └── api.js              # API client
│   │   └── App.jsx                  # Main component
│   └── package.json
├── riskpulse_project/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=sqlite:///db.sqlite3
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/dbname

# ML Model Configuration
ISOLATION_FOREST_CONTAMINATION=0.1
RANDOM_FOREST_N_ESTIMATORS=10
```

### Django Settings
Key settings in `riskpulse_project/settings.py`:
- CORS enabled for frontend development
- REST Framework authentication and permissions
- File upload paths for reports
- ML model caching

## 📈 Scoring Algorithm Details

### Component Scores

1. **DVS (Demographic Variability Score)**
   - Formula: `age / 80`
   - Range: 0-1
   - Captures age-based risk

2. **TNS (Testing/Screening Normalization)**
   - Formula: `screening_count / 3`
   - Range: 0-1
   - Measures testing frequency

3. **ICS (Income/Wealth Clipping)**
   - Formula: `wealth_index / 5`
   - Range: 0-1
   - Normalizes economic indicators

4. **CCS (Consistency Checks)**
   - Compares medical history alignment
   - Range: 0-1
   - Higher = more consistent

5. **HCFD (Healthcare Fraud Detection Index)**
   - Composite: `(DVS + TNS + ICS) * CCS / 3`
   - Foundation for fraud assessment

6. **Rule Score**
   - Detects medical rule violations (R1-R4)
   - Normalized: 0-1
   - Weight: 35% in final risk

7. **Anomaly Score**
   - Isolation Forest + Random Forest ensemble average
   - Weight: 30% in final risk

### Final Risk Score
```
Final Risk = 0.35 * rule_score + 0.30 * anomaly_score + 0.25 * HCFD + 0.10 * (1 - CCS)
Risk = Clip(Risk, 0, 1)  # Ensure 0-1 range
```

## 🔐 Security

- CORS configured for frontend only
- CSRF protection enabled
- SQL injection prevention via ORM
- XSS protection via template escaping
- SQL Injection prevention through parameterized queries
- HTTPS ready (configure in production)

**Note**: This is a development setup. For production:
- Use strong SECRET_KEY
- Set DEBUG=False
- Use environment-specific settings
- Enable HTTPS
- Implement proper authentication
- Use PostgreSQL instead of SQLite
- Set up rate limiting

## 📝 ML Models

### Model Training
Models are pre-trained and serialized as pickle files:
- `api/ml/isolation_forest.pkl` - Anomaly detection model
- `api/ml/random_forest.pkl` - Fraud classification model
- `api/ml/scaler.pkl` - Feature scaling/normalization

To retrain models:
```bash
python create_models.py
```

**Note**: Current models are trained on synthetic data for development. For production:
- Prepare labeled fraud/non-fraud dataset
- Perform feature engineering on actual data
- Implement proper train/test validation
- Monitor model drift and performance
- Implement model versioning

## 📊 Analytics

### Dashboard Metrics
- Total transaction count
- Risk score distribution (low/medium/high/critical)
- Average risk score
- Open/resolved alerts count
- Insurance decision breakdown
- Rule violation statistics

### Trends
- Daily transaction counts
- High-risk transaction trends
- Insurance decision trends
- 30-day historical data

### Model Performance
- Accuracy, precision, recall
- F1 score, AUC-ROC
- Model version and update timestamp

## 🐛 Troubleshooting

### Backend Issues

**Error: "ModuleNotFoundError: No module named 'api'"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check PYTHONPATH includes project root

**Error: "Django has not been configured"**
- Ensure `manage.py` is in current directory
- Run `python manage.py check` for diagnosis

**Error: "ML models not found"**
- Run `python create_models.py` to generate models
- Check `api/ml/` directory for `.pkl` files

### Frontend Issues

**Error: "Cannot GET /api/***"**
- Ensure Django backend is running on port 8000
- Check CORS settings in Django
- Verify API_BASE_URL in `frontend/src/utils/api.js`

**Error: "Failed to compile"**
- Clear node_modules: `rm -rf node_modules`
- Reinstall: `npm install`
- Restart dev server: `npm start`

### Database Issues

**Error: "database is locked"**
- Close any open database connections
- Delete `db.sqlite3` and run migrations again (development only)
- Use PostgreSQL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation in code comments

## 🎓 Educational Notes

This platform was developed as a demonstration of:
- Full-stack machine learning integration
- Django REST Framework best practices
- React component architecture
- Explainable AI implementation
- Healthcare data handling (HIPAA considerations for production)
- Real-time analytics and reporting

## 🗺️ Roadmap

### Phase 3 (Planned)
- [ ] User authentication and multi-user support
- [ ] Role-based access control (RBAC)
- [ ] Advanced filtering and export capabilities
- [ ] Real-time notifications
- [ ] Mobile app version

### Phase 4 (Planned)
- [ ] Integration with healthcare systems (HL7, FHIR)
- [ ] Advanced ML models (XGBoost, Deep Learning)
- [ ] Automated retraining pipeline
- [ ] Fraud case management system
- [ ] Integration with claims processing

## 📚 References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Explainable AI Best Practices](https://christophm.github.io/interpretable-ml-book/)

---

**Last Updated**: June 24, 2026  
**Version**: 1.0.0  
**Status**: Beta - Ready for testing and feedback
