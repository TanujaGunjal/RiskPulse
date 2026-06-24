/**
 * Example App Component - How to Use the Dashboard
 * 
 * This is a simple example showing how to integrate the Dashboard component
 * into a React application.
 */

import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;

/**
 * ============================================================================
 * EXAMPLE WITH REACT ROUTER (Multi-page Application)
 * ============================================================================
 * 
 * import React from 'react';
 * import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
 * import Dashboard from './components/Dashboard';
 * import Transactions from './pages/Transactions';
 * import Alerts from './pages/Alerts';
 * import './App.css';
 * 
 * function App() {
 *   return (
 *     <Router>
 *       <nav className="navbar">
 *         <Link to="/">Dashboard</Link>
 *         <Link to="/transactions">Transactions</Link>
 *         <Link to="/alerts">Alerts</Link>
 *       </nav>
 *       
 *       <Routes>
 *         <Route path="/" element={<Dashboard />} />
 *         <Route path="/transactions" element={<Transactions />} />
 *         <Route path="/alerts" element={<Alerts />} />
 *       </Routes>
 *     </Router>
 *   );
 * }
 * 
 * export default App;
 * 
 * ============================================================================
 * EXAMPLE WITH CONTEXT API (Global State)
 * ============================================================================
 * 
 * import React, { createContext, useState } from 'react';
 * import Dashboard from './components/Dashboard';
 * 
 * export const AppContext = createContext();
 * 
 * function App() {
 *   const [user, setUser] = useState(null);
 *   const [theme, setTheme] = useState('light');
 * 
 *   return (
 *     <AppContext.Provider value={{ user, setUser, theme, setTheme }}>
 *       <div className="App">
 *         <Dashboard />
 *       </div>
 *     </AppContext.Provider>
 *   );
 * }
 * 
 * export default App;
 * 
 * ============================================================================
 * EXAMPLE WITH AUTHENTICATION
 * ============================================================================
 * 
 * import React, { useState, useEffect } from 'react';
 * import Dashboard from './components/Dashboard';
 * import LoginPage from './pages/LoginPage';
 * 
 * function App() {
 *   const [isAuthenticated, setIsAuthenticated] = useState(false);
 *   const [loading, setLoading] = useState(true);
 * 
 *   useEffect(() => {
 *     // Check if user is already logged in
 *     const token = localStorage.getItem('authToken');
 *     if (token) {
 *       setIsAuthenticated(true);
 *     }
 *     setLoading(false);
 *   }, []);
 * 
 *   if (loading) {
 *     return <div>Loading...</div>;
 *   }
 * 
 *   return (
 *     <div className="App">
 *       {isAuthenticated ? (
 *         <Dashboard />
 *       ) : (
 *         <LoginPage onLoginSuccess={() => setIsAuthenticated(true)} />
 *       )}
 *     </div>
 *   );
 * }
 * 
 * export default App;
 */
