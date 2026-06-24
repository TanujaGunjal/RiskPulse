/**
 * React Dashboard Setup & Usage Guide
 * 
 * Healthcare Fraud Detection Dashboard Component
 */

/**
 * ============================================================================
 * INSTALLATION
 * ============================================================================
 * 
 * 1. Install Required Dependencies:
 * 
 *    npm install axios recharts
 * 
 *    - axios: HTTP client for API calls
 *    - recharts: React charting library
 * 
 * ============================================================================
 * ENVIRONMENT SETUP
 * ============================================================================
 * 
 * Create a .env file in your React project root:
 * 
 *    REACT_APP_API_URL=http://localhost:8000/api
 * 
 * For production:
 * 
 *    REACT_APP_API_URL=https://api.yourdomain.com/api
 * 
 * ============================================================================
 * BASIC USAGE
 * ============================================================================
 * 
 * In your App.jsx or main component:
 * 
 *    import Dashboard from './components/Dashboard';
 * 
 *    function App() {
 *      return (
 *        <div className="App">
 *          <Dashboard />
 *        </div>
 *      );
 *    }
 * 
 *    export default App;
 * 
 * ============================================================================
 * WITH REACT ROUTER
 * ============================================================================
 * 
 *    import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
 *    import Dashboard from './components/Dashboard';
 * 
 *    function App() {
 *      return (
 *        <Router>
 *          <Routes>
 *            <Route path="/dashboard" element={<Dashboard />} />
 *          </Routes>
 *        </Router>
 *      );
 *    }
 * 
 * ============================================================================
 * AUTHENTICATION SETUP
 * ============================================================================
 * 
 * To add Bearer token authentication to all API calls:
 * 
 * In utils/api.js, the token is automatically included from localStorage:
 * 
 *    // After user login, save token:
 *    localStorage.setItem('authToken', response.data.token);
 * 
 *    // Logout:
 *    localStorage.removeItem('authToken');
 * 
 * ============================================================================
 * FEATURES & STRUCTURE
 * ============================================================================
 * 
 * Dashboard Component (Dashboard.jsx):
 * ├── Header with refresh button
 * ├── KPI Cards Section:
 * │   ├── Total Records
 * │   ├── High Risk Count
 * │   ├── Critical Risk Count
 * │   └── Average Risk Score
 * ├── Charts Section:
 * │   ├── Monthly Fraud Counts (BarChart)
 * │   └── Risk Tier Distribution (PieChart)
 * ├── Top Risk Records Table:
 * │   ├── Case ID
 * │   ├── Final Risk Score
 * │   ├── Risk Percentage (visual bar)
 * │   ├── Risk Tier (badge)
 * │   └── Created Date
 * └── Footer with last update timestamp
 * 
 * API Utilities (utils/api.js):
 * ├── fetchDashboardStats() - Main stats endpoint
 * ├── fetchTransactions() - With optional filters
 * ├── fetchAlerts() - Unresolved alerts
 * ├── scoreTransaction() - New transaction scoring
 * ├── resolveAlert() - Mark alert as resolved
 * └── generateReport() - Generate PDF reports
 * 
 * ============================================================================
 * STATE MANAGEMENT
 * ============================================================================
 * 
 * The component uses React hooks:
 * - useState: Manages loading, error, and stats state
 * - useEffect: Loads dashboard data on mount
 * 
 * To implement global state management (Redux, Context API):
 * 
 *    // With Context API:
 *    const { stats, loading, error } = useContext(DashboardContext);
 * 
 *    // With Redux:
 *    const { stats, loading, error } = useSelector(state => state.dashboard);
 * 
 * ============================================================================
 * STYLING
 * ============================================================================
 * 
 * Uses CSS Modules (Dashboard.module.css) for scoped styling:
 * - Professional color scheme (blues, grays, with risk tier colors)
 * - Responsive grid layout
 * - Smooth transitions and hover effects
 * - Mobile-first responsive design
 * 
 * Color Scheme:
 * - Low Risk: #10B981 (Green)
 * - Medium Risk: #F59E0B (Amber)
 * - High Risk: #EF6B3E (Orange)
 * - Critical Risk: #EF4444 (Red)
 * 
 * ============================================================================
 * RESPONSIVE BREAKPOINTS
 * ============================================================================
 * 
 * Desktop (1024px+):   Full grid layout
 * Tablet (768-1024px): Single column charts
 * Mobile (480-768px):  Adjusted spacing and font sizes
 * Small Mobile (<480px): Stacked layout, reduced padding
 * 
 * ============================================================================
 * CUSTOMIZATION
 * ============================================================================
 * 
 * 1. Change Chart Colors:
 *    Edit getRiskColor() function in Dashboard.jsx
 * 
 * 2. Modify KPI Cards:
 *    Update kpiSection grid and add/remove KPICard components
 * 
 * 3. Adjust Table Display:
 *    Modify formattedTopRecords mapping and table columns
 * 
 * 4. Update API Endpoint:
 *    Set REACT_APP_API_URL environment variable
 * 
 * 5. Add Filters:
 *    Use fetchTransactions() with filter parameters
 * 
 * ============================================================================
 * ERROR HANDLING
 * ============================================================================
 * 
 * The component includes:
 * - Loading spinner during data fetch
 * - Error message display with retry button
 * - Graceful fallbacks for missing data
 * - Console error logging for debugging
 * 
 * ============================================================================
 * PERFORMANCE OPTIMIZATION
 * ============================================================================
 * 
 * - Data fetches only on component mount
 * - Manual refresh button for data updates
 * - CSS module scoping prevents style conflicts
 * - Responsive Container for optimal chart rendering
 * 
 * To add auto-refresh:
 * 
 *    const [refreshInterval, setRefreshInterval] = useState(60000); // 1 min
 *    
 *    useEffect(() => {
 *      const interval = setInterval(loadDashboardData, refreshInterval);
 *      return () => clearInterval(interval);
 *    }, [refreshInterval]);
 * 
 * ============================================================================
 * TESTING
 * ============================================================================
 * 
 * Mock data for testing (utils/mockData.js):
 * 
 *    export const mockStats = {
 *      total_transactions: 1250,
 *      risk_tier_counts: {
 *        low: 800,
 *        medium: 300,
 *        high: 100,
 *        critical: 50
 *      },
 *      average_risk: 0.342,
 *      total_flagged: 150,
 *      monthly_counts: [
 *        { month: '2026-01', count: 180 },
 *        ...
 *      ],
 *      top_risk_records: [
 *        {
 *          id: 42,
 *          caseid: 'CASE042',
 *          final_risk: 0.987,
 *          risk_tier: 'critical',
 *          created_at: '2026-06-24T09:15:00Z'
 *        },
 *        ...
 *      ]
 *    };
 * 
 * Use in component:
 * 
 *    const loadDashboardData = async () => {
 *      // Use mockStats during development:
 *      setStats(mockStats);
 *      setLoading(false);
 *    };
 * 
 * ============================================================================
 * DEPLOYMENT CHECKLIST
 * ============================================================================
 * 
 * - [ ] Install all dependencies (npm install)
 * - [ ] Set production API URL in .env
 * - [ ] Configure CORS on backend
 * - [ ] Test authentication flow
 * - [ ] Test error handling with invalid API responses
 * - [ ] Verify responsive design on mobile devices
 * - [ ] Run production build (npm run build)
 * - [ ] Test on production domain
 * - [ ] Set up monitoring/error tracking (Sentry, etc.)
 * 
 * ============================================================================
 * BACKEND REQUIREMENTS
 * ============================================================================
 * 
 * Ensure Django backend provides:
 * - GET /api/dashboard/stats/ endpoint
 * - Proper CORS headers
 * - Authentication (optional but recommended)
 * - Error responses with meaningful messages
 * 
 * ============================================================================
 */

// Example package.json dependencies to add:
/*
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  }
}
*/
