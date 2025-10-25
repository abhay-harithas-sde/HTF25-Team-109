import React, { useState, useEffect } from 'react';

const MealHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchMealHistory();
  }, []);

  const fetchMealHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/meal-history');
      const result = await response.json();
      if (result.success) {
        setHistory(result.history);
      }
    } catch (error) {
      console.error('Error fetching meal history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTotalCaloriesForDate = (date) => {
    const dayData = history.find(day => day.date === date);
    if (!dayData) return 0;
    
    return dayData.meals.reduce((total, meal) => total + meal.total_calories, 0);
  };

  const getWeeklyAverage = () => {
    if (history.length === 0) return 0;
    const totalCalories = history.reduce((sum, day) => 
      sum + day.meals.reduce((daySum, meal) => daySum + meal.total_calories, 0), 0
    );
    return Math.round(totalCalories / history.length);
  };

  if (loading) {
    return <div className="loading">Loading meal history...</div>;
  }

  return (
    <div className="meal-history">
      <h2>📊 Your Meal History</h2>
      
      <div className="stats-overview">
        <div className="stat-card">
          <h3>Today's Calories</h3>
          <div className="stat-value">{getTotalCaloriesForDate(selectedDate)}</div>
        </div>
        <div className="stat-card">
          <h3>Weekly Average</h3>
          <div className="stat-value">{getWeeklyAverage()}</div>
        </div>
        <div className="stat-card">
          <h3>Days Tracked</h3>
          <div className="stat-value">{history.length}</div>
        </div>
      </div>

      <div className="date-selector">
        <label>Select Date:</label>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          max={new Date().toISOString().split('T')[0]}
        />
      </div>

      <div className="daily-meals">
        {history
          .filter(day => day.date === selectedDate)
          .map((day, dayIndex) => (
            <div key={dayIndex} className="day-meals">
              <h3>Meals for {new Date(day.date).toLocaleDateString()}</h3>
              
              {day.meals.map((meal, mealIndex) => (
                <div key={mealIndex} className="meal-entry">
                  <div className="meal-header">
                    <span className="meal-time">{meal.time}</span>
                    <span className="meal-calories">{meal.total_calories} cal</span>
                  </div>
                  
                  <div className="meal-foods">
                    {meal.food_items.map((food, foodIndex) => (
                      <span key={foodIndex} className="food-tag">
                        {food}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              
              <div className="day-total">
                <strong>
                  Daily Total: {day.meals.reduce((sum, meal) => sum + meal.total_calories, 0)} calories
                </strong>
              </div>
            </div>
          ))}
        
        {history.filter(day => day.date === selectedDate).length === 0 && (
          <div className="no-meals">
            <p>No meals recorded for this date.</p>
            <p>Start by uploading a photo of your food!</p>
          </div>
        )}
      </div>

      <div className="weekly-chart">
        <h3>Weekly Calorie Trend</h3>
        <div className="chart-placeholder">
          {history.slice(-7).map((day, index) => (
            <div key={index} className="chart-bar">
              <div 
                className="bar" 
                style={{
                  height: `${Math.min(day.meals.reduce((sum, meal) => sum + meal.total_calories, 0) / 30, 100)}px`
                }}
              ></div>
              <span className="bar-label">
                {new Date(day.date).toLocaleDateString('en', { weekday: 'short' })}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MealHistory;