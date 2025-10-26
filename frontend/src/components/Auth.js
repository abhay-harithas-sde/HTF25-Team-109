import React, { useState, useContext } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, User, Mail, Lock, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';

// Auth Context for managing authentication state
const AuthContext = React.createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);

  const login = async (credentials) => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (response.ok) {
        setUser(data.user);
        setIsAuthenticated(true);
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        return { success: true, user: data.user };
      } else {
        return { success: false, error: data.error || 'Login failed' };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  const signup = async (userData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (response.ok) {
        setUser(data.user);
        setIsAuthenticated(true);
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        return { success: true, user: data.user };
      } else {
        return { success: false, error: data.error || 'Signup failed' };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const Auth = ({ onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    height: '',
    weight: '',
    age: '',
    gender: 'other',
    activityLevel: 'moderate',
    dailyCalorieGoal: 2000,
    dietaryRestrictions: [],
    fitnessGoals: []
  });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const { login, signup, loading } = useAuth();

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (name === 'dietaryRestrictions' || name === 'fitnessGoals') {
        setFormData(prev => ({
          ...prev,
          [name]: checked 
            ? [...prev[name], value]
            : prev[name].filter(item => item !== value)
        }));
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    // Confirm password validation (only for signup)
    if (!isLogin) {
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }

      // Additional signup validations
      if (formData.age && (formData.age < 13 || formData.age > 120)) {
        newErrors.age = 'Please enter a valid age';
      }

      if (formData.height && (formData.height < 100 || formData.height > 250)) {
        newErrors.height = 'Please enter a valid height in cm';
      }

      if (formData.weight && (formData.weight < 30 || formData.weight > 300)) {
        newErrors.weight = 'Please enter a valid weight in kg';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setMessage('');
    setMessageType('');

    try {
      let result;
      
      if (isLogin) {
        result = await login({
          email: formData.email,
          password: formData.password
        });
      } else {
        result = await signup(formData);
      }

      if (result.success) {
        setMessage(isLogin ? 'Login successful!' : 'Account created successfully!');
        setMessageType('success');
        setTimeout(() => {
          onClose && onClose();
        }, 1500);
      } else {
        setMessage(result.error);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('An unexpected error occurred. Please try again.');
      setMessageType('error');
    }
  };

  const dietaryOptions = [
    'vegetarian', 'vegan', 'gluten_free', 'dairy_free', 'keto', 'paleo', 'low_carb', 'halal', 'kosher'
  ];

  const fitnessGoalOptions = [
    'weight_loss', 'weight_gain', 'muscle_gain', 'maintenance', 'athletic_performance', 'general_health'
  ];

  return (
    <div className="auth-overlay">
      <motion.div
        className="auth-container"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ duration: 0.3 }}
      >
        <div className="auth-header">
          <h2>{isLogin ? 'Welcome Back' : 'Join FoodVision AI'}</h2>
          <p>{isLogin ? 'Sign in to your account' : 'Create your account to get started'}</p>
        </div>

        {message && (
          <motion.div
            className={`auth-message ${messageType}`}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {messageType === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
            {message}
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <AnimatePresence mode="wait">
            {isLogin ? (
              <motion.div
                key="login"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={18} />
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
                      className={errors.email ? 'error' : ''}
                    />
                  </div>
                  {errors.email && <span className="error-text">{errors.email}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={18} />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password"
                      className={errors.password ? 'error' : ''}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {errors.password && <span className="error-text">{errors.password}</span>}
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="signup"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <div className="input-wrapper">
                      <User className="input-icon" size={18} />
                      <input
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        placeholder="Choose a username"
                        className={errors.username ? 'error' : ''}
                      />
                    </div>
                    {errors.username && <span className="error-text">{errors.username}</span>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="email">Email Address</label>
                    <div className="input-wrapper">
                      <Mail className="input-icon" size={18} />
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        placeholder="Enter your email"
                        className={errors.email ? 'error' : ''}
                      />
                    </div>
                    {errors.email && <span className="error-text">{errors.email}</span>}
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <div className="input-wrapper">
                      <Lock className="input-icon" size={18} />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        placeholder="Create a password"
                        className={errors.password ? 'error' : ''}
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                    {errors.password && <span className="error-text">{errors.password}</span>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <div className="input-wrapper">
                      <Lock className="input-icon" size={18} />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        placeholder="Confirm your password"
                        className={errors.confirmPassword ? 'error' : ''}
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      >
                        {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                    {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
                  </div>
                </div>

                <div className="form-section">
                  <h3>Personal Information (Optional)</h3>
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="age">Age</label>
                      <input
                        type="number"
                        id="age"
                        name="age"
                        value={formData.age}
                        onChange={handleInputChange}
                        placeholder="Your age"
                        min="13"
                        max="120"
                        className={errors.age ? 'error' : ''}
                      />
                      {errors.age && <span className="error-text">{errors.age}</span>}
                    </div>

                    <div className="form-group">
                      <label htmlFor="gender">Gender</label>
                      <select
                        id="gender"
                        name="gender"
                        value={formData.gender}
                        onChange={handleInputChange}
                      >
                        <option value="other">Prefer not to say</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="height">Height (cm)</label>
                      <input
                        type="number"
                        id="height"
                        name="height"
                        value={formData.height}
                        onChange={handleInputChange}
                        placeholder="Height in cm"
                        min="100"
                        max="250"
                        className={errors.height ? 'error' : ''}
                      />
                      {errors.height && <span className="error-text">{errors.height}</span>}
                    </div>

                    <div className="form-group">
                      <label htmlFor="weight">Weight (kg)</label>
                      <input
                        type="number"
                        id="weight"
                        name="weight"
                        value={formData.weight}
                        onChange={handleInputChange}
                        placeholder="Weight in kg"
                        min="30"
                        max="300"
                        className={errors.weight ? 'error' : ''}
                      />
                      {errors.weight && <span className="error-text">{errors.weight}</span>}
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="activityLevel">Activity Level</label>
                    <select
                      id="activityLevel"
                      name="activityLevel"
                      value={formData.activityLevel}
                      onChange={handleInputChange}
                    >
                      <option value="sedentary">Sedentary (little/no exercise)</option>
                      <option value="light">Light (light exercise 1-3 days/week)</option>
                      <option value="moderate">Moderate (moderate exercise 3-5 days/week)</option>
                      <option value="active">Active (hard exercise 6-7 days/week)</option>
                      <option value="very_active">Very Active (very hard exercise, physical job)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="dailyCalorieGoal">Daily Calorie Goal</label>
                    <input
                      type="number"
                      id="dailyCalorieGoal"
                      name="dailyCalorieGoal"
                      value={formData.dailyCalorieGoal}
                      onChange={handleInputChange}
                      placeholder="2000"
                      min="1000"
                      max="5000"
                    />
                  </div>

                  <div className="form-group">
                    <label>Dietary Restrictions</label>
                    <div className="checkbox-group">
                      {dietaryOptions.map(option => (
                        <label key={option} className="checkbox-label">
                          <input
                            type="checkbox"
                            name="dietaryRestrictions"
                            value={option}
                            checked={formData.dietaryRestrictions.includes(option)}
                            onChange={handleInputChange}
                          />
                          <span>{option.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Fitness Goals</label>
                    <div className="checkbox-group">
                      {fitnessGoalOptions.map(option => (
                        <label key={option} className="checkbox-label">
                          <input
                            type="checkbox"
                            name="fitnessGoals"
                            value={option}
                            checked={formData.fitnessGoals.includes(option)}
                            onChange={handleInputChange}
                          />
                          <span>{option.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            type="submit"
            className="auth-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <div className="loading-spinner" />
            ) : (
              <>
                {isLogin ? 'Sign In' : 'Create Account'}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-switch">
          <p>
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setErrors({});
                setMessage('');
                setFormData({
                  username: '',
                  email: '',
                  password: '',
                  confirmPassword: '',
                  height: '',
                  weight: '',
                  age: '',
                  gender: 'other',
                  activityLevel: 'moderate',
                  dailyCalorieGoal: 2000,
                  dietaryRestrictions: [],
                  fitnessGoals: []
                });
              }}
              className="switch-btn"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>

        {onClose && (
          <button
            type="button"
            className="auth-close-btn"
            onClick={onClose}
          >
            ×
          </button>
        )}
      </motion.div>
    </div>
  );
};

export default Auth;