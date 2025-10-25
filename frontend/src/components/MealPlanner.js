import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../App';

const MealPlanner = ({ suggestions, onPlanMeal }) => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [mealPlan, setMealPlan] = useState({});
  const [viewMode, setViewMode] = useState('suggestions'); // 'suggestions', 'calendar', 'shopping'
  const [selectedMealType, setSelectedMealType] = useState('breakfast');
  const [customMeal, setCustomMeal] = useState({ name: '', ingredients: '', calories: '' });
  const [shoppingList, setShoppingList] = useState([]);
  const { user } = useAppContext();

  useEffect(() => {
    loadMealPlan();
    generateShoppingList();
  }, [selectedDate]);

  const loadMealPlan = async () => {
    try {
      const response = await fetch(`/api/meal-plan?date=${selectedDate}&user_id=${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setMealPlan(data.plan || {});
      }
    } catch (error) {
      console.error('Failed to load meal plan:', error);
    }
  };

  const saveMealToPlan = async (meal, mealType, date) => {
    try {
      const response = await fetch('/api/meal-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          date: date,
          meal_type: mealType,
          meal: meal
        })
      });

      if (response.ok) {
        setMealPlan(prev => ({
          ...prev,
          [date]: {
            ...prev[date],
            [mealType]: meal
          }
        }));
        generateShoppingList();
      }
    } catch (error) {
      console.error('Failed to save meal plan:', error);
    }
  };

  const generateShoppingList = () => {
    const ingredients = new Set();
    
    // Extract ingredients from current week's meal plan
    const today = new Date();
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];
      
      const dayPlan = mealPlan[dateStr];
      if (dayPlan) {
        Object.values(dayPlan).forEach(meal => {
          if (meal && meal.ingredients) {
            meal.ingredients.forEach(ingredient => ingredients.add(ingredient));
          }
        });
      }
    }
    
    setShoppingList(Array.from(ingredients));
  };

  const addCustomMeal = () => {
    if (customMeal.name && customMeal.ingredients && customMeal.calories) {
      const meal = {
        name: customMeal.name,
        description: `Custom meal: ${customMeal.name}`,
        calories: parseInt(customMeal.calories),
        ingredients: customMeal.ingredients.split(',').map(i => i.trim()),
        prep_time: "Custom",
        difficulty: "custom",
        tags: ["custom"]
      };
      
      saveMealToPlan(meal, selectedMealType, selectedDate);
      setCustomMeal({ name: '', ingredients: '', calories: '' });
    }
  };

  const getWeekDates = () => {
    const today = new Date();
    const week = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      week.push(date);
    }
    return week;
  };

  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];

  return (
    <div className="meal-planner">
      <div className="planner-header">
        <h2>🍽️ AI Meal Planner</h2>
        <div className="view-toggle">
          {['suggestions', 'calendar', 'shopping'].map(mode => (
            <button
              key={mode}
              className={`toggle-btn ${viewMode === mode ? 'active' : ''}`}
              onClick={() => setViewMode(mode)}
            >
              {mode === 'suggestions' && '💡 Suggestions'}
              {mode === 'calendar' && '📅 Calendar'}
              {mode === 'shopping' && '🛒 Shopping'}
            </button>
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        {/* Suggestions View */}
        {viewMode === 'suggestions' && (
          <motion.div
            key="suggestions"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="suggestions-view"
          >
            <div className="meal-type-selector">
              {mealTypes.map(type => (
                <button
                  key={type}
                  className={`meal-type-btn ${selectedMealType === type ? 'active' : ''}`}
                  onClick={() => setSelectedMealType(type)}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>

            <div className="suggestions-grid">
              {suggestions.map((suggestion, index) => (
                <motion.div
                  key={index}
                  className="suggestion-card"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="suggestion-header">
                    <h3>{suggestion.name}</h3>
                    <div className="suggestion-meta">
                      <span className="calories">{suggestion.calories} cal</span>
                      <span className="time">{suggestion.prep_time}</span>
                      <span className={`difficulty ${suggestion.difficulty}`}>
                        {suggestion.difficulty}
                      </span>
                    </div>
                  </div>
                  
                  <p className="suggestion-description">{suggestion.description}</p>
                  
                  <div className="suggestion-tags">
                    {suggestion.tags?.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                  
                  <div className="suggestion-ingredients">
                    <strong>Ingredients:</strong>
                    <ul>
                      {suggestion.ingredients?.slice(0, 4).map(ingredient => (
                        <li key={ingredient}>{ingredient}</li>
                      ))}
                      {suggestion.ingredients?.length > 4 && (
                        <li>+{suggestion.ingredients.length - 4} more...</li>
                      )}
                    </ul>
                  </div>
                  
                  <div className="suggestion-actions">
                    <button
                      className="plan-btn"
                      onClick={() => saveMealToPlan(suggestion, selectedMealType, selectedDate)}
                    >
                      📅 Plan for {selectedMealType}
                    </button>
                    <button
                      className="cook-btn"
                      onClick={() => onPlanMeal({ 
                        items: [{ 
                          food_name: suggestion.name, 
                          calories: suggestion.calories,
                          protein: suggestion.calories * 0.15 / 4, // Estimate
                          carbs: suggestion.calories * 0.5 / 4,
                          fat: suggestion.calories * 0.35 / 9,
                          portion: 1
                        }] 
                      })}
                    >
                      🍳 Cook Now
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Custom Meal Creator */}
            <div className="custom-meal-creator">
              <h3>Create Custom Meal</h3>
              <div className="custom-meal-form">
                <input
                  type="text"
                  placeholder="Meal name"
                  value={customMeal.name}
                  onChange={(e) => setCustomMeal(prev => ({ ...prev, name: e.target.value }))}
                />
                <input
                  type="text"
                  placeholder="Ingredients (comma separated)"
                  value={customMeal.ingredients}
                  onChange={(e) => setCustomMeal(prev => ({ ...prev, ingredients: e.target.value }))}
                />
                <input
                  type="number"
                  placeholder="Estimated calories"
                  value={customMeal.calories}
                  onChange={(e) => setCustomMeal(prev => ({ ...prev, calories: e.target.value }))}
                />
                <button onClick={addCustomMeal} className="add-custom-btn">
                  ➕ Add Custom Meal
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Calendar View */}
        {viewMode === 'calendar' && (
          <motion.div
            key="calendar"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="calendar-view"
          >
            <div className="date-selector">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
              />
            </div>

            <div className="weekly-calendar">
              {getWeekDates().map(date => {
                const dateStr = date.toISOString().split('T')[0];
                const dayPlan = mealPlan[dateStr] || {};
                const isToday = dateStr === new Date().toISOString().split('T')[0];
                
                return (
                  <div key={dateStr} className={`day-column ${isToday ? 'today' : ''}`}>
                    <div className="day-header">
                      <h4>{date.toLocaleDateString('en-US', { weekday: 'short' })}</h4>
                      <span>{date.getDate()}</span>
                    </div>
                    
                    {mealTypes.map(mealType => (
                      <div key={mealType} className="meal-slot">
                        <div className="meal-type-label">{mealType}</div>
                        {dayPlan[mealType] ? (
                          <div className="planned-meal">
                            <div className="meal-name">{dayPlan[mealType].name}</div>
                            <div className="meal-calories">{dayPlan[mealType].calories} cal</div>
                          </div>
                        ) : (
                          <div className="empty-meal">
                            <button 
                              className="add-meal-btn"
                              onClick={() => {
                                setSelectedDate(dateStr);
                                setSelectedMealType(mealType);
                                setViewMode('suggestions');
                              }}
                            >
                              + Add
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Shopping List View */}
        {viewMode === 'shopping' && (
          <motion.div
            key="shopping"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="shopping-view"
          >
            <div className="shopping-header">
              <h3>🛒 Weekly Shopping List</h3>
              <p>Based on your meal plan for this week</p>
            </div>

            <div className="shopping-list">
              {shoppingList.length > 0 ? (
                <div className="ingredients-grid">
                  {shoppingList.map((ingredient, index) => (
                    <motion.div
                      key={index}
                      className="ingredient-item"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <input type="checkbox" id={`ingredient-${index}`} />
                      <label htmlFor={`ingredient-${index}`}>{ingredient}</label>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="empty-shopping-list">
                  <p>No ingredients needed yet. Start planning your meals!</p>
                  <button 
                    className="start-planning-btn"
                    onClick={() => setViewMode('suggestions')}
                  >
                    Start Planning Meals
                  </button>
                </div>
              )}
            </div>

            {shoppingList.length > 0 && (
              <div className="shopping-actions">
                <button className="export-list-btn">
                  📤 Export List
                </button>
                <button className="clear-list-btn">
                  🗑️ Clear Completed
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MealPlanner;