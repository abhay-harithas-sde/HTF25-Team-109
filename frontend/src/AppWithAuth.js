import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { AuthProvider, useAuth } from './components/Auth';
import Auth from './components/Auth';
import App from './App';
import { User, LogOut, Settings } from 'lucide-react';
import { authAPI, healthCheck } from './utils/api';
import AuthDebug from './components/AuthDebug';

// Main App wrapper with authentication
const AppWithAuth = () => {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  );
};

// Authenticated app component
const AuthenticatedApp = () => {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Check for existing token on app load and verify backend connectivity
  useEffect(() => {
    const initializeApp = async () => {
      // First check if backend is accessible
      try {
        const healthResult = await healthCheck();
        if (!healthResult.success) {
          console.warn('Backend health check failed:', healthResult.error);
          toast.error('Unable to connect to server. Some features may not work.');
        }
      } catch (error) {
        console.warn('Backend health check error:', error);
        toast.error('Unable to connect to server. Some features may not work.');
      }

      // Then check for existing authentication
      const token = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');
      
      if (token && savedUser) {
        // Verify token is still valid
        verifyToken(token);
      }
    };

    initializeApp();
  }, []);

  const verifyToken = async (token) => {
    try {
      const result = await authAPI.verifyToken(token);

      if (!result.success) {
        // Token is invalid, clear storage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        logout();
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      logout();
    }
  };

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
    toast.success('👋 Logged out successfully');
  };

  const handleAuthSuccess = (userData) => {
    setShowAuth(false);
    toast.success(`🎉 Welcome${userData?.username ? `, ${userData.username}` : ''}!`);
  };

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="auth-loading">
        <div className="loading-spinner-container">
          <div className="loading-spinner">
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
          </div>
          <div className="loading-message">Loading FoodVision AI...</div>
        </div>
      </div>
    );
  }

  // Show authentication modal if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="app-container">
        {/* Landing page with login prompt */}
        <div className="landing-page">
          <div className="landing-hero">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="hero-content"
            >
              <div className="app-logo">🍽️</div>
              <h1>FoodVision AI</h1>
              <p className="hero-subtitle">
                Advanced AI-Powered Nutrition Tracking Platform
              </p>
              <div className="hero-features">
                <div className="feature-item">
                  <span className="feature-icon">🤖</span>
                  <span>Multi-AI Food Recognition</span>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">📊</span>
                  <span>Advanced Analytics</span>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">🎯</span>
                  <span>Personalized Goals</span>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">👥</span>
                  <span>Social Features</span>
                </div>
              </div>
              <div className="hero-actions">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="cta-button primary"
                  onClick={() => setShowAuth(true)}
                >
                  Get Started
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="cta-button secondary"
                  onClick={() => setShowAuth(true)}
                >
                  Sign In
                </motion.button>
              </div>
            </motion.div>
          </div>
          
          <div className="landing-features">
            <div className="features-grid">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="feature-card"
              >
                <div className="feature-icon-large">🔍</div>
                <h3>Smart Food Recognition</h3>
                <p>Advanced AI models identify food items with high accuracy using ensemble learning</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="feature-card"
              >
                <div className="feature-icon-large">📱</div>
                <h3>Modern Interface</h3>
                <p>Beautiful, responsive design with dark mode and accessibility features</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="feature-card"
              >
                <div className="feature-icon-large">🧠</div>
                <h3>AI Insights</h3>
                <p>Personalized nutrition recommendations powered by machine learning</p>
              </motion.div>
            </div>
          </div>
        </div>

        {/* Authentication Modal */}
        <AnimatePresence>
          {showAuth && (
            <Auth onClose={() => setShowAuth(false)} onSuccess={handleAuthSuccess} />
          )}
        </AnimatePresence>

        {/* Debug Panel - Remove in production */}
        {process.env.NODE_ENV === 'development' && <AuthDebug />}
      </div>
    );
  }

  // Show main app if authenticated
  return (
    <div className="app-container authenticated">
      {/* User menu in header */}
      <div className="app-header-user">
        <div className="user-info" onClick={() => setShowUserMenu(!showUserMenu)}>
          <div className="user-avatar">
            <User size={20} />
          </div>
          <span className="user-name">{user?.username || 'User'}</span>
        </div>
        
        <AnimatePresence>
          {showUserMenu && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="user-menu"
            >
              <div className="user-menu-header">
                <div className="user-details">
                  <strong>{user?.username}</strong>
                  <span>{user?.email}</span>
                </div>
              </div>
              <div className="user-menu-items">
                <button className="menu-item">
                  <Settings size={16} />
                  Settings
                </button>
                <button className="menu-item logout" onClick={handleLogout}>
                  <LogOut size={16} />
                  Logout
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Main App */}
      <App />
    </div>
  );
};

export default AppWithAuth;