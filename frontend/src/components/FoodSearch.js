import React, { useState, useEffect } from 'react';

const FoodSearch = ({ onAddFood }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFood, setSelectedFood] = useState(null);
  const [portion, setPortion] = useState(1);

  useEffect(() => {
    if (searchQuery.length > 2) {
      searchFood();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const searchFood = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/search-food?q=${encodeURIComponent(searchQuery)}`);
      const result = await response.json();
      if (result.success) {
        setSearchResults(result.results);
      }
    } catch (error) {
      console.error('Error searching food:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectFood = (food) => {
    setSelectedFood(food);
    setPortion(1);
  };

  const addFoodToMeal = () => {
    if (selectedFood) {
      const foodWithPortion = {
        ...selectedFood,
        portion: portion,
        calories: selectedFood.nutrition.calories_per_100g * portion,
        protein: selectedFood.nutrition.protein * portion,
        carbs: selectedFood.nutrition.carbs * portion,
        fat: selectedFood.nutrition.fat * portion,
        fiber: selectedFood.nutrition.fiber * portion
      };
      
      onAddFood(foodWithPortion);
      setSelectedFood(null);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  return (
    <div className="food-search">
      <h3>🔍 Add Food Manually</h3>
      
      <div className="search-input">
        <input
          type="text"
          placeholder="Search for food (e.g., apple, chicken, rice)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-field"
        />
        {loading && <div className="search-loading">Searching...</div>}
      </div>

      {searchResults.length > 0 && (
        <div className="search-results">
          <h4>Search Results:</h4>
          {searchResults.map((food, index) => (
            <div 
              key={index} 
              className="search-result-item"
              onClick={() => selectFood(food)}
            >
              <div className="food-info">
                <span className="food-name">{food.food_name}</span>
                <span className="food-calories">
                  {food.nutrition.calories_per_100g} cal/100g
                </span>
              </div>
              <div className="food-macros">
                <span>P: {food.nutrition.protein}g</span>
                <span>C: {food.nutrition.carbs}g</span>
                <span>F: {food.nutrition.fat}g</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedFood && (
        <div className="food-details-modal">
          <div className="modal-content">
            <h4>Add {selectedFood.food_name}</h4>
            
            <div className="portion-selector">
              <label>Portion Size:</label>
              <div className="portion-controls">
                <button 
                  onClick={() => setPortion(Math.max(0.1, portion - 0.1))}
                  className="portion-btn"
                >
                  -
                </button>
                <input
                  type="number"
                  value={portion}
                  onChange={(e) => setPortion(parseFloat(e.target.value) || 0)}
                  step="0.1"
                  min="0.1"
                  className="portion-input"
                />
                <button 
                  onClick={() => setPortion(portion + 0.1)}
                  className="portion-btn"
                >
                  +
                </button>
              </div>
              <span className="portion-note">
                {portion} × 100g = {Math.round(portion * 100)}g
              </span>
            </div>

            <div className="nutrition-preview">
              <h5>Nutrition (for {Math.round(portion * 100)}g):</h5>
              <div className="nutrition-grid">
                <div className="nutrition-item">
                  <span className="label">Calories:</span>
                  <span className="value">
                    {Math.round(selectedFood.nutrition.calories_per_100g * portion)}
                  </span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Protein:</span>
                  <span className="value">
                    {Math.round(selectedFood.nutrition.protein * portion * 10) / 10}g
                  </span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Carbs:</span>
                  <span className="value">
                    {Math.round(selectedFood.nutrition.carbs * portion * 10) / 10}g
                  </span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Fat:</span>
                  <span className="value">
                    {Math.round(selectedFood.nutrition.fat * portion * 10) / 10}g
                  </span>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button onClick={addFoodToMeal} className="add-food-btn">
                ✅ Add to Meal
              </button>
              <button 
                onClick={() => setSelectedFood(null)} 
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FoodSearch;