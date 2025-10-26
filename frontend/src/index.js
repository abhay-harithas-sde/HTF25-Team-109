import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import './AppWithAuth.css';
import AppWithAuth from './AppWithAuth';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AppWithAuth />
  </React.StrictMode>
);