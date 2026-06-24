/**
 * API utility functions for fraud detection dashboard
 */

import axios from 'axios';

// Configure base URL for API requests
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Fetch dashboard statistics
 * @returns {Promise<Object>} Dashboard statistics object
 */
export const fetchDashboardStats = async () => {
  try {
    const response = await apiClient.get('/dashboard/stats/');
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};

/**
 * Fetch transactions with optional filters
 * @param {Object} filters - Filter parameters
 * @returns {Promise<Object>} Transactions response
 */
export const fetchTransactions = async (filters = {}) => {
  try {
    const response = await apiClient.get('/transactions/', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Error fetching transactions:', error);
    throw error;
  }
};

/**
 * Fetch unresolved alerts
 * @returns {Promise<Object>} Alerts response
 */
export const fetchAlerts = async () => {
  try {
    const response = await apiClient.get('/alerts/');
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};

/**
 * Score a new transaction
 * @param {Object} transactionData - Transaction data to score
 * @returns {Promise<Object>} Scoring result
 */
export const scoreTransaction = async (transactionData) => {
  try {
    const response = await apiClient.post('/score/', transactionData);
    return response.data;
  } catch (error) {
    console.error('Error scoring transaction:', error);
    throw error;
  }
};

/**
 * Resolve an alert
 * @param {number} alertId - Alert ID
 * @returns {Promise<Object>} Updated alert
 */
export const resolveAlert = async (alertId) => {
  try {
    const response = await apiClient.patch(`/alerts/${alertId}/resolve/`);
    return response.data;
  } catch (error) {
    console.error('Error resolving alert:', error);
    throw error;
  }
};

/**
 * Generate a PDF report
 * @param {string} reportType - Report type (daily, weekly, monthly)
 * @returns {Promise<Blob>} PDF file blob
 */
export const generateReport = async (reportType = 'daily') => {
  try {
    const response = await apiClient.post(
      '/reports/generate/',
      { report_type: reportType },
      { responseType: 'blob' }
    );
    return response.data;
  } catch (error) {
    console.error('Error generating report:', error);
    throw error;
  }
};

export default apiClient;
