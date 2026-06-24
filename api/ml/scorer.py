"""
Healthcare Fraud Detection Scorer Module

This module loads pre-trained machine learning models and scoring artifacts,
then provides functions to compute fraud risk scores and risk tiers.
"""

import os
import numpy as np
import joblib
import logging
from typing import Dict, Tuple, Any
from pathlib import Path


logger = logging.getLogger(__name__)


# Model file paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR

ISOLATION_FOREST_PATH = MODEL_DIR / "isolation_forest.pkl"
RANDOM_FOREST_PATH = MODEL_DIR / "random_forest.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"


# Risk tier thresholds
RISK_THRESHOLDS = {
    'low': 0.25,
    'medium': 0.50,
    'high': 0.75,
}


# Load models at module startup
try:
    isolation_forest = joblib.load(ISOLATION_FOREST_PATH)
    logger.info(f"Loaded Isolation Forest model from {ISOLATION_FOREST_PATH}")
except FileNotFoundError:
    logger.warning(f"Isolation Forest model not found at {ISOLATION_FOREST_PATH}")
    isolation_forest = None

try:
    random_forest = joblib.load(RANDOM_FOREST_PATH)
    logger.info(f"Loaded Random Forest model from {RANDOM_FOREST_PATH}")
except FileNotFoundError:
    logger.warning(f"Random Forest model not found at {RANDOM_FOREST_PATH}")
    random_forest = None

try:
    scaler = joblib.load(SCALER_PATH)
    logger.info(f"Loaded Scaler from {SCALER_PATH}")
except FileNotFoundError:
    logger.warning(f"Scaler not found at {SCALER_PATH}")
    scaler = None


def _compute_dvs(age: float) -> float:
    """
    Compute Demographic Variability Score (DVS).
    
    DVS = age / 80, clipped to [0, 1]
    """
    dvs = age / 80.0
    return np.clip(dvs, 0, 1)


def _compute_tns(screening_count: int) -> float:
    """
    Compute Testing/Screening Normalization Score (TNS).
    
    TNS = screening_count / 3, clipped to [0, 1]
    """
    tns = screening_count / 3.0
    return np.clip(tns, 0, 1)


def _compute_ics(wealth_idx: float) -> float:
    """
    Compute Income/Wealth Clipping Score (ICS).
    
    ICS = wealth_idx / 5, clipped to [0, 1]
    """
    ics = wealth_idx / 5.0
    return np.clip(ics, 0, 1)


def _compute_ccs(has_diabetes: bool, has_htn: bool, told_high_gluc: bool, 
                 told_high_bp: bool, tx_diabetes: bool, tx_htn: bool) -> float:
    """
    Compute Consistency Check Score (CCS).
    
    CCS = sum of 4 consistency checks / 4
    
    Consistency checks:
    - C1: has_diabetes and told_high_gluc should align
    - C2: has_htn and told_high_bp should align
    - C3: Overall health consistency
    - C4: Medical history consistency
    """
    consistency_checks = 0
    
    # C1: Diabetes consistency (told_high_gluc suggests diabetes likelihood)
    if (has_diabetes and told_high_gluc) or (not has_diabetes and not told_high_gluc):
        consistency_checks += 1
    
    # C2: Hypertension consistency (told_high_bp suggests htn likelihood)
    if (has_htn and told_high_bp) or (not has_htn and not told_high_bp):
        consistency_checks += 1
    
    # C3: General consistency (both conditions or neither)
    has_conditions = has_diabetes or has_htn
    has_reported_issues = told_high_gluc or told_high_bp
    if has_conditions == has_reported_issues:
        consistency_checks += 1
    
    # C4: Treatment alignment check
    treated = tx_diabetes or tx_htn
    has_conditions_check = has_diabetes or has_htn
    if treated == has_conditions_check or (not has_conditions_check and not treated):
        consistency_checks += 1
    
    ccs = consistency_checks / 4.0
    return ccs


def _compute_hcfd(dvs: float, tns: float, ics: float, ccs: float) -> float:
    """
    Compute Healthcare Fraud Detection (HCFD) score.
    
    HCFD = 0.20*(1-DVS) * 0.30*(1-TNS) * 0.20*(1-ICS) * 0.30*(1-CCS)
    """
    hcfd = (0.20 * (1 - dvs) * 
            0.30 * (1 - tns) * 
            0.20 * (1 - ics) * 
            0.30 * (1 - ccs))
    return np.clip(hcfd, 0, 1)


def _compute_rule_score(age: int, has_diabetes: bool, has_htn: bool,
                       told_high_gluc: bool, told_high_bp: bool,
                       tx_diabetes: bool, tx_htn: bool) -> Tuple[float, list]:
    """
    Compute rule-based fraud score from medical inconsistency rules R1-R4.
    
    Returns:
        Tuple of (rule_score, rule_violations) where rule_violations is a list
        of triggered rules
    """
    rule_violations = []
    violation_count = 0
    
    # R1: Age-medication mismatch
    # Very young age with multiple chronic conditions is suspicious
    if age < 30 and (has_diabetes or has_htn) and (tx_diabetes or tx_htn):
        rule_violations.append("R1: Young age with chronic condition treatment")
        violation_count += 1
    
    # R2: Treatment without diagnosis
    # Receiving treatment for conditions not diagnosed is suspicious
    if tx_diabetes and not has_diabetes:
        rule_violations.append("R2: Diabetes treatment without diabetes diagnosis")
        violation_count += 1
    
    if tx_htn and not has_htn:
        rule_violations.append("R2: Hypertension treatment without hypertension diagnosis")
        violation_count += 1
    
    # R3: Reporting high glucose/BP without diagnosis
    # Reported high values but no corresponding diagnosis
    if told_high_gluc and not has_diabetes:
        rule_violations.append("R3: High glucose reported but no diabetes diagnosis")
        violation_count += 1
    
    if told_high_bp and not has_htn:
        rule_violations.append("R3: High BP reported but no hypertension diagnosis")
        violation_count += 1
    
    # R4: No conditions but receiving multiple treatments
    # Not diagnosed with any condition but on multiple medications
    medication_count = sum([tx_diabetes, tx_htn])
    condition_count = sum([has_diabetes, has_htn])
    if medication_count > 0 and condition_count == 0:
        rule_violations.append("R4: Multiple treatments without corresponding diagnoses")
        violation_count += 1
    
    # Compute rule score (0-1)
    # Maximum 4 violations possible
    rule_score = min(violation_count / 4.0, 1.0)
    
    return rule_score, rule_violations


def _get_anomaly_score(age: float, wealth_idx: float, screening_count: int,
                      has_diabetes: bool, has_htn: bool, told_high_gluc: bool,
                      told_high_bp: bool, tx_diabetes: bool, tx_htn: bool) -> float:
    """
    Compute anomaly score using ensemble of Isolation Forest and Random Forest.
    
    Returns anomaly score between 0 and 1.
    """
    if isolation_forest is None and random_forest is None:
        logger.warning("No anomaly detection models available, returning 0")
        return 0.0
    
    # Prepare features for model input
    features = np.array([[
        age,
        wealth_idx,
        screening_count,
        int(has_diabetes),
        int(has_htn),
        int(told_high_gluc),
        int(told_high_bp),
        int(tx_diabetes),
        int(tx_htn)
    ]])
    
    # Scale features if scaler is available
    if scaler is not None:
        try:
            features_scaled = scaler.transform(features)
        except Exception as e:
            logger.error(f"Error scaling features: {e}")
            features_scaled = features
    else:
        features_scaled = features
    
    anomaly_scores = []
    
    # Isolation Forest anomaly score
    if isolation_forest is not None:
        try:
            # Isolation Forest returns -1 for anomalies, 1 for normal
            # Convert to 0-1 scale where 1 is more anomalous
            if_prediction = isolation_forest.predict(features_scaled)
            if_score = 0.5 if if_prediction[0] == 1 else 0.8  # Anomaly gets 0.8
            anomaly_scores.append(if_score)
        except Exception as e:
            logger.error(f"Error in Isolation Forest prediction: {e}")
    
    # Random Forest anomaly detection using anomaly score
    if random_forest is not None:
        try:
            # Get prediction probability
            if hasattr(random_forest, 'predict_proba'):
                rf_proba = random_forest.predict_proba(features_scaled)
                # Use the max probability as confidence, invert for anomaly
                rf_score = 1.0 - np.max(rf_proba)
                anomaly_scores.append(rf_score)
            else:
                rf_prediction = random_forest.predict(features_scaled)
                rf_score = 0.5 if rf_prediction[0] == 1 else 0.3
                anomaly_scores.append(rf_score)
        except Exception as e:
            logger.error(f"Error in Random Forest prediction: {e}")
    
    # Average anomaly scores if both available
    if anomaly_scores:
        anomaly_score = np.mean(anomaly_scores)
    else:
        anomaly_score = 0.0
    
    return np.clip(anomaly_score, 0, 1)


def _get_risk_tier(final_risk: float) -> str:
    """
    Determine risk tier based on final risk score.
    
    Thresholds:
    - final_risk < 0.25: Low Risk
    - 0.25 <= final_risk < 0.50: Medium Risk
    - 0.50 <= final_risk < 0.75: High Risk
    - final_risk >= 0.75: Critical Risk
    """
    if final_risk >= RISK_THRESHOLDS['high']:
        return 'critical'
    elif final_risk >= RISK_THRESHOLDS['medium']:
        return 'high'
    elif final_risk >= RISK_THRESHOLDS['low']:
        return 'medium'
    else:
        return 'low'


def _generate_explanation(final_risk: float, rule_score: float, 
                         anomaly_score: float, hcfd_score: float, ccs: float,
                         rule_violations: list) -> str:
    """
    Generate human-readable explanation for the fraud risk assessment.
    """
    risk_tier = _get_risk_tier(final_risk)
    
    explanation_parts = [
        f"Risk Assessment: {risk_tier.replace('_', ' ').title()}",
        f"Final Risk Score: {final_risk:.3f}",
        "",
        "Contributing Factors:",
        f"  - Rule-based Violations (35% weight): {rule_score:.3f}",
        f"  - Anomaly Detection (30% weight): {anomaly_score:.3f}",
        f"  - Healthcare Fraud Detection (25% weight): {hcfd_score:.3f}",
        f"  - Inverse Consistency (10% weight): {1-ccs:.3f}",
    ]
    
    if rule_violations:
        explanation_parts.append("")
        explanation_parts.append("Triggered Rules:")
        for violation in rule_violations:
            explanation_parts.append(f"  - {violation}")
    
    if ccs < 0.5:
        explanation_parts.append("")
        explanation_parts.append(f"Warning: Low consistency score ({ccs:.3f}) - Medical history inconsistencies detected")
    
    return "\n".join(explanation_parts)


def compute_final_risk(age: int, wealth_idx: float, screening_count: int,
                      has_diabetes: bool, has_htn: bool, told_high_gluc: bool,
                      told_high_bp: bool, tx_diabetes: bool, tx_htn: bool) -> Dict[str, Any]:
    """
    Compute final fraud risk score and tier for a healthcare transaction.
    
    Args:
        age: Patient age in years
        wealth_idx: Wealth index (0-5+)
        screening_count: Number of health screenings
        has_diabetes: Whether patient has diabetes diagnosis
        has_htn: Whether patient has hypertension diagnosis
        told_high_gluc: Whether patient reported high glucose
        told_high_bp: Whether patient reported high blood pressure
        tx_diabetes: Whether patient is on diabetes treatment
        tx_htn: Whether patient is on hypertension treatment
    
    Returns:
        Dictionary containing:
        - final_risk: Float between 0-1 indicating overall fraud risk
        - risk_tier: String tier (low, medium, high, critical)
        - explanation: Human-readable explanation
        - scores: Dict of component scores (DVS, TNS, ICS, CCS, HCFD, rule_score, anomaly_score)
        - rule_violations: List of triggered fraud rules
    """
    
    # Compute demographic and consistency scores
    dvs = _compute_dvs(age)
    tns = _compute_tns(screening_count)
    ics = _compute_ics(wealth_idx)
    ccs = _compute_ccs(has_diabetes, has_htn, told_high_gluc, told_high_bp, tx_diabetes, tx_htn)
    hcfd = _compute_hcfd(dvs, tns, ics, ccs)
    
    # Compute rule-based fraud score
    rule_score, rule_violations = _compute_rule_score(
        age, has_diabetes, has_htn, told_high_gluc, told_high_bp,
        tx_diabetes, tx_htn
    )
    
    # Compute anomaly score from ML models
    anomaly_score = _get_anomaly_score(
        age, wealth_idx, screening_count, has_diabetes, has_htn,
        told_high_gluc, told_high_bp, tx_diabetes, tx_htn
    )
    
    # Normalize scores to 0-1 range
    rule_norm = np.clip(rule_score, 0, 1)
    anomaly_norm = np.clip(anomaly_score, 0, 1)
    hcfd_norm = np.clip(hcfd, 0, 1)
    ccs_inv = np.clip(1 - ccs, 0, 1)
    
    # Compute weighted final risk score
    # FinalRisk = 0.35*rule_norm + 0.30*anomaly_norm + 0.25*HCFD + 0.10*(1-CCS)
    final_risk = (
        0.35 * rule_norm +
        0.30 * anomaly_norm +
        0.25 * hcfd_norm +
        0.10 * ccs_inv
    )
    final_risk = np.clip(final_risk, 0, 1)
    
    # Determine risk tier
    risk_tier = _get_risk_tier(final_risk)
    
    # Generate explanation
    explanation = _generate_explanation(
        final_risk, rule_norm, anomaly_norm, hcfd_norm, ccs,
        rule_violations
    )
    
    # Compile component scores
    scores = {
        'DVS': float(dvs),
        'TNS': float(tns),
        'ICS': float(ics),
        'CCS': float(ccs),
        'HCFD': float(hcfd_norm),
        'rule_score': float(rule_norm),
        'anomaly_score': float(anomaly_norm),
    }
    
    return {
        'final_risk': float(final_risk),
        'risk_tier': risk_tier,
        'explanation': explanation,
        'scores': scores,
        'rule_violations': rule_violations,
    }
