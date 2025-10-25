import React from 'react';
import { motion } from 'framer-motion';

const LoadingSpinner = ({ message = "🔍 Analyzing your food with AI..." }) => {
  return (
    <div className="loading-spinner-container">
      <motion.div
        className="loading-spinner"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      >
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </motion.div>
      
      <motion.div
        className="loading-message"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {message}
      </motion.div>
      
      <motion.div
        className="loading-dots"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <motion.span
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
        >
          •
        </motion.span>
        <motion.span
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
        >
          •
        </motion.span>
        <motion.span
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
        >
          •
        </motion.span>
      </motion.div>
      
      <div className="loading-features">
        <motion.div
          className="feature-item"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1 }}
        >
          🤖 AI-powered food recognition
        </motion.div>
        <motion.div
          className="feature-item"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.2 }}
        >
          📊 Nutritional analysis
        </motion.div>
        <motion.div
          className="feature-item"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.4 }}
        >
          🎯 Portion estimation
        </motion.div>
      </div>
    </div>
  );
};

export default LoadingSpinner;