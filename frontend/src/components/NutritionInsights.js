import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../App';

const NutritionInsights = ({ insights }) => {
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [timeRange, setTimeRange] = useState('week');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAppContext();

  useEffect(() => {
    loadAnalysisData();
  }, [timeRange]);

  const loadAnalysisData = async () => {
    setLoading(true);
    try {
      const days = timeRange === 'week' ? 7 : timeRange === 'month' ? 30 : 90;
      const response = await fetch('/api/ai-nutrition-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, days })
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisData(data.analysis);
      }
    } catch (error) {
      console.error('Failed to load analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      case 'tip': return '💡';
      default: return '📊';
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'success': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      case 'tip': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const generatePersonalizedTips = () => {
    if (!analysisData) return [];

    const tips = [];
    const { summary } = analysisData;

    if (summary.avg_daily_calories < summary.calorie_goal * 0.8) {
      tips.push({
        type: 'tip',
        title: 'Increase Healthy Calories',
        message: 'Try adding nutrient-dense snacks like nuts, avocado, or Greek yogurt to reach your calorie goals.',
        priority: 'high',
        icon: '🥜'
      });
    }

    if (summary.avg_protein < 50) {
      tips.push({
        type: 'tip',
        title: 'Boost Your Protein',
        message: 'Include protein-rich foods like lean meats, eggs, legumes, or protein shakes in your meals.',
        priority: 'medium',
        icon: '🥩'
      });
    }

    tips.push({
      type: 'tip',
      title: 'Hydration Reminder',
      message: 'Aim for 8-10 glasses of water daily. Proper hydration supports metabolism and appetite control.',
      priority: 'medium',
      icon: '💧'
    });

    tips.push({
      type: 'tip',
      title: 'Meal Timing',
      message: 'Try to eat regular meals every 3-4 hours to maintain stable blood sugar and energy levels.',
      priority: 'low',
      icon: '⏰'
    });

    return tips;
  };

  const allInsights = [...(insights || []), ...generatePersonalizedTips()];

  if (loading) {
    return (
      <div className="nutrition-insights loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Analyzing your nutrition data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="nutrition-insights">
      <div className="insights-header">
        <h2>🧠 AI Nutrition Insights</h2>
        <div className="time-range-selector">
          <label>Analysis Period:</label>
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last 3 Months</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      {analysisData && (
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <h3>Daily Average</h3>
              <div className="metric">
                <span className="value">{Math.round(analysisData.summary.avg_daily_calories)}</span>
                <span className="unit">calories</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${Math.min((analysisData.summary.avg_daily_calories / analysisData.summary.calorie_goal) * 100, 100)}%` 
                  }}
                />
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-icon">🎯</div>
            <div className="card-content">
              <h3>Goal Achievement</h3>
              <div className="metric">
                <span className="value">{Math.round(analysisData.summary.goal_achievement)}</span>
                <span className="unit">%</span>
              </div>
              <div className={`status ${analysisData.summary.goal_achievement >= 90 ? 'good' : analysisData.summary.goal_achievement >= 70 ? 'okay' : 'needs-work'}`}>
                {analysisData.summary.goal_achievement >= 90 ? 'Excellent' : 
                 analysisData.summary.goal_achievement >= 70 ? 'Good' : 'Needs Work'}
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-icon">📈</div>
            <div className="card-content">
              <h3>Trend</h3>
              <div className="trend-indicator">
                {analysisData.trends?.calorie_trend === 'increasing' && (
                  <>
                    <span className="trend-arrow up">↗️</span>
                    <span>Increasing</span>
                  </>
                )}
                {analysisData.trends?.calorie_trend === 'decreasing' && (
                  <>
                    <span className="trend-arrow down">↘️</span>
                    <span>Decreasing</span>
                  </>
                )}
                {analysisData.trends?.calorie_trend === 'stable' && (
                  <>
                    <span className="trend-arrow stable">➡️</span>
                    <span>Stable</span>
                  </>
                )}
              </div>
              {analysisData.trends?.change_percentage && (
                <div className="change-percentage">
                  {Math.abs(analysisData.trends.change_percentage)}% change
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Insights Grid */}
      <div className="insights-grid">
        {allInsights.map((insight, index) => (
          <motion.div
            key={index}
            className={`insight-card ${insight.type} ${insight.priority || 'medium'}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setSelectedInsight(insight)}
          >
            <div className="insight-header">
              <div 
                className="insight-icon"
                style={{ color: getInsightColor(insight.type) }}
              >
                {insight.icon || getInsightIcon(insight.type)}
              </div>
              <div className="insight-priority">
                {insight.priority === 'high' && '🔥'}
                {insight.priority === 'medium' && '⭐'}
                {insight.priority === 'low' && '💡'}
              </div>
            </div>
            
            <div className="insight-content">
              <h3>{insight.title}</h3>
              <p>{insight.message}</p>
            </div>
            
            <div className="insight-footer">
              <button className="learn-more-btn">
                Learn More →
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recommendations Section */}
      {analysisData?.recommendations && (
        <div className="recommendations-section">
          <h3>🎯 Personalized Recommendations</h3>
          <div className="recommendations-grid">
            {analysisData.recommendations.map((rec, index) => (
              <motion.div
                key={index}
                className={`recommendation-card ${rec.priority}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="rec-icon">{rec.icon}</div>
                <div className="rec-content">
                  <h4>{rec.title}</h4>
                  <p>{rec.message}</p>
                  <span className="rec-category">{rec.category}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Insight Modal */}
      <AnimatePresence>
        {selectedInsight && (
          <motion.div
            className="insight-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedInsight(null)}
          >
            <motion.div
              className="insight-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <div className="modal-icon">{selectedInsight.icon || getInsightIcon(selectedInsight.type)}</div>
                <h2>{selectedInsight.title}</h2>
                <button 
                  className="close-modal"
                  onClick={() => setSelectedInsight(null)}
                >
                  ✕
                </button>
              </div>
              
              <div className="modal-content">
                <p className="insight-description">{selectedInsight.message}</p>
                
                <div className="insight-details">
                  <h4>Why this matters:</h4>
                  <p>
                    {selectedInsight.type === 'warning' && 
                      "This insight highlights an area where your nutrition could be improved for better health outcomes."}
                    {selectedInsight.type === 'success' && 
                      "Great job! You're doing well in this area. Keep up the good work!"}
                    {selectedInsight.type === 'info' && 
                      "This information can help you make more informed decisions about your nutrition."}
                    {selectedInsight.type === 'tip' && 
                      "This tip is based on nutrition science and your personal eating patterns."}
                  </p>
                </div>
                
                <div className="action-suggestions">
                  <h4>What you can do:</h4>
                  <ul>
                    {selectedInsight.type === 'warning' && selectedInsight.title.includes('Calorie') && (
                      <>
                        <li>Add healthy snacks between meals</li>
                        <li>Include more calorie-dense nutritious foods</li>
                        <li>Consider consulting with a nutritionist</li>
                      </>
                    )}
                    {selectedInsight.type === 'tip' && selectedInsight.title.includes('Protein') && (
                      <>
                        <li>Include protein in every meal</li>
                        <li>Try protein-rich snacks like Greek yogurt</li>
                        <li>Consider a protein supplement if needed</li>
                      </>
                    )}
                    {selectedInsight.type === 'tip' && selectedInsight.title.includes('Hydration') && (
                      <>
                        <li>Set reminders to drink water regularly</li>
                        <li>Keep a water bottle with you</li>
                        <li>Try infused water for variety</li>
                      </>
                    )}
                  </ul>
                </div>
              </div>
              
              <div className="modal-actions">
                <button className="action-btn primary">
                  Set Reminder
                </button>
                <button className="action-btn secondary">
                  Learn More
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NutritionInsights;