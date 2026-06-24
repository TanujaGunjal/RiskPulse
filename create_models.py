"""Generate mock ML model artifacts for fraud detection scoring."""

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# Create api/ml directory if not exists
ml_dir = Path('api/ml')
ml_dir.mkdir(parents=True, exist_ok=True)

# Generate dummy training data (9 features as per scorer.py)
# Features: age, wealth_idx, screening_count, has_diabetes, has_htn, 
#           told_high_gluc, told_high_bp, tx_diabetes, tx_htn
X_train = np.random.randn(100, 9)
y_train = np.random.randint(0, 2, 100)

# Create and fit Isolation Forest
iso_forest = IsolationForest(random_state=42, contamination=0.1)
iso_forest.fit(X_train)
joblib.dump(iso_forest, ml_dir / 'isolation_forest.pkl')
print('✅ Created isolation_forest.pkl')

# Create and fit Random Forest
rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
rf_model.fit(X_train, y_train)
joblib.dump(rf_model, ml_dir / 'random_forest.pkl')
print('✅ Created random_forest.pkl')

# Create and fit StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)
joblib.dump(scaler, ml_dir / 'scaler.pkl')
print('✅ Created scaler.pkl')

print(f'\n✅ All models saved to {ml_dir}')
print(f'Files created:')
print(f'  - {ml_dir / "isolation_forest.pkl"}')
print(f'  - {ml_dir / "random_forest.pkl"}')
print(f'  - {ml_dir / "scaler.pkl"}')
