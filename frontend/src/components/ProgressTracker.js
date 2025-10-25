import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ProgressTracker = ({ dailyStats }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [achievements, setAchievements] = useState([]);
  const [weeklyProgress, setWeeklyProgress] = useState([]);

  useEffect(() => {
    // Show progress tracker when user makes significant progress
    const totalCalories = dailyStats.calories;
    const calorieGoal = 2000; // This should come from user preferences
    
    if (totalCalories > 0 && totalCalories >= calorieGoal * 0.25) {
      setIsVisible(true);
      checkAchievements();
    }
  }, [dailyStats]);

  useEffect(() => {
    loadWeeklyProgress();
  }, []);

  const loadWeeklyProgress = async () => {
    // Mock weekly progress data
    const mockData = [
      { day: 'Mon', calories: 1850, goal: 2000 },
      { day: 'Tue', calories: 2100, goal: 2000 },
      { day: 'Wed', calories: 1950, goal: 2000 },
      { day: 'Thu', calories: 2200, goal: 2000 },
      { day: 'Fri', calories: 1800, goal: 2000 },
      { day: 'Sat', calories: 2300, goal: 2000 },
      { day: 'Sun', calories: dailyStats.calories, goal: 2000 }
    ];
    setWeeklyProgress(mockData);
  };

  const checkAchievements = () => {
    const newAchievements = [];
    
    // Check various achievement conditions
    if (dailyStats.calories >= 2000) {
      newAchievements.push({
        id: 'calorie_goal',
        title: 'Calorie Goal Reached!',
        description: 'You\'ve met your daily calorie target',
        icon: '🎯',
        type: 'daily'
      });
    }

    if (dailyStats.protein >= 100) {
      newAchievements.push({
        id: 'protein_power',
        title: 'Protein Powerhouse!',
        description: 'Excellent protein intake today',
        icon: '💪',
        type: 'nutrition'
      });
    }

    if (dailyStats.water >= 8) {
      newAchievements.push({
        id: 'hydration_hero',
        title: 'Hydration Hero!',
        description: 'You\'ve stayed well hydrated',
        icon: '💧',
        type: 'health'
      });
    }

    // Check streak achievements
    const currentStreak = localStorage.getItem('tracking_streak') || 0;
    if (currentStreak >= 7) {
      newAchievements.push({
        id: 'week_streak',
        title: 'Week Warrior!',
        description: '7 days of consistent tracking',
        icon: '🔥',
        type: 'streak'
      });
    }

    setAchievements(newAchievements);
  };

  const getProgressPercentage = (current, goal) => {
    return Math.min((current / goal) * 100, 100);
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 90) return '#10b981'; // Green
    if (percentage >= 70) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="progress-tracker"
        initial={{ opacity: 0, x: 300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 300 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <div className="tracker-header">
          <h3>📊 Today's Progress</h3>
          <button 
            className="minimize-btn"
            onClick={() => setIsVisible(false)}
          >
            ➖
          </button>
        </div>

        {/* Daily Progress Rings */}
        <div className="progress-rings">
          <div className="progress-ring">
            <svg width="80" height="80" viewBox="0 0 80 80">
              <circle
                cx="40"
                cy="40"
                r="35"
                stroke="#e5e7eb"
                strokeWidth="6"
                fill="none"
              />
              <circle
                cx="40"
                cy="40"
                r="35"
                stroke={getProgressColor(getProgressPercentage(dailyStats.calories, 2000))}
                strokeWidth="6"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 35}`}
                strokeDashoffset={`${2 * Math.PI * 35 * (1 - getProgressPercentage(dailyStats.calories, 2000) / 100)}`}
                strokeLinecap="round"
                transform="rotate(-90 40 40)"
              />
            </svg>
            <div className="ring-content">
              <span className="ring-value">{Math.round(dailyStats.calories)}</span>
              <span className="ring-label">cal</span>
            </div>
          </div>

          <div className="progress-ring">
            <svg width="60" height="60" viewBox="0 0 60 60">
              <circle
                cx="30"
                cy="30"
                r="25"
                stroke="#e5e7eb"
                strokeWidth="4"
                fill="none"
              />
              <circle
                cx="30"
                cy="30"
                r="25"
                stroke="#3b82f6"
                strokeWidth="4"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 25}`}
                strokeDashoffset={`${2 * Math.PI * 25 * (1 - Math.min(dailyStats.protein / 100, 1))}`}
                strokeLinecap="round"
                transform="rotate(-90 30 30)"
              />
            </svg>
            <div className="ring-content">
              <span className="ring-value">{Math.round(dailyStats.protein)}</span>
              <span className="ring-label">g</span>
            </div>
          </div>

          <div className="progress-ring">
            <svg width="60" height="60" viewBox="0 0 60 60">
              <circle
                cx="30"
                cy="30"
                r="25"
                stroke="#e5e7eb"
                strokeWidth="4"
                fill="none"
              />
              <circle
                cx="30"
                cy="30"
                r="25"
                stroke="#06b6d4"
                strokeWidth="4"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 25}`}
                strokeDashoffset={`${2 * Math.PI * 25 * (1 - Math.min(dailyStats.water / 8, 1))}`}
                strokeLinecap="round"
                transform="rotate(-90 30 30)"
              />
            </svg>
            <div className="ring-content">
              <span className="ring-value">{dailyStats.water || 0}</span>
              <span className="ring-label">💧</span>
            </div>
          </div>
        </div>

        {/* Weekly Progress Chart */}
        <div className="weekly-chart">
          <h4>📈 This Week</h4>
          <div className="chart-bars">
            {weeklyProgress.map((day, index) => (
              <div key={day.day} className="chart-bar">
                <div 
                  className="bar"
                  style={{ 
                    height: `${(day.calories / day.goal) * 100}%`,
                    backgroundColor: getProgressColor((day.calories / day.goal) * 100)
                  }}
                />
                <span className="bar-label">{day.day}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Achievements */}
        {achievements.length > 0 && (
          <div className="achievements-section">
            <h4>🏆 Today's Achievements</h4>
            <div className="achievements-list">
              {achievements.map((achievement, index) => (
                <motion.div
                  key={achievement.id}
                  className={`achievement-item ${achievement.type}`}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.2 }}
                >
                  <div className="achievement-icon">{achievement.icon}</div>
                  <div className="achievement-content">
                    <h5>{achievement.title}</h5>
                    <p>{achievement.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Stats */}
        <div className="quick-stats">
          <div className="stat-item">
            <span className="stat-icon">🔥</span>
            <div className="stat-content">
              <span className="stat-value">{Math.round(dailyStats.calories)}</span>
              <span className="stat-label">Calories</span>
            </div>
          </div>
          <div className="stat-item">
            <span className="stat-icon">💪</span>
            <div className="stat-content">
              <span className="stat-value">{Math.round(dailyStats.protein)}g</span>
              <span className="stat-label">Protein</span>
            </div>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🥖</span>
            <div className="stat-content">
              <span className="stat-value">{Math.round(dailyStats.carbs)}g</span>
              <span className="stat-label">Carbs</span>
            </div>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🥑</span>
            <div className="stat-content">
              <span className="stat-value">{Math.round(dailyStats.fat)}g</span>
              <span className="stat-label">Fat</span>
            </div>
          </div>
        </div>

        {/* Motivational Message */}
        <div className="motivation-section">
          <div className="motivation-message">
            {dailyStats.calories >= 2000 ? (
              <p>🎉 Amazing! You've reached your calorie goal today!</p>
            ) : dailyStats.calories >= 1500 ? (
              <p>💪 Great progress! You're on track to meet your goals!</p>
            ) : (
              <p>🌟 Keep going! Every healthy choice counts!</p>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ProgressTracker;