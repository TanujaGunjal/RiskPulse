import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard/Dashboard';
import RiskScorer from './components/RiskScorer/RiskScorer';
import Analytics from './components/Analytics/Analytics';
import Transactions from './components/Transactions/Transactions';
import Alerts from './components/Alerts/Alerts';
import Reports from './components/Reports/Reports';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard'); // 'dashboard', 'scorer', 'transactions', 'alerts', 'reports', 'analytics'

  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>RiskPulse</h1>
          <p className="navbar-subtitle">Healthcare Fraud Detection Platform</p>
        </div>
        <ul className="navbar-nav">
          <li>
            <button 
              className={`nav-button ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              Dashboard
            </button>
          </li>
          <li>
            <button 
              className={`nav-button ${currentPage === 'scorer' ? 'active' : ''}`}
              onClick={() => setCurrentPage('scorer')}
            >
              Risk Scorer
            </button>
          </li>
          <li>
            <button 
              className={`nav-button ${currentPage === 'transactions' ? 'active' : ''}`}
              onClick={() => setCurrentPage('transactions')}
            >
              Transactions
            </button>
          </li>
          <li>
            <button 
              className={`nav-button ${currentPage === 'alerts' ? 'active' : ''}`}
              onClick={() => setCurrentPage('alerts')}
            >
              Alerts
            </button>
          </li>
          <li>
            <button 
              className={`nav-button ${currentPage === 'reports' ? 'active' : ''}`}
              onClick={() => setCurrentPage('reports')}
            >
              Reports
            </button>
          </li>
          <li>
            <button 
              className={`nav-button ${currentPage === 'analytics' ? 'active' : ''}`}
              onClick={() => setCurrentPage('analytics')}
            >
              Analytics
            </button>
          </li>
        </ul>
      </nav>

      <main className="main-content">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'scorer' && <RiskScorer />}
        {currentPage === 'transactions' && <Transactions />}
        {currentPage === 'alerts' && <Alerts />}
        {currentPage === 'reports' && <Reports />}
        {currentPage === 'analytics' && <Analytics />}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 RiskPulse - Healthcare Fraud Detection. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
