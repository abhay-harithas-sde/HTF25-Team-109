import React, { useState } from 'react';

const FoodResults = ({ results, onSaveMeal, onBack }) => {
  const [selectedItems, setSelectedItems] = useState([]);
  const [portions, setPortions] = useState({});

  const toggleFoodItem = (index) => {
    const newSelected = selectedItems.includes(index)
      ? selectedItems.filter(i => i !== index)
      : [...selectedItems, index];
    setSelectedItems(newSelected);
  };

  const updatePortion = (index, portion) => {
    setPortions({
      ...portions,
      [index]: portion
    });
  };

  const calculateTotalCalories = () => {
    return selectedItems.reduce((total, index) => {
      const item = results[index];
      const portion = portions[index] || 1;
      return total + (item.nutrition.calories_per_100g * portion);
    }, 0);
  };

  const handleSaveMeal = () => {
    const mealData = {
      timestamp: new Date().toISOString(),
      items: selectedItems.map(index => ({
        ...results[index],
        portion: portions[index] || 1
      })),
      total_calories: calculateTotalCalories()
    };
    
    onSaveMeal(mealData);
  };

  return (
    <div className="food-results">
      <div className="results-header">
        <button onClick={onBack} className="back-btn">← Back</button>
        <h2>Food Analysis Results</h2>
      </div>

      <div className="detected-foods">
        {results.map((item, index) => (
          <div 
            key={index} 
            className={`food-item ${selectedItems.includes(index) ? 'selected' : ''}`}
          >
            <div className="food-header">
              <input
                type="checkbox"
                checked={selectedItems.includes(index)}
                onChange={() => toggleFoodItem(index)}
              />
              <h3>{item.food_name}</h3>
              <span className="confidence">
                {(item.confidence * 100).toFixed(1)}% confident
              </span>
            </div>

            {selectedItems.includes(index) && (
              <div className="food-details">
                <div className="portion-selector">
                  <label>Portion size:</label>
                  <select 
                    value={portions[index] || 1}
                    onChange={(e) => updatePortion(index, parseFloat(e.target.value))}
                  >
                    <option value={0.5}>Half portion (50g)</option>
                    <option value={1}>Standard portion (100g)</option>
                    <option value={1.5}>Large portion (150g)</option>
                    <option value={2}>Extra large (200g)</option>
                  </select>
                </div>

                <div className="nutrition-info">
                  <div className="nutrition-grid">
                    <div className="nutrition-item">
                      <span className="label">Calories:</span>
                      <span className="value">
                        {Math.round(item.nutrition.calories_per_100g * (portions[index] || 1))}
                      </span>
                    </div>
                    <div className="nutrition-item">
                      <span className="label">Protein:</span>
                      <span className="value">
                        {Math.round(item.nutrition.protein * (portions[index] || 1))}g
                      </span>
                    </div>
                    <div className="nutrition-item">
                      <span className="label">Carbs:</span>
                      <span className="value">
                        {Math.round(item.nutrition.carbs * (portions[index] || 1))}g
                      </span>
                    </div>
                    <div className="nutrition-item">
                      <span className="label">Fat:</span>
                      <span className="value">
                        {Math.round(item.nutrition.fat * (portions[index] || 1))}g
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedItems.length > 0 && (
        <div className="meal-summary">
          <div className="total-calories">
            <h3>Total Calories: {Math.round(calculateTotalCalories())}</h3>
          </div>
          <button onClick={handleSaveMeal} className="save-meal-btn">
            💾 Save Meal
          </button>
        </div>
      )}
    </div>
  );
};

export default FoodResults;