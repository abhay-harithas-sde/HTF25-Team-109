import React, { useState, useEffect } from 'react';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(7);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/analytics?days=${timeRange}`);
      const result = await response.json();
      if (result.success) {
        setAnalytics(result.analytics);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateAverage = (data) => {
    if (!data || data.length === 0) return 0;
    const sum = data.reduce((acc, item) => acc + item.calories, 0);
    return Math.round(sum / data.length);
  };

  const getMacroPercentage = (macro, total) => {
    if (total === 0) return 0;
    return Math.round((macro / total) * 100);
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="no-data">No analytics data available</div>;
  }

  const totalMacros = analytics.macros.protein + analytics.macros.carbs + analytics.macros.fat;

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h2>📊 Nutrition Analytics</h2>
        <div className="time-range-selector">
          <label>Time Range:</label>
          <select value={timeRange} onChange={(e) => setTimeRange(parseInt(e.target.value))}>
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 2 weeks</option>
            <option value={30}>Last month</option>
            <option value={90}>Last 3 months</option>
          </select>
        </div>
      </div>

      <div className="analytics-grid">
        {/* Calorie Trends */}
        <div className="analytics-card">
          <h3>Daily Calorie Trends</h3>
          <div className="calorie-chart">
            {analytics.daily_calories.map((day, index) => (
              <div key={index} className="chart-day">
                <div 
                  className="calorie-bar"
                  style={{
                    height: `${Math.min((day.calories / 3000) * 100, 100)}%`
                  }}
                  title={`${day.date}: ${day.calories} calories`}
                ></div>
                <span className="day-label">
                  {new Date(day.date).toLocaleDateString('en', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </span>
              </div>
            ))}
          </div>
          <div className="chart-stats">
            <div className="stat">
              <span className="label">Average:</span>
              <span className="value">{calculateAverage(analytics.daily_calories)} cal</span>
            </div>
            <div className="stat">
              <span className="label">Total Days:</span>
              <span className="value">{analytics.daily_calories.length}</span>
            </div>
          </div>
        </div>

        {/* Macro Breakdown */}
        <div className="analytics-card">
          <h3>Macronutrient Breakdown</h3>
          <div className="macro-chart">
            <div className="macro-pie">
              <div 
                className="macro-segment protein"
                style={{
                  '--percentage': `${getMacroPercentage(analytics.macros.protein * 4, totalMacros * 4)}%`
                }}
              ></div>
              <div 
                className="macro-segment carbs"
                style={{
                  '--percentage': `${getMacroPercentage(analytics.macros.carbs * 4, totalMacros * 4)}%`
                }}
              ></div>
              <div 
                className="macro-segment fat"
                style={{
                  '--percentage': `${getMacroPercentage(analytics.macros.fat * 9, totalMacros * 4)}%`
                }}
              ></div>
            </div>
            <div className="macro-legend">
              <div className="legend-item">
                <span className="color-box protein"></span>
                <span>Protein: {Math.round(analytics.macros.protein)}g</span>
              </div>
              <div className="legend-item">
                <span className="color-box carbs"></span>
                <span>Carbs: {Math.round(analytics.macros.carbs)}g</span>
              </div>
              <div className="legend-item">
                <span className="color-box fat"></span>
                <span>Fat: {Math.round(analytics.macros.fat)}g</span>
              </div>
              <div className="legend-item">
                <span className="color-box fiber"></span>
                <span>Fiber: {Math.round(analytics.macros.fiber)}g</span>
              </div>
            </div>
          </div>
        </div>

        {/* Frequent Foods */}
        <div className="analytics-card">
          <h3>Most Frequent Foods</h3>
          <div className="frequent-foods">
            {analytics.frequent_foods.map((food, index) => (
              <div key={index} className="food-frequency">
                <div className="food-info">
                  <span className="food-name">{food.food}</span>
                  <span className="food-count">{food.count}x</span>
                </div>
                <div className="frequency-bar">
                  <div 
                    className="frequency-fill"
                    style={{
                      width: `${(food.count / analytics.frequent_foods[0].count) * 100}%`
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Health Insights */}
        <div className="analytics-card">
          <h3>Health Insights</h3>
          <div className="insights">
            <div className="insight">
              <span className="insight-icon">🎯</span>
              <div className="insight-text">
                <strong>Calorie Goal Progress</strong>
                <p>You're averaging {calculateAverage(analytics.daily_calories)} calories per day</p>
              </div>
            </div>
            <div className="insight">
              <span className="insight-icon">🥗</span>
              <div className="insight-text">
                <strong>Fiber Intake</strong>
                <p>Daily fiber: {Math.round(analytics.macros.fiber / timeRange)}g</p>
              </div>
            </div>
            <div className="insight">
              <span className="insight-icon">💪</span>
              <div className="insight-text">
                <strong>Protein Balance</strong>
                <p>Daily protein: {Math.round(analytics.macros.protein / timeRange)}g</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;