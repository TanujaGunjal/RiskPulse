/**
 * Reports Generation Page
 * 
 * Generate and download PDF reports
 */

import React, { useState } from 'react';
import styles from './Reports.module.css';
import apiClient from '../../utils/api';

const ReportForm = ({ onSubmit, loading }) => {
  const [reportType, setReportType] = useState('daily');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(reportType);
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.formGroup}>
        <label htmlFor="reportType">Report Type</label>
        <select
          id="reportType"
          value={reportType}
          onChange={(e) => setReportType(e.target.value)}
          className={styles.select}
          disabled={loading}
        >
          <option value="daily">Daily Report (Last 24 Hours)</option>
          <option value="weekly">Weekly Report (Last 7 Days)</option>
          <option value="monthly">Monthly Report (Last 30 Days)</option>
        </select>
      </div>

      <div className={styles.formDescription}>
        {reportType === 'daily' && (
          <p>📊 Generates a report for transactions from the last 24 hours</p>
        )}
        {reportType === 'weekly' && (
          <p>📊 Generates a report for transactions from the last 7 days</p>
        )}
        {reportType === 'monthly' && (
          <p>📊 Generates a report for transactions from the last 30 days</p>
        )}
      </div>

      <button type="submit" className={styles.submitButton} disabled={loading}>
        {loading ? (
          <>
            <span className={styles.loadingSpinner}></span>
            Generating...
          </>
        ) : (
          <>📄 Generate PDF Report</>
        )}
      </button>
    </form>
  );
};

const Reports = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [recentReports, setRecentReports] = useState([
    { id: 1, type: 'daily', date: new Date().toISOString(), status: 'ready' },
    { id: 2, type: 'weekly', date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), status: 'ready' },
  ]);

  const handleGenerateReport = async (reportType) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post(
        '/reports/generate/',
        { report_type: reportType },
        { responseType: 'blob' }
      );

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `fraud_detection_${reportType}_${new Date().toISOString().split('T')[0]}.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccessMessage(`✓ ${reportType.charAt(0).toUpperCase() + reportType.slice(1)} report downloaded successfully`);
      setTimeout(() => setSuccessMessage(''), 3000);

      // Add to recent reports
      setRecentReports([
        {
          id: recentReports.length + 1,
          type: reportType,
          date: new Date().toISOString(),
          status: 'ready',
        },
        ...recentReports,
      ].slice(0, 10));
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Report Generation</h1>
        <p className={styles.subtitle}>Generate PDF reports of fraud detection activity</p>
      </div>

      {successMessage && (
        <div className={styles.successMessage}>
          {successMessage}
        </div>
      )}

      {error && (
        <div className={styles.errorMessage}>
          {error}
        </div>
      )}

      {/* Main Form Section */}
      <div className={styles.formSection}>
        <div className={styles.formCard}>
          <h2>Create New Report</h2>
          <ReportForm onSubmit={handleGenerateReport} loading={loading} />
        </div>

        {/* Report Info Cards */}
        <div className={styles.infoSection}>
          <h3>What's Included in Reports</h3>
          <div className={styles.infoGrid}>
            <div className={styles.infoCard}>
              <div className={styles.infoIcon}>📊</div>
              <h4>Summary Statistics</h4>
              <p>Total transactions, average risk score, and risk tier breakdown</p>
            </div>
            <div className={styles.infoCard}>
              <div className={styles.infoIcon}>⚠️</div>
              <h4>Risk Distribution</h4>
              <p>Detailed breakdown of low, medium, high, and critical risk cases</p>
            </div>
            <div className={styles.infoCard}>
              <div className={styles.infoIcon}>📈</div>
              <h4>Trends & Patterns</h4>
              <p>Temporal analysis and fraud detection patterns</p>
            </div>
            <div className={styles.infoCard}>
              <div className={styles.infoIcon}>🎯</div>
              <h4>Top Risk Cases</h4>
              <p>Highest risk transactions requiring immediate attention</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      {recentReports.length > 0 && (
        <div className={styles.recentSection}>
          <h2>Recently Generated Reports</h2>
          <div className={styles.reportsList}>
            {recentReports.map((report) => (
              <div key={report.id} className={styles.reportItem}>
                <div className={styles.reportIcon}>📄</div>
                <div className={styles.reportInfo}>
                  <h4>{report.type.charAt(0).toUpperCase() + report.type.slice(1)} Report</h4>
                  <p>{new Date(report.date).toLocaleString()}</p>
                </div>
                <div className={styles.reportStatus}>
                  <span className={`${styles.statusBadge} ${styles[`status-${report.status}`]}`}>
                    ✓ {report.status.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FAQ Section */}
      <div className={styles.faqSection}>
        <h2>Frequently Asked Questions</h2>
        <div className={styles.faqItems}>
          <div className={styles.faqItem}>
            <h4>How often can I generate reports?</h4>
            <p>You can generate reports as frequently as needed. Each report is generated on-demand with the latest data.</p>
          </div>
          <div className={styles.faqItem}>
            <h4>What format are reports in?</h4>
            <p>Reports are generated as PDF files which can be opened, printed, or shared easily. They contain formatted tables and comprehensive statistics.</p>
          </div>
          <div className={styles.faqItem}>
            <h4>Can I customize the report contents?</h4>
            <p>Currently, reports are generated with standard content. Custom report generation features may be added in future updates.</p>
          </div>
          <div className={styles.faqItem}>
            <h4>How long does it take to generate a report?</h4>
            <p>Most reports are generated within a few seconds. The time may vary depending on the amount of data in the selected date range.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
