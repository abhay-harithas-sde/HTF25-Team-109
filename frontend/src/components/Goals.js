import React, { useState, useEffect } from 'react';

const Goals = () => {
  const [goals, setGoals] = useState({
    daily_calories: 2000,
    height: '',
    weight: '',
    age: '',
    activity_level: 'moderate'
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/nutrition-goals');
      const result = await response.json();
      if (result.success) {
        setGoals(result.goals);
      }
    } catch (error) {
      console.error('Error fetching goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveGoals = async () => {
    setSaving(true);
    try {
      const response = await fetch('http://localhost:5000/api/nutrition-goals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(goals),
      });

      const result = await response.json();
      if (result.success) {
        alert('Goals updated successfully!');
      } else {
        alert('Error updating goals: ' + result.error);
      }
    } catch (error) {
      alert('Error saving goals: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const calculateBMR = () => {
    if (!goals.weight || !goals.height || !goals.age) return 0;
    
    // Mifflin-St Jeor Equation (assuming male for simplicity)
    const bmr = 10 * goals.weight + 6.25 * goals.height - 5 * goals.age + 5;
    
    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      very_active: 1.9
    };
    
    return Math.round(bmr * activityMultipliers[goals.activity_level]);
  };

  const calculateBMI = () => {
    if (!goals.weight || !goals.height) return 0;
    const heightInMeters = goals.height / 100;
    return (goals.weight / (heightInMeters * heightInMeters)).toFixed(1);
  };

  const getBMICategory = (bmi) => {
    if (bmi < 18.5) return { category: 'Underweight', color: '#3498db' };
    if (bmi < 25) return { category: 'Normal', color: '#2ecc71' };
    if (bmi < 30) return { category: 'Overweight', color: '#f39c12' };
    return { category: 'Obese', color: '#e74c3c' };
  };

  const handleInputChange = (field, value) => {
    setGoals(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading) {
    return <div className="loading">Loading goals...</div>;
  }

  const recommendedCalories = calculateBMR();
  const bmi = calculateBMI();
  const bmiInfo = getBMICategory(bmi);

  return (
    <div className="goals">
      <h2>🎯 Nutrition Goals & Profile</h2>
      
      <div className="goals-grid">
        {/* Personal Information */}
        <div className="goals-card">
          <h3>Personal Information</h3>
          <div className="form-group">
            <label>Height (cm):</label>
            <input
              type="number"
              value={goals.height}
              onChange={(e) => handleInputChange('height', parseFloat(e.target.value))}
              placeholder="170"
            />
          </div>
          
          <div className="form-group">
            <label>Weight (kg):</label>
            <input
              type="number"
              value={goals.weight}
              onChange={(e) => handleInputChange('weight', parseFloat(e.target.value))}
              placeholder="70"
            />
          </div>
          
          <div className="form-group">
            <label>Age:</label>
            <input
              type="number"
              value={goals.age}
              onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
              placeholder="25"
            />
          </div>
          
          <div className="form-group">
            <label>Activity Level:</label>
            <select
              value={goals.activity_level}
              onChange={(e) => handleInputChange('activity_level', e.target.value)}
            >
              <option value="sedentary">Sedentary (little/no exercise)</option>
              <option value="light">Light (light exercise 1-3 days/week)</option>
              <option value="moderate">Moderate (moderate exercise 3-5 days/week)</option>
              <option value="active">Active (hard exercise 6-7 days/week)</option>
              <option value="very_active">Very Active (very hard exercise, physical job)</option>
            </select>
          </div>
        </div>

        {/* Calorie Goals */}
        <div className="goals-card">
          <h3>Daily Calorie Goal</h3>
          <div className="calorie-input">
            <input
              type="number"
              value={goals.daily_calories}
              onChange={(e) => handleInputChange('daily_calories', parseInt(e.target.value))}
              className="calorie-field"
            />
            <span className="calorie-unit">calories/day</span>
          </div>
          
          {recommendedCalories > 0 && (
            <div className="recommendation">
              <p>💡 Recommended: <strong>{recommendedCalories} calories/day</strong></p>
              <button 
                className="use-recommended"
                onClick={() => handleInputChange('daily_calories', recommendedCalories)}
              >
                Use Recommended
              </button>
            </div>
          )}
          
          <div className="calorie-breakdown">
            <h4>Macro Targets (based on your goal):</h4>
            <div className="macro-targets">
              <div className="macro-target">
                <span className="macro-name">Protein (25%):</span>
                <span className="macro-value">{Math.round(goals.daily_calories * 0.25 / 4)}g</span>
              </div>
              <div className="macro-target">
                <span className="macro-name">Carbs (45%):</span>
                <span className="macro-value">{Math.round(goals.daily_calories * 0.45 / 4)}g</span>
              </div>
              <div className="macro-target">
                <span className="macro-name">Fat (30%):</span>
                <span className="macro-value">{Math.round(goals.daily_calories * 0.30 / 9)}g</span>
              </div>
            </div>
          </div>
        </div>

        {/* Health Metrics */}
        <div className="goals-card">
          <h3>Health Metrics</h3>
          
          {bmi > 0 && (
            <div className="bmi-section">
              <div className="bmi-display">
                <span className="bmi-label">BMI:</span>
                <span className="bmi-value" style={{ color: bmiInfo.color }}>
                  {bmi}
                </span>
                <span className="bmi-category" style={{ color: bmiInfo.color }}>
                  ({bmiInfo.category})
                </span>
              </div>
              
              <div className="bmi-scale">
                <div className="bmi-bar">
                  <div className="bmi-ranges">
                    <span className="range underweight">Under</span>
                    <span className="range normal">Normal</span>
                    <span className="range overweight">Over</span>
                    <span className="range obese">Obese</span>
                  </div>
                  <div 
                    className="bmi-indicator"
                    style={{ 
                      left: `${Math.min((bmi / 40) * 100, 95)}%`,
                      backgroundColor: bmiInfo.color
                    }}
                  ></div>
                </div>
              </div>
            </div>
          )}
          
          {recommendedCalories > 0 && (
            <div className="health-stats">
              <div className="health-stat">
                <span className="stat-label">BMR:</span>
                <span className="stat-value">{Math.round(calculateBMR() / 1.55)} cal/day</span>
              </div>
              <div className="health-stat">
                <span className="stat-label">TDEE:</span>
                <span className="stat-value">{recommendedCalories} cal/day</span>
              </div>
            </div>
          )}
        </div>

        {/* Goal Recommendations */}
        <div className="goals-card">
          <h3>Personalized Recommendations</h3>
          <div className="recommendations">
            <div className="recommendation-item">
              <span className="rec-icon">💧</span>
              <div className="rec-text">
                <strong>Water Intake:</strong>
                <p>Aim for {goals.weight ? Math.round(goals.weight * 35) : 2500}ml per day</p>
              </div>
            </div>
            
            <div className="recommendation-item">
              <span className="rec-icon">🥬</span>
              <div className="rec-text">
                <strong>Fiber Goal:</strong>
                <p>Target 25-35g of fiber daily</p>
              </div>
            </div>
            
            <div className="recommendation-item">
              <span className="rec-icon">🍽️</span>
              <div className="rec-text">
                <strong>Meal Timing:</strong>
                <p>Eat every 3-4 hours to maintain energy</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="goals-actions">
        <button 
          className="save-goals-btn"
          onClick={saveGoals}
          disabled={saving}
        >
          {saving ? 'Saving...' : '💾 Save Goals'}
        </button>
      </div>
    </div>
  );
};

export default Goals;