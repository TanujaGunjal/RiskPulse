/**
 * Example Usage of RiskScorer Component
 */

import React from 'react';
import RiskScorer from './components/RiskScorer';

/**
 * ============================================================================
 * BASIC USAGE
 * ============================================================================
 */

export function BasicExample() {
  return (
    <div>
      <RiskScorer />
    </div>
  );
}

/**
 * ============================================================================
 * WITH REACT ROUTER
 * ============================================================================
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';

export function AppWithRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/score" element={<RiskScorer />} />
      </Routes>
    </Router>
  );
}

/**
 * ============================================================================
 * WITH NAVIGATION LAYOUT
 * ============================================================================
 */

import './AppLayout.css';

export function AppWithLayout() {
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  return (
    <div className="app-layout">
      <nav className="sidebar-nav">
        <h2>Fraud Detection Platform</h2>
        <ul>
          <li>
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={currentPage === 'dashboard' ? 'active' : ''}
            >
              📊 Dashboard
            </button>
          </li>
          <li>
            <button
              onClick={() => setCurrentPage('score')}
              className={currentPage === 'score' ? 'active' : ''}
            >
              🔍 Risk Scorer
            </button>
          </li>
          <li>
            <button
              onClick={() => setCurrentPage('transactions')}
              className={currentPage === 'transactions' ? 'active' : ''}
            >
              📋 Transactions
            </button>
          </li>
          <li>
            <button
              onClick={() => setCurrentPage('alerts')}
              className={currentPage === 'alerts' ? 'active' : ''}
            >
              🚨 Alerts
            </button>
          </li>
        </ul>
      </nav>

      <main className="main-content">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'score' && <RiskScorer />}
        {currentPage === 'transactions' && <div>Transactions Page</div>}
        {currentPage === 'alerts' && <div>Alerts Page</div>}
      </main>
    </div>
  );
}

/**
 * ============================================================================
 * WITH CONTEXT API FOR STATE MANAGEMENT
 * ============================================================================
 */

import { createContext, useState } from 'react';

export const AppContext = createContext();

export function AppWithContext() {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');

  return (
    <AppContext.Provider value={{ user, setUser, theme, setTheme }}>
      <RiskScorer />
    </AppContext.Provider>
  );
}

/**
 * ============================================================================
 * WITH ERROR BOUNDARY
 * ============================================================================
 */

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong. Please refresh the page.</h1>;
    }

    return this.props.children;
  }
}

export function AppWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <RiskScorer />
    </ErrorBoundary>
  );
}

/**
 * ============================================================================
 * WITH AUTHENTICATION
 * ============================================================================
 */

export function AppWithAuth() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('authToken');
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div>
        <h1>Please log in to access the Risk Scorer</h1>
        <button onClick={() => setIsAuthenticated(true)}>Login</button>
      </div>
    );
  }

  return <RiskScorer />;
}

/**
 * ============================================================================
 * EXAMPLE WITH RESULTS HANDLING
 * ============================================================================
 */

export function AppWithResultsHandling() {
  const [lastResult, setLastResult] = React.useState(null);

  // This would typically be implemented inside the RiskScorer component
  // or passed as a callback prop (if we extend the component)

  return (
    <div>
      <RiskScorer />
      {lastResult && (
        <div className="results-sidebar">
          <h3>Last Scoring Result</h3>
          <p>Case: {lastResult.caseid}</p>
          <p>Risk: {(lastResult.final_risk * 100).toFixed(1)}%</p>
          <p>Tier: {lastResult.risk_tier}</p>
        </div>
      )}
    </div>
  );
}

/**
 * ============================================================================
 * FORM DATA EXAMPLES FOR TESTING
 * ============================================================================
 */

export const testCases = {
  // Low Risk Case
  lowRisk: {
    caseid: 'LOW001',
    age: 35,
    wealth_idx: 3.5,
    education: 'College',
    residence: 'Urban',
    screening_count: 2,
    has_diabetes: false,
    has_htn: false,
    told_high_gluc: false,
    told_high_bp: false,
    tx_diabetes: false,
    tx_htn: false,
  },

  // Medium Risk Case
  mediumRisk: {
    caseid: 'MED001',
    age: 50,
    wealth_idx: 2.5,
    education: 'High School',
    residence: 'Rural',
    screening_count: 1,
    has_diabetes: true,
    has_htn: false,
    told_high_gluc: true,
    told_high_bp: false,
    tx_diabetes: true,
    tx_htn: false,
  },

  // High Risk Case
  highRisk: {
    caseid: 'HIGH001',
    age: 55,
    wealth_idx: 1.5,
    education: 'Elementary',
    residence: 'Rural',
    screening_count: 0,
    has_diabetes: false,
    has_htn: true,
    told_high_gluc: true,
    told_high_bp: true,
    tx_diabetes: true,
    tx_htn: false,
  },

  // Critical Risk Case
  criticalRisk: {
    caseid: 'CRIT001',
    age: 28,
    wealth_idx: 0.5,
    education: 'None',
    residence: 'Rural',
    screening_count: 0,
    has_diabetes: false,
    has_htn: false,
    told_high_gluc: true,
    told_high_bp: true,
    tx_diabetes: true,
    tx_htn: true,
  },
};

/**
 * ============================================================================
 * MOCK API FOR DEVELOPMENT/TESTING
 * ============================================================================
 */

export const mockApiResponse = {
  transaction_id: 42,
  caseid: 'TEST001',
  final_risk: 0.623,
  risk_tier: 'high',
  alert_id: 5,
  scores: {
    DVS: 0.5625,
    TNS: 0.667,
    ICS: 0.5,
    CCS: 0.75,
    HCFD: 0.012,
    rule_score: 0.25,
    anomaly_score: 0.401,
  },
  explanation:
    'Risk Assessment: High Risk\n\nFinal Risk Score: 0.623\n\nContributing Factors:\n  - Rule-based Violations (35% weight): 0.250\n  - Anomaly Detection (30% weight): 0.401\n  - Healthcare Fraud Detection (25% weight): 0.012\n  - Inverse Consistency (10% weight): 0.250\n\nWarning: Some medical history inconsistencies detected.',
  rule_violations: [
    'R2: Diabetes treatment without diabetes diagnosis',
    'R3: High BP reported but no hypertension diagnosis',
  ],
};

export default {
  BasicExample,
  AppWithRouter,
  AppWithLayout,
  AppWithContext,
  AppWithErrorBoundary,
  AppWithAuth,
  AppWithResultsHandling,
  testCases,
  mockApiResponse,
};
