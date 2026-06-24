import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import styles from './Analytics.module.css';
import apiClient from '../../utils/api';

const Analytics = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [modelData, setModelData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch all analytics data using apiClient
      const [dashboard, trends, models] = await Promise.all([
        apiClient.get('/analytics/dashboard/'),
        apiClient.get('/analytics/trends/', { params: { days: 30 } }),
        apiClient.get('/analytics/model_performance/'),
      ]);

      setDashboardData(dashboard.data);
      setTrendsData(trends.data);
      setModelData(models.data);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.container}><p>Loading analytics...</p></div>;
  if (error) return <div className={styles.container}><p className={styles.error}>{error}</p></div>;
  if (!dashboardData) return <div className={styles.container}><p>No data available</p></div>;

  const COLORS = ['#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div className={styles.container}>
      <h1>📊 Analytics Dashboard</h1>

      {/* KPI Cards */}
      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <h3>Total Transactions</h3>
          <p className={styles.kpiValue}>{dashboardData.transactions.total}</p>
        </div>
        <div className={styles.kpiCard}>
          <h3>Avg Risk Score</h3>
          <p className={styles.kpiValue}>{(dashboardData.transactions.average_risk_score * 100).toFixed(1)}%</p>
        </div>
        <div className={styles.kpiCard}>
          <h3>Insurance Approvals</h3>
          <p className={styles.kpiValue}>{dashboardData.insurance.by_decision.approved || 0}</p>
        </div>
        <div className={styles.kpiCard}>
          <h3>Open Alerts</h3>
          <p className={styles.kpiValue}>{dashboardData.alerts.open}</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className={styles.chartsGrid}>
        {/* Risk Distribution */}
        <div className={styles.chartBox}>
          <h3>Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={Object.entries(dashboardData.transactions.risk_distribution || {}).map(([name, value]) => ({
                  name, value
                }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {Object.entries(dashboardData.transactions.risk_distribution || {}).map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Insurance Decisions */}
        <div className={styles.chartBox}>
          <h3>Insurance Decisions</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={Object.entries(dashboardData.insurance.by_decision || {}).map(([decision, count]) => ({
              name: decision,
              count
            }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trends */}
      {trendsData && trendsData.daily_transactions && (
        <div className={styles.chartBox}>
          <h3>📈 Transaction Trends (30 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendsData.daily_transactions}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#8884d8" name="Transaction Count" />
              <Line type="monotone" dataKey="high_risk_count" stroke="#FF8042" name="High Risk" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Model Performance */}
      {modelData && modelData.model_performance && (
        <div className={styles.modelSection}>
          <h3>🤖 Model Performance Metrics</h3>
          <div className={styles.modelGrid}>
            {modelData.model_performance.map((model, idx) => (
              <div key={idx} className={styles.modelCard}>
                <h4>{model.model_type}</h4>
                <p>Version: {model.version}</p>
                <div className={styles.metrics}>
                  <p>Accuracy: {(model.accuracy * 100).toFixed(1)}%</p>
                  <p>Precision: {(model.precision * 100).toFixed(1)}%</p>
                  <p>Recall: {(model.recall * 100).toFixed(1)}%</p>
                  <p>F1 Score: {(model.f1_score * 100).toFixed(1)}%</p>
                  <p>AUC-ROC: {(model.auc_roc * 100).toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fraud Indicators */}
      <div className={styles.indicatorBox}>
        <h3>⚠️ Fraud Indicators</h3>
        <p>Total Rule Violations: <strong>{dashboardData.fraud_indicators.total_violations}</strong></p>
        <p>Results Analyzed: <strong>{dashboardData.fraud_indicators.results_analyzed}</strong></p>
      </div>

      {/* Refresh Button */}
      <button className={styles.refreshBtn} onClick={loadAnalyticsData}>
        🔄 Refresh Data
      </button>
    </div>
  );
};

export default Analytics;
