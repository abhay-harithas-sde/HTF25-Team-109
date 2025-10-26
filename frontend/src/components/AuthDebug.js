import React, { useState } from 'react';
import { authAPI, healthCheck } from '../utils/api';

const AuthDebug = () => {
  const [debugInfo, setDebugInfo] = useState('');
  const [loading, setLoading] = useState(false);

  const testHealthCheck = async () => {
    setLoading(true);
    setDebugInfo('Testing health check...\n');
    
    try {
      const result = await healthCheck();
      setDebugInfo(prev => prev + `Health check result: ${JSON.stringify(result, null, 2)}\n`);
    } catch (error) {
      setDebugInfo(prev => prev + `Health check error: ${error.message}\n`);
    }
    
    setLoading(false);
  };

  const testLogin = async () => {
    setLoading(true);
    setDebugInfo(prev => prev + 'Testing login with test credentials...\n');
    
    try {
      const result = await authAPI.login({
        email: 'test@example.com',
        password: 'testpass123'
      });
      setDebugInfo(prev => prev + `Login result: ${JSON.stringify(result, null, 2)}\n`);
    } catch (error) {
      setDebugInfo(prev => prev + `Login error: ${error.message}\n`);
    }
    
    setLoading(false);
  };

  const testSignup = async () => {
    setLoading(true);
    setDebugInfo(prev => prev + 'Testing signup with test credentials...\n');
    
    try {
      const result = await authAPI.signup({
        username: 'debuguser',
        email: 'debug@example.com',
        password: 'debugpass123',
        age: 25,
        height: 170,
        weight: 70
      });
      setDebugInfo(prev => prev + `Signup result: ${JSON.stringify(result, null, 2)}\n`);
    } catch (error) {
      setDebugInfo(prev => prev + `Signup error: ${error.message}\n`);
    }
    
    setLoading(false);
  };

  const clearDebug = () => {
    setDebugInfo('');
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '1px solid #ccc', 
      padding: '10px', 
      borderRadius: '5px',
      maxWidth: '400px',
      maxHeight: '300px',
      overflow: 'auto',
      zIndex: 9999,
      fontSize: '12px'
    }}>
      <h4>Auth Debug Panel</h4>
      <div style={{ marginBottom: '10px' }}>
        <button onClick={testHealthCheck} disabled={loading} style={{ marginRight: '5px' }}>
          Health Check
        </button>
        <button onClick={testLogin} disabled={loading} style={{ marginRight: '5px' }}>
          Test Login
        </button>
        <button onClick={testSignup} disabled={loading} style={{ marginRight: '5px' }}>
          Test Signup
        </button>
        <button onClick={clearDebug} disabled={loading}>
          Clear
        </button>
      </div>
      <pre style={{ 
        background: '#f5f5f5', 
        padding: '5px', 
        borderRadius: '3px',
        fontSize: '10px',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word'
      }}>
        {debugInfo || 'Click buttons above to test authentication...'}
      </pre>
    </div>
  );
};

export default AuthDebug;