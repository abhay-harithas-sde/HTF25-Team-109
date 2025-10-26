import React, { useState, useEffect, useContext, createContext } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast, Toaster } from 'react-hot-toast';
import './App.css';
import ImageUpload from './components/ImageUpload';
import FoodResults from './components/FoodResults';
import MealHistory from './components/MealHistory';
import Analytics from './components/Analytics';
import Goals from './components/Goals';
import FoodSearch from './components/FoodSearch';
import AIAssistant from './components/AIAssistant';
import MealPlanner from './components/MealPlanner';
import NutritionInsights from './components/NutritionInsights';
import SocialFeatures from './components/SocialFeatures';
import VoiceControl from './components/VoiceControl';
import ProgressTracker from './components/ProgressTracker';
import RecipeGenerator from './components/RecipeGenerator';
import LoadingSpinner from './components/LoadingSpinner';
import Auth, { AuthProvider, useAuth } from './components/Auth';
import './components/Auth.css';

// Create App Context for global state management
const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

function App() {
  // Enhanced state management
  const [currentView, setCurrentView] = useState('dashboard');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [manualFoods, setManualFoods] = useState([]);
  const [user, setUser] = useState({
    id: 1,
    name: 'Demo User',
    email: 'demo@foodvision.com',
    preferences: {
      theme: 'light',
      units: 'metric',
      notifications: true,
      aiMode: 'advanced'
    }
  });
  const [dailyStats, setDailyStats] = useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    water: 0,
    steps: 0
  });
  const [aiInsights, setAiInsights] = useState([]);
  const [mealSuggestions, setMealSuggestions] = useState([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [darkMode, setDarkMode] = useState(false);

  // Context value for global state
  const contextValue = {
    user,
    setUser,
    dailyStats,
    setDailyStats,
    aiInsights,
    setAiInsights,
    mealSuggestions,
    setMealSuggestions,
    darkMode,
    setDarkMode,
    isOnline
  };

  // Check online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Load user preferences
  useEffect(() => {
    const savedPreferences = localStorage.getItem('foodvision_preferences');
    if (savedPreferences) {
      const preferences = JSON.parse(savedPreferences);
      setUser(prev => ({ ...prev, preferences: { ...prev.preferences, ...preferences } }));
      setDarkMode(preferences.theme === 'dark');
    }
  }, []);

  // Load daily stats
  useEffect(() => {
    loadDailyStats();
    loadAIInsights();
    loadMealSuggestions();
  }, []);

  const loadDailyStats = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await fetch(`/api/daily-stats?date=${today}&user_id=${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setDailyStats(data.stats || dailyStats);
      }
    } catch (error) {
      console.error('Failed to load daily stats:', error);
    }
  };

  const loadAIInsights = async () => {
    try {
      const response = await fetch(`/api/ai-nutrition-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, days: 7 })
      });
      if (response.ok) {
        const data = await response.json();
        setAiInsights(data.analysis?.insights || []);
      }
    } catch (error) {
      console.error('Failed to load AI insights:', error);
    }
  };

  const loadMealSuggestions = async () => {
    try {
      const currentHour = new Date().getHours();
      let mealType = 'snack';
      if (currentHour >= 6 && currentHour < 11) mealType = 'breakfast';
      else if (currentHour >= 11 && currentHour < 16) mealType = 'lunch';
      else if (currentHour >= 16 && currentHour < 22) mealType = 'dinner';

      const response = await fetch('/api/ai-meal-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          meal_type: mealType,
          calorie_target: user.preferences?.dailyCalories || 2000,
          dietary_preferences: user.preferences?.dietary || []
        })
      });
      if (response.ok) {
        const data = await response.json();
        setMealSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Failed to load meal suggestions:', error);
    }
  };

  const handleImageAnalysis = async (imageData, options = {}) => {
    setLoading(true);
    const loadingToast = toast.loading('🔍 Analyzing your food with AI...');
    
    try {
      const response = await fetch('/api/analyze-food', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          image: imageData,
          advanced_mode: user.preferences?.aiMode === 'advanced',
          user_id: user.id,
          ...options
        }),
      });

      const result = await response.json();
      if (result.success) {
        setAnalysisResults({
          predictions: result.predictions,
          imagePath: result.image_path,
          processingTime: result.processing_time,
          aiConfidence: result.ai_confidence,
          imageContext: result.image_context,
          portionAnalysis: result.portion_analysis
        });
        setCurrentView('results');
        toast.success('✅ Food analysis complete!', { id: loadingToast });
        
        // Update daily stats if auto-save is enabled
        if (user.preferences?.autoSave) {
          await saveMeal({ items: result.predictions });
        }
      } else {
        toast.error('❌ Error analyzing image: ' + result.error, { id: loadingToast });
      }
    } catch (error) {
      toast.error('❌ Connection error: ' + error.message, { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  const saveMeal = async (mealData, options = {}) => {
    const savingToast = toast.loading('💾 Saving your meal...');
    
    try {
      // Determine meal type based on current time
      const hour = new Date().getHours();
      let mealType = options.mealType || 'snack';
      if (!options.mealType) {
        if (hour >= 6 && hour < 11) mealType = 'breakfast';
        else if (hour >= 11 && hour < 16) mealType = 'lunch';
        else if (hour >= 16 && hour < 22) mealType = 'dinner';
      }

      const response = await fetch('/api/save-meal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...mealData,
          user_id: user.id,
          meal_type: mealType,
          image_path: analysisResults?.imagePath || '',
          ai_confidence: analysisResults?.aiConfidence || 0,
          processing_time: analysisResults?.processingTime || 0,
          location: options.location,
          mood_rating: options.moodRating || 5,
          notes: options.notes || ''
        }),
      });

      const result = await response.json();
      if (result.success) {
        toast.success('✅ Meal saved successfully!', { id: savingToast });
        
        // Update daily stats
        const totalCalories = mealData.items?.reduce((sum, item) => sum + (item.calories || 0), 0) || 0;
        const totalProtein = mealData.items?.reduce((sum, item) => sum + (item.protein || 0), 0) || 0;
        const totalCarbs = mealData.items?.reduce((sum, item) => sum + (item.carbs || 0), 0) || 0;
        const totalFat = mealData.items?.reduce((sum, item) => sum + (item.fat || 0), 0) || 0;
        
        setDailyStats(prev => ({
          ...prev,
          calories: prev.calories + totalCalories,
          protein: prev.protein + totalProtein,
          carbs: prev.carbs + totalCarbs,
          fat: prev.fat + totalFat
        }));
        
        // Navigate based on user preference
        if (options.stayOnResults) {
          // Stay on results page
        } else {
          setCurrentView(options.nextView || 'dashboard');
        }
        
        setAnalysisResults(null);
        setManualFoods([]);
        
        // Reload insights and suggestions
        loadAIInsights();
        loadMealSuggestions();
      } else {
        toast.error('❌ Error saving meal: ' + result.error, { id: savingToast });
      }
    } catch (error) {
      toast.error('❌ Connection error: ' + error.message, { id: savingToast });
    }
  };

  const addManualFood = (food) => {
    setManualFoods(prev => [...prev, { ...food, id: Date.now() }]);
    toast.success(`✅ Added ${food.food_name} to your meal`);
  };

  const removeManualFood = (id) => {
    setManualFoods(prev => prev.filter(food => food.id !== id));
    toast.success('🗑️ Food item removed');
  };

  const updateManualFood = (id, updates) => {
    setManualFoods(prev => prev.map(food => 
      food.id === id ? { ...food, ...updates } : food
    ));
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    const newPreferences = { ...user.preferences, theme: newDarkMode ? 'dark' : 'light' };
    setUser(prev => ({ ...prev, preferences: newPreferences }));
    localStorage.setItem('foodvision_preferences', JSON.stringify(newPreferences));
  };

  const updateUserPreferences = (newPreferences) => {
    const updatedPreferences = { ...user.preferences, ...newPreferences };
    setUser(prev => ({ ...prev, preferences: updatedPreferences }));
    localStorage.setItem('foodvision_preferences', JSON.stringify(updatedPreferences));
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className={`App ${darkMode ? 'dark-mode' : ''}`}>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: darkMode ? '#1f2937' : '#ffffff',
              color: darkMode ? '#ffffff' : '#1f2937',
              border: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '500'
            }
          }}
        />
        
        {/* Enhanced Header with Status Bar */}
        <header className="App-header">
          <div className="header-top">
            <div className="app-title">
              <motion.h1 
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                🍽️ FoodVision AI
              </motion.h1>
              <div className="status-indicators">
                <div className={`status-dot ${isOnline ? 'online' : 'offline'}`} 
                     title={isOnline ? 'Online' : 'Offline'} />
                <div className="ai-status" title="AI Enhanced">🤖</div>
                <button 
                  className="theme-toggle"
                  onClick={toggleDarkMode}
                  title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>
              </div>
            </div>
            
            {/* Daily Progress Bar */}
            <div className="daily-progress">
              <div className="progress-item">
                <span className="progress-label">Calories</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill calories"
                    style={{ width: `${Math.min((dailyStats.calories / (user.preferences?.dailyCalories || 2000)) * 100, 100)}%` }}
                  />
                </div>
                <span className="progress-text">
                  {Math.round(dailyStats.calories)}/{user.preferences?.dailyCalories || 2000}
                </span>
              </div>
            </div>
          </div>
          
          {/* Enhanced Navigation */}
          <nav className="main-nav">
            {[
              { key: 'dashboard', icon: '🏠', label: 'Dashboard' },
              { key: 'upload', icon: '📷', label: 'Scan Food' },
              { key: 'manual', icon: '➕', label: 'Add Manual' },
              { key: 'planner', icon: '📅', label: 'Meal Plan' },
              { key: 'history', icon: '📊', label: 'History' },
              { key: 'analytics', icon: '📈', label: 'Analytics' },
              { key: 'insights', icon: '🧠', label: 'AI Insights' },
              { key: 'recipes', icon: '👨‍🍳', label: 'Recipes' },
              { key: 'goals', icon: '🎯', label: 'Goals' },
              { key: 'social', icon: '👥', label: 'Social' }
            ].map(({ key, icon, label }) => (
              <motion.button
                key={key}
                className={`nav-btn ${currentView === key ? 'active' : ''}`}
                onClick={() => setCurrentView(key)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <span className="nav-icon">{icon}</span>
                <span className="nav-label">{label}</span>
              </motion.button>
            ))}
          </nav>
        </header>

        {/* Voice Control Component */}
        <VoiceControl 
          onCommand={(command) => {
            if (command.includes('scan food')) setCurrentView('upload');
            else if (command.includes('add food')) setCurrentView('manual');
            else if (command.includes('show history')) setCurrentView('history');
            else if (command.includes('analytics')) setCurrentView('analytics');
          }}
        />

        {/* Main Content Area */}
        <main className="App-main">
          <AnimatePresence mode="wait">
            {loading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="loading-container"
              >
                <LoadingSpinner />
              </motion.div>
            )}
            
            {/* Dashboard View */}
            {currentView === 'dashboard' && !loading && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="dashboard-view"
              >
                <div className="dashboard-grid">
                  {/* Quick Stats */}
                  <div className="stats-card">
                    <h3>Today's Progress</h3>
                    <div className="stats-grid">
                      <div className="stat-item">
                        <span className="stat-value">{Math.round(dailyStats.calories)}</span>
                        <span className="stat-label">Calories</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{Math.round(dailyStats.protein)}g</span>
                        <span className="stat-label">Protein</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{Math.round(dailyStats.carbs)}g</span>
                        <span className="stat-label">Carbs</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{Math.round(dailyStats.fat)}g</span>
                        <span className="stat-label">Fat</span>
                      </div>
                    </div>
                  </div>

                  {/* AI Insights Preview */}
                  <div className="insights-preview">
                    <h3>🧠 AI Insights</h3>
                    {aiInsights.slice(0, 2).map((insight, index) => (
                      <div key={index} className="insight-item">
                        <span className="insight-icon">{insight.icon}</span>
                        <div className="insight-content">
                          <strong>{insight.title}</strong>
                          <p>{insight.message}</p>
                        </div>
                      </div>
                    ))}
                    <button 
                      className="view-all-btn"
                      onClick={() => setCurrentView('insights')}
                    >
                      View All Insights
                    </button>
                  </div>

                  {/* Meal Suggestions */}
                  <div className="suggestions-preview">
                    <h3>🍽️ Meal Suggestions</h3>
                    {mealSuggestions.slice(0, 2).map((suggestion, index) => (
                      <div key={index} className="suggestion-item">
                        <h4>{suggestion.name}</h4>
                        <p>{suggestion.description}</p>
                        <div className="suggestion-meta">
                          <span>{suggestion.calories} cal</span>
                          <span>{suggestion.prep_time}</span>
                        </div>
                      </div>
                    ))}
                    <button 
                      className="view-all-btn"
                      onClick={() => setCurrentView('planner')}
                    >
                      View All Suggestions
                    </button>
                  </div>

                  {/* Quick Actions */}
                  <div className="quick-actions">
                    <h3>Quick Actions</h3>
                    <div className="action-buttons">
                      <button 
                        className="action-btn scan"
                        onClick={() => setCurrentView('upload')}
                      >
                        📷 Scan Food
                      </button>
                      <button 
                        className="action-btn manual"
                        onClick={() => setCurrentView('manual')}
                      >
                        ➕ Add Manual
                      </button>
                      <button 
                        className="action-btn recipe"
                        onClick={() => setCurrentView('recipes')}
                      >
                        👨‍🍳 Generate Recipe
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            
            {/* Upload View */}
            {currentView === 'upload' && !loading && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <ImageUpload 
                  onImageAnalysis={handleImageAnalysis}
                  aiMode={user.preferences?.aiMode}
                />
              </motion.div>
            )}
            
            {/* Manual Entry View */}
            {currentView === 'manual' && (
              <motion.div
                key="manual"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="manual-entry"
              >
                <FoodSearch onAddFood={addManualFood} />
                
                {manualFoods.length > 0 && (
                  <div className="manual-foods-list">
                    <h3>Added Foods ({manualFoods.length})</h3>
                    {manualFoods.map((food) => (
                      <div key={food.id} className="manual-food-item">
                        <div className="food-info">
                          <span className="food-name">{food.food_name}</span>
                          <span className="food-portion">{Math.round(food.portion * 100)}g</span>
                          <span className="food-calories">{Math.round(food.calories)} cal</span>
                        </div>
                        <div className="food-actions">
                          <button 
                            onClick={() => updateManualFood(food.id, { 
                              portion: food.portion * 1.1,
                              calories: food.calories * 1.1 
                            })}
                            className="adjust-btn plus"
                            title="Increase portion"
                          >
                            ➕
                          </button>
                          <button 
                            onClick={() => updateManualFood(food.id, { 
                              portion: Math.max(0.1, food.portion * 0.9),
                              calories: Math.max(food.calories * 0.1, food.calories * 0.9)
                            })}
                            className="adjust-btn minus"
                            title="Decrease portion"
                          >
                            ➖
                          </button>
                          <button 
                            onClick={() => removeManualFood(food.id)}
                            className="remove-food-btn"
                            title="Remove food"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    ))}
                    
                    <div className="manual-meal-summary">
                      <div className="total-calories">
                        Total: {Math.round(manualFoods.reduce((sum, food) => sum + food.calories, 0))} calories
                      </div>
                      <div className="meal-actions">
                        <button 
                          onClick={() => saveMeal({ items: manualFoods })}
                          className="save-manual-meal-btn primary"
                        >
                          💾 Save Meal
                        </button>
                        <button 
                          onClick={() => setManualFoods([])}
                          className="clear-meal-btn secondary"
                        >
                          🗑️ Clear All
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* Meal Planner View */}
            {currentView === 'planner' && (
              <motion.div
                key="planner"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <MealPlanner 
                  suggestions={mealSuggestions}
                  onPlanMeal={saveMeal}
                />
              </motion.div>
            )}
            
            {/* Results View */}
            {currentView === 'results' && analysisResults && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <FoodResults 
                  results={analysisResults.predictions} 
                  processingTime={analysisResults.processingTime}
                  aiConfidence={analysisResults.aiConfidence}
                  imageContext={analysisResults.imageContext}
                  onSaveMeal={saveMeal}
                  onBack={() => setCurrentView('upload')}
                />
              </motion.div>
            )}
            
            {/* History View */}
            {currentView === 'history' && (
              <motion.div
                key="history"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <MealHistory />
              </motion.div>
            )}
            
            {/* Analytics View */}
            {currentView === 'analytics' && (
              <motion.div
                key="analytics"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Analytics />
              </motion.div>
            )}

            {/* AI Insights View */}
            {currentView === 'insights' && (
              <motion.div
                key="insights"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <NutritionInsights insights={aiInsights} />
              </motion.div>
            )}

            {/* Recipe Generator View */}
            {currentView === 'recipes' && (
              <motion.div
                key="recipes"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <RecipeGenerator />
              </motion.div>
            )}
            
            {/* Goals View */}
            {currentView === 'goals' && (
              <motion.div
                key="goals"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Goals onUpdatePreferences={updateUserPreferences} />
              </motion.div>
            )}

            {/* Social Features View */}
            {currentView === 'social' && (
              <motion.div
                key="social"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <SocialFeatures />
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* AI Assistant Floating Button */}
        <AIAssistant />

        {/* Progress Tracker */}
        <ProgressTracker dailyStats={dailyStats} />
      </div>
    </AppContext.Provider>
  );
}

export default App;