/**
 * Healthcare Fraud Detection Dashboard Component
 * 
 * Displays key fraud detection metrics, trends, and risk records
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { fetchDashboardStats } from '../../utils/api';
import styles from './Dashboard.module.css';

/**
 * Loading Spinner Component
 */
const LoadingSpinner = () => (
  <div className={styles.spinnerContainer}>
    <div className={styles.spinner}></div>
    <p>Loading dashboard data...</p>
  </div>
);

/**
 * KPI Card Component
 */
const KPICard = ({ title, value, icon, color, subtitle }) => (
  <div className={`${styles.kpiCard} ${styles[`kpi-${color}`]}`}>
    <div className={styles.kpiIcon}>{icon}</div>
    <div className={styles.kpiContent}>
      <p className={styles.kpiTitle}>{title}</p>
      <p className={styles.kpiValue}>{value}</p>
      {subtitle && <p className={styles.kpiSubtitle}>{subtitle}</p>}
    </div>
  </div>
);

/**
 * Dashboard Component
 */
const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load dashboard data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <p className={styles.errorMessage}>{error}</p>
        <button onClick={loadDashboardData} className={styles.retryButton}>
          Retry
        </button>
      </div>
    );
  }

  if (!stats) {
    return <div className={styles.noData}>No data available</div>;
  }

  // Extract stats
  const {
    total_transactions = 0,
    risk_tier_counts = {},
    average_risk = 0,
    total_flagged = 0,
    monthly_counts = [],
    top_risk_records = [],
  } = stats;

  // Calculate critical and high risk counts
  const criticalCount = risk_tier_counts.critical || 0;
  const highCount = risk_tier_counts.high || 0;
  const highRiskTotal = criticalCount + highCount;

  // Prepare pie chart data
  const pieData = [
    {
      name: 'Low Risk',
      value: risk_tier_counts.low || 0,
      color: '#10B981',
    },
    {
      name: 'Medium Risk',
      value: risk_tier_counts.medium || 0,
      color: '#F59E0B',
    },
    {
      name: 'High Risk',
      value: risk_tier_counts.high || 0,
      color: '#EF6B3E',
    },
    {
      name: 'Critical Risk',
      value: risk_tier_counts.critical || 0,
      color: '#EF4444',
    },
  ].filter((item) => item.value > 0);

  // Format top risk records
  const formattedTopRecords = top_risk_records.map((record) => ({
    ...record,
    riskPercent: (record.final_risk * 100).toFixed(1),
  }));

  return (
    <div className={styles.dashboard}>
      {/* Header */}
      <div className={styles.header}>
        <h1>Healthcare Fraud Detection Dashboard</h1>
        <p className={styles.subtitle}>Real-time fraud detection and risk analytics</p>
        <button onClick={loadDashboardData} className={styles.refreshButton}>
          ↻ Refresh
        </button>
      </div>

      {/* KPI Cards Section */}
      <div className={styles.kpiSection}>
        <KPICard
          title="Total Records"
          value={total_transactions.toLocaleString()}
          icon="📊"
          color="blue"
        />
        <KPICard
          title="High Risk"
          value={highCount}
          icon="⚠️"
          color="orange"
          subtitle={`${((highCount / total_transactions) * 100).toFixed(1)}% of total`}
        />
        <KPICard
          title="Critical Risk"
          value={criticalCount}
          icon="🚨"
          color="red"
          subtitle={`${((criticalCount / total_transactions) * 100).toFixed(1)}% of total`}
        />
        <KPICard
          title="Average Risk Score"
          value={(average_risk * 100).toFixed(1)}
          icon="📈"
          color="green"
          subtitle="0-100 scale"
        />
      </div>

      {/* Charts Section */}
      <div className={styles.chartsSection}>
        {/* Monthly Fraud Counts Chart */}
        <div className={styles.chartContainer}>
          <h2>Monthly Fraud Counts (Last 6 Months)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthly_counts}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#f9fafb',
                  border: '1px solid #e5e7eb',
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Tier Distribution Chart */}
        <div className={styles.chartContainer}>
          <h2>Risk Tier Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value, percent }) =>
                  `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => value.toLocaleString()}
                contentStyle={{
                  backgroundColor: '#f9fafb',
                  border: '1px solid #e5e7eb',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Risk Records Table */}
      <div className={styles.tableSection}>
        <h2>Top 5 Highest Risk Records</h2>
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Final Risk Score</th>
                <th>Risk Percentage</th>
                <th>Risk Tier</th>
                <th>Created Date</th>
              </tr>
            </thead>
            <tbody>
              {formattedTopRecords.length > 0 ? (
                formattedTopRecords.map((record, index) => (
                  <tr key={index} className={styles[`risk-${record.risk_tier}`]}>
                    <td className={styles.caseIdCell}>
                      <span className={styles.caseId}>{record.caseid}</span>
                    </td>
                    <td>
                      <span className={styles.riskScore}>
                        {record.final_risk.toFixed(3)}
                      </span>
                    </td>
                    <td>
                      <div className={styles.riskBar}>
                        <div
                          className={styles.riskFill}
                          style={{
                            width: `${record.riskPercent}%`,
                            backgroundColor: getRiskColor(record.risk_tier),
                          }}
                        ></div>
                      </div>
                      <span className={styles.riskPercent}>{record.riskPercent}%</span>
                    </td>
                    <td>
                      <span
                        className={`${styles.riskBadge} ${styles[`badge-${record.risk_tier}`]}`}
                      >
                        {record.risk_tier.charAt(0).toUpperCase() +
                          record.risk_tier.slice(1)}
                      </span>
                    </td>
                    <td>
                      {new Date(record.created_at).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className={styles.noRecords}>
                    No records found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <p>
          Last updated: {new Date().toLocaleString('en-US', { dateStyle: 'long', timeStyle: 'short' })}
        </p>
      </div>
    </div>
  );
};

/**
 * Helper function to get color for risk tier
 */
function getRiskColor(riskTier) {
  const colors = {
    low: '#10B981',
    medium: '#F59E0B',
    high: '#EF6B3E',
    critical: '#EF4444',
  };
  return colors[riskTier] || '#6B7280';
}

export default Dashboard;
