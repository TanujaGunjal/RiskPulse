"""
Enhanced ML Ensemble for Healthcare Fraud Detection

Integrates:
- XGBoost Disease Risk Prediction
- Isolation Forest Anomaly Detection
- Autoencoder Anomaly Detection
- HCFD Rule-Based Scoring
- HCFD-XAI Explainability

This module DOES NOT store NFHS data.
NFHS is only used for model training (separate pipeline).
"""

import numpy as np
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = Path(__file__).parent
XGBOOST_MODEL = MODEL_DIR / "xgboost_disease_risk.pkl"
ISOLATION_FOREST_MODEL = MODEL_DIR / "isolation_forest.pkl"
AUTOENCODER_MODEL = MODEL_DIR / "autoencoder.h5"
SCALER_MODEL = MODEL_DIR / "scaler.pkl"


class MLEnsemble:
    """
    Unified ML Ensemble for fraud detection.
    
    Architecture:
        Input Features
            ↓
        ├─→ XGBoost Disease Risk Score
        ├─→ Isolation Forest Anomaly Score
        ├─→ Autoencoder Anomaly Score
        ├─→ HCFD Rule-Based Score
            ↓
        Weighted Ensemble
            ↓
        Final Risk Score (0-1)
        
    Weights:
        - XGBoost: 35% (disease risk)
        - Isolation Forest: 20% (statistical anomaly)
        - Autoencoder: 15% (deep anomaly)
        - HCFD Rules: 30% (medical validation)
    """
    
    def __init__(self):
        """Initialize ensemble, loading models if available."""
        self.xgboost_model = self._load_xgboost()
        self.isolation_forest = self._load_isolation_forest()
        self.autoencoder = self._load_autoencoder()
        self.scaler = self._load_scaler()
        
        self.weights = {
            'xgboost': 0.35,
            'isolation_forest': 0.20,
            'autoencoder': 0.15,
            'hcfd_rules': 0.30,
        }
    
    def _load_xgboost(self):
        """Load XGBoost disease risk model."""
        try:
            import joblib
            if XGBOOST_MODEL.exists():
                model = joblib.load(XGBOOST_MODEL)
                logger.info(f"✅ XGBoost model loaded from {XGBOOST_MODEL}")
                return model
        except Exception as e:
            logger.warning(f"⚠️ Failed to load XGBoost model: {e}")
        return None
    
    def _load_isolation_forest(self):
        """Load Isolation Forest anomaly detection model."""
        try:
            import joblib
            if ISOLATION_FOREST_MODEL.exists():
                model = joblib.load(ISOLATION_FOREST_MODEL)
                logger.info(f"✅ Isolation Forest model loaded")
                return model
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Isolation Forest: {e}")
        return None
    
    def _load_autoencoder(self):
        """Load Autoencoder anomaly detection model."""
        try:
            import tensorflow as tf
            if AUTOENCODER_MODEL.exists():
                model = tf.keras.models.load_model(AUTOENCODER_MODEL)
                logger.info(f"✅ Autoencoder model loaded")
                return model
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Autoencoder: {e}")
        return None
    
    def _load_scaler(self):
        """Load feature scaler for normalization."""
        try:
            import joblib
            if SCALER_MODEL.exists():
                scaler = joblib.load(SCALER_MODEL)
                logger.info(f"✅ Feature scaler loaded")
                return scaler
        except Exception as e:
            logger.warning(f"⚠️ Failed to load scaler: {e}")
        return None
    
    def _extract_features(self, transaction_data):
        """
        Extract feature vector from transaction data.
        
        Features:
            age, wealth_idx, has_diabetes, has_htn,
            told_high_gluc, told_high_bp,
            tx_diabetes, tx_htn, screening_count
        """
        features = np.array([
            transaction_data.get('age', 0),
            transaction_data.get('wealth_idx', 2.5),
            int(transaction_data.get('has_diabetes', False)),
            int(transaction_data.get('has_htn', False)),
            int(transaction_data.get('told_high_gluc', False)),
            int(transaction_data.get('told_high_bp', False)),
            int(transaction_data.get('tx_diabetes', False)),
            int(transaction_data.get('tx_htn', False)),
            transaction_data.get('screening_count', 0),
        ], dtype=np.float32)
        return features
    
    def get_xgboost_score(self, features):
        """Get disease risk score from XGBoost model."""
        if self.xgboost_model is None:
            logger.warning("XGBoost model unavailable, returning 0.0")
            return 0.0, {}
        
        try:
            # Ensure features are in correct shape
            features_reshaped = features.reshape(1, -1)
            
            # Get prediction probability
            prob = self.xgboost_model.predict_proba(features_reshaped)[0]
            risk_score = float(prob[1])  # Probability of high risk
            
            logger.debug(f"XGBoost disease risk: {risk_score:.4f}")
            
            return risk_score, {
                'model': 'XGBoost',
                'score': risk_score,
                'confidence': float(max(prob)),
            }
        except Exception as e:
            logger.error(f"XGBoost prediction error: {e}")
            return 0.0, {}
    
    def get_isolation_forest_score(self, features):
        """Get anomaly score from Isolation Forest."""
        if self.isolation_forest is None:
            logger.warning("Isolation Forest unavailable, returning 0.0")
            return 0.0, {}
        
        try:
            if self.scaler:
                features_scaled = self.scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Get anomaly score (-1 for anomalies, 1 for normal)
            anomaly_label = self.isolation_forest.predict(features_scaled)[0]
            
            # Convert to probability (0-1)
            anomaly_score = 0.0 if anomaly_label == 1 else 1.0
            
            logger.debug(f"Isolation Forest anomaly: {anomaly_score:.4f}")
            
            return anomaly_score, {
                'model': 'Isolation Forest',
                'score': anomaly_score,
                'is_anomaly': anomaly_label == -1,
            }
        except Exception as e:
            logger.error(f"Isolation Forest error: {e}")
            return 0.0, {}
    
    def get_autoencoder_score(self, features):
        """Get reconstruction error from Autoencoder."""
        if self.autoencoder is None:
            logger.warning("Autoencoder unavailable, returning 0.0")
            return 0.0, {}
        
        try:
            if self.scaler:
                features_scaled = self.scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            # Get reconstruction error
            reconstruction = self.autoencoder.predict(features_scaled)
            reconstruction_error = float(np.mean(np.abs(features_scaled - reconstruction)))
            
            # Normalize to 0-1 scale (threshold at 0.5)
            anomaly_score = min(reconstruction_error / 0.5, 1.0)
            
            logger.debug(f"Autoencoder reconstruction error: {reconstruction_error:.4f}")
            
            return anomaly_score, {
                'model': 'Autoencoder',
                'reconstruction_error': reconstruction_error,
                'score': anomaly_score,
            }
        except Exception as e:
            logger.error(f"Autoencoder error: {e}")
            return 0.0, {}
    
    def get_hcfd_score(self, transaction_data):
        """Get HCFD rule-based fraud detection score."""
        # Medical inconsistency checks
        score = 0.0
        violations = []
        
        has_diabetes = transaction_data.get('has_diabetes', False)
        has_htn = transaction_data.get('has_htn', False)
        told_high_gluc = transaction_data.get('told_high_gluc', False)
        told_high_bp = transaction_data.get('told_high_bp', False)
        tx_diabetes = transaction_data.get('tx_diabetes', False)
        tx_htn = transaction_data.get('tx_htn', False)
        age = transaction_data.get('age', 0)
        
        # Rule 1: Patient reports high glucose but no diabetes diagnosis
        if told_high_gluc and not has_diabetes:
            score += 0.2
            violations.append("R1: High glucose without diabetes diagnosis")
        
        # Rule 2: Patient reports high BP but no HTN diagnosis
        if told_high_bp and not has_htn:
            score += 0.2
            violations.append("R2: High BP without hypertension diagnosis")
        
        # Rule 3: Has diagnosis but not in treatment
        if has_diabetes and not tx_diabetes:
            score += 0.15
            violations.append("R3: Diabetes diagnosis without treatment")
        
        if has_htn and not tx_htn:
            score += 0.15
            violations.append("R3: Hypertension diagnosis without treatment")
        
        # Rule 4: Young age with multiple chronic conditions unlikely
        if age < 30 and (has_diabetes and has_htn):
            score += 0.1
            violations.append("R4: Young age with multiple chronic conditions")
        
        # Normalize to 0-1
        hcfd_score = min(score, 1.0)
        
        logger.debug(f"HCFD score: {hcfd_score:.4f}, violations: {len(violations)}")
        
        return hcfd_score, {
            'model': 'HCFD Rules',
            'score': hcfd_score,
            'violations': violations,
        }
    
    def compute_final_risk(self, transaction_data):
        """
        Compute final risk using ensemble of all models.
        
        Returns:
            dict: {
                'final_risk': 0.0-1.0,
                'risk_tier': 'low'/'medium'/'high'/'critical',
                'scores': {
                    'xgboost': score,
                    'isolation_forest': score,
                    'autoencoder': score,
                    'hcfd': score,
                },
                'explanations': [list of contributing factors],
                'feature_importance': {feature: importance},
                'model_versions': {model: version},
            }
        """
        
        # Extract features
        features = self._extract_features(transaction_data)
        
        # Get individual model scores
        xgb_score, xgb_info = self.get_xgboost_score(features)
        iso_forest_score, iso_info = self.get_isolation_forest_score(features)
        autoencoder_score, auto_info = self.get_autoencoder_score(features)
        hcfd_score, hcfd_info = self.get_hcfd_score(transaction_data)
        
        # Weighted ensemble
        final_risk = (
            self.weights['xgboost'] * xgb_score +
            self.weights['isolation_forest'] * iso_forest_score +
            self.weights['autoencoder'] * autoencoder_score +
            self.weights['hcfd_rules'] * hcfd_score
        )
        
        # Clip to 0-1
        final_risk = float(np.clip(final_risk, 0.0, 1.0))
        
        # Determine risk tier
        if final_risk < 0.25:
            risk_tier = 'low'
        elif final_risk < 0.50:
            risk_tier = 'medium'
        elif final_risk < 0.75:
            risk_tier = 'high'
        else:
            risk_tier = 'critical'
        
        # Build explanations
        explanations = []
        if xgb_score > 0.5:
            explanations.append(f"Disease risk detected by XGBoost ({xgb_score:.2%})")
        if iso_forest_score > 0.5:
            explanations.append(f"Statistical anomaly detected ({iso_forest_score:.2%})")
        if autoencoder_score > 0.5:
            explanations.append(f"Deep learning anomaly detected ({autoencoder_score:.2%})")
        if hcfd_info.get('violations'):
            explanations.extend(hcfd_info['violations'])
        
        if not explanations:
            explanations = ["No significant fraud indicators detected"]
        
        return {
            'final_risk': final_risk,
            'risk_tier': risk_tier,
            'scores': {
                'xgboost': float(xgb_score),
                'isolation_forest': float(iso_forest_score),
                'autoencoder': float(autoencoder_score),
                'hcfd': float(hcfd_score),
            },
            'explanations': explanations,
            'violations': hcfd_info.get('violations', []),
            'feature_importance': {
                'xgboost': xgb_info,
                'isolation_forest': iso_info,
                'autoencoder': auto_info,
                'hcfd': hcfd_info,
            },
            'model_versions': {
                'xgboost': '1.0.0' if self.xgboost_model else 'unavailable',
                'isolation_forest': '1.0.0' if self.isolation_forest else 'unavailable',
                'autoencoder': '1.0.0' if self.autoencoder else 'unavailable',
                'hcfd': '1.0.0',
            },
        }


# Global ensemble instance
_ensemble = None

def get_ensemble():
    """Get or create the ML ensemble."""
    global _ensemble
    if _ensemble is None:
        _ensemble = MLEnsemble()
    return _ensemble
