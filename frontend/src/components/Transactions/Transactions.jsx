/**
 * Transactions List Page
 * 
 * Displays all transactions with search, filtering, and pagination
 */

import React, { useState, useEffect } from 'react';
import styles from './Transactions.module.css';
import apiClient from '../../utils/api';

const LoadingSpinner = () => (
  <div className={styles.spinnerContainer}>
    <div className={styles.spinner}></div>
    <p>Loading transactions...</p>
  </div>
);

const TransactionDetailModal = ({ transaction, onClose }) => {
  if (!transaction) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Transaction Details</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        <div className={styles.modalBody}>
          <div className={styles.detailGrid}>
            <div className={styles.detailItem}>
              <label>Case ID</label>
              <p>{transaction.caseid}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Age</label>
              <p>{transaction.age}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Final Risk Score</label>
              <p className={styles.riskScore}>{transaction.final_risk.toFixed(3)}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Risk Tier</label>
              <p className={`${styles.riskTier} ${styles[`tier-${transaction.risk_tier}`]}`}>
                {transaction.risk_tier.toUpperCase()}
              </p>
            </div>
            <div className={styles.detailItem}>
              <label>Created Date</label>
              <p>{new Date(transaction.created_at).toLocaleString()}</p>
            </div>
            <div className={styles.detailItem}>
              <label>Has Active Alerts</label>
              <p>{transaction.has_alerts ? '⚠️ Yes' : '✅ No'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTransaction, setSelectedTransaction] = useState(null);

  // Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [riskTierFilter, setRiskTierFilter] = useState('');
  const [minRiskFilter, setMinRiskFilter] = useState('');
  const [maxRiskFilter, setMaxRiskFilter] = useState('');

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Load transactions
  const loadTransactions = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page: currentPage,
        page_size: pageSize,
      };

      if (searchTerm) params.search = searchTerm;
      if (riskTierFilter) params.risk_tier = riskTierFilter;
      if (minRiskFilter) params.min_risk = minRiskFilter;
      if (maxRiskFilter) params.max_risk = maxRiskFilter;

      const response = await apiClient.get('/transactions/', { params });
      
      setTransactions(response.data.results || []);
      setTotalCount(response.data.count || 0);
    } catch (err) {
      console.error('Error loading transactions:', err);
      setError('Failed to load transactions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, riskTierFilter, minRiskFilter, maxRiskFilter]);

  useEffect(() => {
    loadTransactions();
  }, [currentPage, pageSize, searchTerm, riskTierFilter, minRiskFilter, maxRiskFilter]);

  const totalPages = Math.ceil(totalCount / pageSize);

  if (loading && transactions.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Transactions</h1>
        <p className={styles.subtitle}>Search and filter transaction records</p>
        <button onClick={loadTransactions} className={styles.refreshButton}>
          ↻ Refresh
        </button>
      </div>

      {/* Filters Section */}
      <div className={styles.filtersSection}>
        <h2>Filters</h2>
        <div className={styles.filterGrid}>
          <div className={styles.filterGroup}>
            <label>Search Case ID</label>
            <input
              type="text"
              placeholder="Enter case ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={styles.filterInput}
            />
          </div>

          <div className={styles.filterGroup}>
            <label>Risk Tier</label>
            <select
              value={riskTierFilter}
              onChange={(e) => setRiskTierFilter(e.target.value)}
              className={styles.filterSelect}
            >
              <option value="">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label>Min Risk Score</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              placeholder="0.00"
              value={minRiskFilter}
              onChange={(e) => setMinRiskFilter(e.target.value)}
              className={styles.filterInput}
            />
          </div>

          <div className={styles.filterGroup}>
            <label>Max Risk Score</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              placeholder="1.00"
              value={maxRiskFilter}
              onChange={(e) => setMaxRiskFilter(e.target.value)}
              className={styles.filterInput}
            />
          </div>
        </div>
      </div>

      {error && (
        <div className={styles.errorMessage}>
          {error}
        </div>
      )}

      {/* Transactions Table */}
      <div className={styles.tableSection}>
        <div className={styles.tableHeader}>
          <span>Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} transactions</span>
          <div className={styles.pageSizeSelector}>
            <label>Page size:</label>
            <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {transactions.length > 0 ? (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Age</th>
                  <th>Risk Score</th>
                  <th>Risk Tier</th>
                  <th>Alerts</th>
                  <th>Created Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id} className={styles[`risk-${tx.risk_tier}`]}>
                    <td className={styles.caseIdCell}>{tx.caseid}</td>
                    <td>{tx.age}</td>
                    <td className={styles.riskScoreCell}>
                      <span className={styles.riskScore}>{tx.final_risk.toFixed(3)}</span>
                    </td>
                    <td>
                      <span className={`${styles.riskTierBadge} ${styles[`badge-${tx.risk_tier}`]}`}>
                        {tx.risk_tier.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      {tx.has_alerts ? (
                        <span className={styles.alertIcon}>⚠️ Active</span>
                      ) : (
                        <span className={styles.noAlert}>✅ None</span>
                      )}
                    </td>
                    <td className={styles.dateCell}>
                      {new Date(tx.created_at).toLocaleDateString()}
                    </td>
                    <td className={styles.actionsCell}>
                      <button
                        className={styles.detailButton}
                        onClick={() => setSelectedTransaction(tx)}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.noData}>
            <p>No transactions found</p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className={styles.pagination}>
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              className={styles.paginationButton}
            >
              ← Previous
            </button>
            <span className={styles.pageIndicator}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              className={styles.paginationButton}
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedTransaction && (
        <TransactionDetailModal
          transaction={selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
        />
      )}
    </div>
  );
};

export default Transactions;
