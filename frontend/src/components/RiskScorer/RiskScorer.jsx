/**
 * Risk Scorer Page Component
 * 
 * Form-based interface for scoring healthcare transactions and detecting fraud risk.
 * Displays animated results with sub-scores and detailed explanation.
 */

import React, { useState } from 'react';
import { scoreTransaction } from '../../utils/api';
import styles from './RiskScorer.module.css';

/**
 * Circular Score Ring Component
 */
const ScoreRing = ({ score, maxScore = 100 }) => {
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference - (score / maxScore) * circumference;
  
  return (
    <div className={styles.scoreRingContainer}>
      <svg viewBox="0 0 120 120" className={styles.scoreRingSvg}>
        {/* Background ring */}
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="8"
        />
        {/* Animated progress ring */}
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke={getScoreColor(score)}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={styles.scoreRingProgress}
        />
      </svg>
      <div className={styles.scoreRingText}>
        <span className={styles.scoreValue}>{score.toFixed(1)}</span>
        <span className={styles.scoreLabel}>Risk Score</span>
      </div>
    </div>
  );
};

/**
 * Sub-Score Card Component
 */
const ScoreCard = ({ label, score, description }) => (
  <div className={styles.scoreCard}>
    <div className={styles.scoreCardHeader}>
      <h4>{label}</h4>
      <span className={styles.scoreCardValue}>{(score * 100).toFixed(1)}%</span>
    </div>
    <div className={styles.scoreCardBar}>
      <div
        className={styles.scoreCardBarFill}
        style={{ width: `${score * 100}%` }}
      ></div>
    </div>
    {description && <p className={styles.scoreCardDescription}>{description}</p>}
  </div>
);

/**
 * Risk Tier Badge Component
 */
const RiskTierBadge = ({ tier }) => {
  const tierConfig = {
    low: { label: 'Low Risk', color: 'low' },
    medium: { label: 'Medium Risk', color: 'medium' },
    high: { label: 'High Risk', color: 'high' },
    critical: { label: 'Critical Risk', color: 'critical' },
  };
  
  const config = tierConfig[tier] || tierConfig.low;
  
  return (
    <span className={`${styles.riskTierBadge} ${styles[`badge-${config.color}`]}`}>
      {config.label}
    </span>
  );
};

/**
 * Main RiskScorer Component
 */
const RiskScorer = () => {
  // Form state
  const [formData, setFormData] = useState({
    caseid: '',
    age: '',
    wealth_idx: '2.5',
    education: '',
    residence: '',
    screening_count: '0',
    has_diabetes: false,
    has_htn: false,
    told_high_gluc: false,
    told_high_bp: false,
    tx_diabetes: false,
    tx_htn: false,
  });

  // Result state
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Handle form input changes
   */
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      setResult(null);

      // Validate required fields
      if (!formData.caseid || !formData.age) {
        setError('Please fill in Case ID and Age');
        setLoading(false);
        return;
      }

      // Prepare data for API
      const scoreData = {
        caseid: formData.caseid,
        age: parseInt(formData.age),
        wealth_idx: parseFloat(formData.wealth_idx),
        education: formData.education,
        residence: formData.residence,
        screening_count: parseInt(formData.screening_count),
        has_diabetes: formData.has_diabetes,
        has_htn: formData.has_htn,
        told_high_gluc: formData.told_high_gluc,
        told_high_bp: formData.told_high_bp,
        tx_diabetes: formData.tx_diabetes,
        tx_htn: formData.tx_htn,
      };

      // Call API
      const scoreResult = await scoreTransaction(scoreData);
      setResult(scoreResult);
    } catch (err) {
      console.error('Error scoring transaction:', err);
      setError(err.response?.data?.error || 'Failed to score transaction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle reset form
   */
  const handleReset = () => {
    setFormData({
      caseid: '',
      age: '',
      wealth_idx: '2.5',
      education: '',
      residence: '',
      screening_count: '0',
      has_diabetes: false,
      has_htn: false,
      told_high_gluc: false,
      told_high_bp: false,
      tx_diabetes: false,
      tx_htn: false,
    });
    setResult(null);
    setError(null);
  };

  return (
    <div className={styles.riskScorer}>
      {/* Header */}
      <div className={styles.header}>
        <h1>Risk Scorer</h1>
        <p className={styles.subtitle}>
          Enter transaction details to calculate fraud risk score
        </p>
      </div>

      <div className={styles.container}>
        {/* Form Section */}
        <div className={`${styles.section} ${styles.formSection}`}>
          <h2>Transaction Details</h2>
          <form onSubmit={handleSubmit} className={styles.form}>
            {/* Row 1: Case ID and Age */}
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="caseid">Case ID *</label>
                <input
                  type="text"
                  id="caseid"
                  name="caseid"
                  value={formData.caseid}
                  onChange={handleInputChange}
                  placeholder="e.g., CASE001"
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="age">Age *</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  placeholder="Enter age"
                  min="0"
                  max="150"
                  required
                />
              </div>
            </div>

            {/* Row 2: Education and Residence */}
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="education">Education</label>
                <input
                  type="text"
                  id="education"
                  name="education"
                  value={formData.education}
                  onChange={handleInputChange}
                  placeholder="e.g., High School"
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="residence">Residence</label>
                <input
                  type="text"
                  id="residence"
                  name="residence"
                  value={formData.residence}
                  onChange={handleInputChange}
                  placeholder="e.g., Urban"
                />
              </div>
            </div>

            {/* Row 3: Wealth Index and Screening Count */}
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="wealth_idx">Wealth Index</label>
                <select
                  id="wealth_idx"
                  name="wealth_idx"
                  value={formData.wealth_idx}
                  onChange={handleInputChange}
                >
                  <option value="0.5">Very Low (0.5)</option>
                  <option value="1.5">Low (1.5)</option>
                  <option value="2.5">Medium (2.5)</option>
                  <option value="3.5">High (3.5)</option>
                  <option value="4.5">Very High (4.5)</option>
                </select>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="screening_count">Screening Count</label>
                <select
                  id="screening_count"
                  name="screening_count"
                  value={formData.screening_count}
                  onChange={handleInputChange}
                >
                  <option value="0">None (0)</option>
                  <option value="1">1 Screening</option>
                  <option value="2">2 Screenings</option>
                  <option value="3">3+ Screenings</option>
                </select>
              </div>
            </div>

            {/* Row 4: Checkboxes - Diagnoses */}
            <div className={styles.formSection}>
              <h3>Diagnoses</h3>
              <div className={styles.checkboxGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="has_diabetes"
                    checked={formData.has_diabetes}
                    onChange={handleInputChange}
                  />
                  <span>Has Diabetes</span>
                </label>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="has_htn"
                    checked={formData.has_htn}
                    onChange={handleInputChange}
                  />
                  <span>Has Hypertension (HTN)</span>
                </label>
              </div>
            </div>

            {/* Row 5: Checkboxes - Reported High Values */}
            <div className={styles.formSection}>
              <h3>Reported High Values</h3>
              <div className={styles.checkboxGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="told_high_gluc"
                    checked={formData.told_high_gluc}
                    onChange={handleInputChange}
                  />
                  <span>Told High Glucose</span>
                </label>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="told_high_bp"
                    checked={formData.told_high_bp}
                    onChange={handleInputChange}
                  />
                  <span>Told High Blood Pressure</span>
                </label>
              </div>
            </div>

            {/* Row 6: Checkboxes - Treatments */}
            <div className={styles.formSection}>
              <h3>Current Treatments</h3>
              <div className={styles.checkboxGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="tx_diabetes"
                    checked={formData.tx_diabetes}
                    onChange={handleInputChange}
                  />
                  <span>Diabetes Treatment</span>
                </label>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="tx_htn"
                    checked={formData.tx_htn}
                    onChange={handleInputChange}
                  />
                  <span>Hypertension Treatment</span>
                </label>
              </div>
            </div>

            {/* Error Message */}
            {error && <div className={styles.errorMessage}>{error}</div>}

            {/* Buttons */}
            <div className={styles.formButtons}>
              <button
                type="submit"
                disabled={loading}
                className={`${styles.button} ${styles.submitButton}`}
              >
                {loading ? 'Calculating...' : 'Calculate Risk Score'}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className={`${styles.button} ${styles.resetButton}`}
                disabled={loading}
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* Results Section */}
        {result && (
          <div className={`${styles.section} ${styles.resultsSection}`}>
            <h2>Risk Assessment Results</h2>

            {/* Case ID */}
            <div className={styles.resultHeader}>
              <span className={styles.caseIdResult}>Case: {result.caseid}</span>
              <RiskTierBadge tier={result.risk_tier} />
            </div>

            {/* Score Ring */}
            <div className={styles.scoreRingWrapper}>
              <ScoreRing score={result.final_risk * 100} />
            </div>

            {/* Sub-Scores */}
            <div className={styles.scoresGrid}>
              <ScoreCard
                label="DVS"
                score={result.scores.DVS}
                description="Demographic Variability"
              />
              <ScoreCard
                label="TNS"
                score={result.scores.TNS}
                description="Testing/Screening"
              />
              <ScoreCard
                label="ICS"
                score={result.scores.ICS}
                description="Income/Wealth"
              />
              <ScoreCard
                label="CCS"
                score={result.scores.CCS}
                description="Consistency Check"
              />
              <ScoreCard
                label="HCFD"
                score={result.scores.HCFD}
                description="Healthcare Fraud Detection"
              />
              <ScoreCard
                label="Rule Score"
                score={result.scores.rule_score}
                description="Medical Inconsistencies"
              />
              <ScoreCard
                label="Anomaly Score"
                score={result.scores.anomaly_score}
                description="ML Anomaly Detection"
              />
            </div>

            {/* Formula Box */}
            <div className={styles.formulaBox}>
              <h3>Risk Calculation Formula</h3>
              <div className={styles.formula}>
                <span className={styles.formulaLabel}>Final Risk</span>
                <span className={styles.formulaEquals}>=</span>
                <div className={styles.formulaTerms}>
                  <div className={styles.formulaTerm}>
                    <span className={styles.weight}>0.35</span>
                    <span>×</span>
                    <span className={styles.component}>Rule Score</span>
                  </div>
                  <span className={styles.plus}>+</span>
                  <div className={styles.formulaTerm}>
                    <span className={styles.weight}>0.30</span>
                    <span>×</span>
                    <span className={styles.component}>Anomaly Score</span>
                  </div>
                  <span className={styles.plus}>+</span>
                  <div className={styles.formulaTerm}>
                    <span className={styles.weight}>0.25</span>
                    <span>×</span>
                    <span className={styles.component}>HCFD</span>
                  </div>
                  <span className={styles.plus}>+</span>
                  <div className={styles.formulaTerm}>
                    <span className={styles.weight}>0.10</span>
                    <span>×</span>
                    <span>(1 − CCS)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Explanation Box */}
            <div className={styles.explanationBox}>
              <h3>Risk Assessment Explanation</h3>
              <pre className={styles.explanationText}>{result.explanation}</pre>
            </div>

            {/* Rule Violations */}
            {result.rule_violations && result.rule_violations.length > 0 && (
              <div className={styles.violationsBox}>
                <h3>Triggered Rules</h3>
                <ul className={styles.violationsList}>
                  {result.rule_violations.map((violation, index) => (
                    <li key={index} className={styles.violationItem}>
                      {violation}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* New Assessment Button */}
            <button onClick={handleReset} className={styles.newAssessmentButton}>
              New Assessment
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className={styles.loadingContainer}>
            <div className={styles.spinner}></div>
            <p>Calculating risk score...</p>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Helper function to get color for risk score
 */
function getScoreColor(score) {
  if (score >= 75) return '#EF4444'; // Critical - Red
  if (score >= 50) return '#EF6B3E'; // High - Orange
  if (score >= 25) return '#F59E0B'; // Medium - Amber
  return '#10B981'; // Low - Green
}

export default RiskScorer;
