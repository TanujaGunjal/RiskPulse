/**
 * Alerts Management Page
 * 
 * Displays unresolved alerts with resolution actions
 */

import React, { useState, useEffect } from 'react';
import styles from './Alerts.module.css';
import apiClient from '../../utils/api';

const LoadingSpinner = () => (
  <div className={styles.spinnerContainer}>
    <div className={styles.spinner}></div>
    <p>Loading alerts...</p>
  </div>
);

const AlertDetailModal = ({ alert, onClose, onResolve }) => {
  if (!alert) return null;

  const handleResolve = async () => {
    await onResolve(alert.id);
    onClose();
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Alert Details</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        <div className={styles.modalBody}>
          <div className={styles.detailGrid}>
            <div className={styles.detailItem}>
              <label>Alert ID</label>
              <p>{alert.id}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Case ID</label>
              <p className={styles.caseIdBold}>{alert.caseid}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Final Risk Score</label>
              <p className={styles.riskScore}>{alert.final_risk.toFixed(3)}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Risk Tier</label>
              <p className={`${styles.riskTier} ${styles[`tier-${alert.risk_tier}`]}`}>
                {alert.risk_tier.toUpperCase()}
              </p>
            </div>
            <div className={styles.detailItem}>
              <label>Created Date</label>
              <p>{new Date(alert.created_at).toLocaleString()}</p>
            </div>
          </div>
          <div className={styles.messageSection}>
            <label>Alert Message</label>
            <p className={styles.message}>{alert.message}</p>
          </div>
          <div className={styles.actionsModal}>
            <button className={styles.resolveButtonModal} onClick={handleResolve}>
              ✓ Mark as Resolved
            </button>
            <button className={styles.cancelButton} onClick={onClose}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Load alerts
  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/alerts/');
      setAlerts(response.data.alerts || []);
    } catch (err) {
      console.error('Error loading alerts:', err);
      setError('Failed to load alerts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Resolve alert
  const handleResolveAlert = async (alertId) => {
    try {
      await apiClient.patch(`/alerts/${alertId}/resolve/`);
      setSuccessMessage(`Alert #${alertId} marked as resolved`);
      loadAlerts();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error resolving alert:', err);
      setError('Failed to resolve alert. Please try again.');
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1>Alerts Management</h1>
          <p className={styles.subtitle}>High-risk transactions requiring attention</p>
        </div>
        <button onClick={loadAlerts} className={styles.refreshButton}>
          ↻ Refresh
        </button>
      </div>

      {successMessage && (
        <div className={styles.successMessage}>
          ✓ {successMessage}
        </div>
      )}

      {error && (
        <div className={styles.errorMessage}>
          {error}
        </div>
      )}

      {/* Alerts Stats */}
      <div className={styles.statsSection}>
        <div className={styles.statCard}>
          <h3>Total Unresolved Alerts</h3>
          <p className={styles.statValue}>{alerts.length}</p>
        </div>
        <div className={styles.statCard}>
          <h3>Critical Alerts</h3>
          <p className={styles.statValue} style={{ color: '#ef4444' }}>
            {alerts.filter(a => a.risk_tier === 'critical').length}
          </p>
        </div>
        <div className={styles.statCard}>
          <h3>High Risk Alerts</h3>
          <p className={styles.statValue} style={{ color: '#f97316' }}>
            {alerts.filter(a => a.risk_tier === 'high').length}
          </p>
        </div>
      </div>

      {/* Alerts Table */}
      <div className={styles.tableSection}>
        {alerts.length > 0 ? (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>Case ID</th>
                  <th>Risk Score</th>
                  <th>Risk Tier</th>
                  <th>Message</th>
                  <th>Created Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id} className={styles[`risk-${alert.risk_tier}`]}>
                    <td className={styles.alertIdCell}>#{alert.id}</td>
                    <td className={styles.caseIdCell}>{alert.caseid}</td>
                    <td className={styles.riskScoreCell}>
                      <span className={styles.riskScore}>{alert.final_risk.toFixed(3)}</span>
                    </td>
                    <td>
                      <span className={`${styles.riskTierBadge} ${styles[`badge-${alert.risk_tier}`]}`}>
                        {alert.risk_tier.toUpperCase()}
                      </span>
                    </td>
                    <td className={styles.messageCell}>
                      <span className={styles.messageTruncated}>{alert.message}</span>
                    </td>
                    <td className={styles.dateCell}>
                      {new Date(alert.created_at).toLocaleDateString()}
                    </td>
                    <td className={styles.actionsCell}>
                      <button
                        className={styles.detailButton}
                        onClick={() => setSelectedAlert(alert)}
                      >
                        View & Resolve
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.noData}>
            <div className={styles.noDataIcon}>✓</div>
            <p>No unresolved alerts</p>
            <p className={styles.noDataSubtext}>All transactions are within acceptable risk parameters</p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onResolve={handleResolveAlert}
        />
      )}
    </div>
  );
};

export default Alerts;
