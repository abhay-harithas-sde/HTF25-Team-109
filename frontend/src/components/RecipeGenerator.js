import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../App';

const RecipeGenerator = () => {
  const [ingredients, setIngredients] = useState([]);
  const [newIngredient, setNewIngredient] = useState('');
  const [dietaryRestrictions, setDietaryRestrictions] = useState([]);
  const [cuisineType, setCuisineType] = useState('any');
  const [mealType, setMealType] = useState('any');
  const [cookingTime, setCookingTime] = useState('any');
  const [difficulty, setDifficulty] = useState('any');
  const [generatedRecipes, setGeneratedRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const { user } = useAppContext();

  const cuisineTypes = [
    'any', 'italian', 'mexican', 'asian', 'indian', 'mediterranean', 
    'american', 'french', 'thai', 'japanese', 'chinese'
  ];

  const mealTypes = ['any', 'breakfast', 'lunch', 'dinner', 'snack', 'dessert'];
  const cookingTimes = ['any', '15 min', '30 min', '45 min', '1 hour', '1+ hours'];
  const difficulties = ['any', 'easy', 'medium', 'hard'];

  const commonDietaryRestrictions = [
    'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 
    'paleo', 'low-carb', 'low-fat', 'nut-free'
  ];

  const addIngredient = () => {
    if (newIngredient.trim() && !ingredients.includes(newIngredient.trim().toLowerCase())) {
      setIngredients([...ingredients, newIngredient.trim().toLowerCase()]);
      setNewIngredient('');
    }
  };

  const removeIngredient = (ingredient) => {
    setIngredients(ingredients.filter(i => i !== ingredient));
  };

  const toggleDietaryRestriction = (restriction) => {
    setDietaryRestrictions(prev => 
      prev.includes(restriction) 
        ? prev.filter(r => r !== restriction)
        : [...prev, restriction]
    );
  };

  const generateRecipes = async () => {
    if (ingredients.length === 0) {
      alert('Please add at least one ingredient');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/generate-recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          ingredients,
          dietary_restrictions: dietaryRestrictions,
          cuisine_type: cuisineType,
          meal_type: mealType,
          cooking_time: cookingTime,
          difficulty
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedRecipes(data.recipes || []);
      } else {
        // Fallback to mock recipes if API fails
        setGeneratedRecipes(generateMockRecipes());
      }
    } catch (error) {
      console.error('Failed to generate recipes:', error);
      setGeneratedRecipes(generateMockRecipes());
    } finally {
      setLoading(false);
    }
  };

  const generateMockRecipes = () => {
    const mockRecipes = [
      {
        id: 1,
        name: "Quick Veggie Stir-fry",
        description: "A healthy and colorful stir-fry using your available ingredients",
        prep_time: "15 minutes",
        cook_time: "10 minutes",
        difficulty: "easy",
        servings: 2,
        calories_per_serving: 280,
        ingredients: ingredients.slice(0, 5).map(ing => ({ name: ing, amount: "1 cup" })),
        instructions: [
          "Heat oil in a large pan or wok over high heat",
          "Add harder vegetables first and stir-fry for 3-4 minutes",
          "Add softer vegetables and continue cooking for 2-3 minutes",
          "Season with soy sauce, garlic, and ginger",
          "Serve hot over rice or noodles"
        ],
        nutrition: {
          protein: 12,
          carbs: 35,
          fat: 8,
          fiber: 6
        },
        tags: ["quick", "healthy", "vegetarian"]
      },
      {
        id: 2,
        name: "Hearty Ingredient Bowl",
        description: "A nutritious bowl combining your ingredients with grains and protein",
        prep_time: "20 minutes",
        cook_time: "25 minutes",
        difficulty: "medium",
        servings: 3,
        calories_per_serving: 420,
        ingredients: ingredients.slice(0, 6).map(ing => ({ name: ing, amount: "1/2 cup" })),
        instructions: [
          "Cook grains according to package instructions",
          "Prepare protein source (tofu, chicken, or beans)",
          "Sauté vegetables until tender",
          "Combine all ingredients in bowls",
          "Top with your favorite sauce or dressing"
        ],
        nutrition: {
          protein: 18,
          carbs: 45,
          fat: 12,
          fiber: 8
        },
        tags: ["filling", "balanced", "meal-prep"]
      }
    ];

    return mockRecipes.filter(recipe => {
      if (mealType !== 'any' && !recipe.tags.includes(mealType)) return false;
      if (difficulty !== 'any' && recipe.difficulty !== difficulty) return false;
      return true;
    });
  };

  const saveRecipe = async (recipe) => {
    try {
      const response = await fetch('/api/save-recipe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          recipe
        })
      });

      if (response.ok) {
        alert('Recipe saved to your collection!');
      }
    } catch (error) {
      console.error('Failed to save recipe:', error);
    }
  };

  const cookRecipe = (recipe) => {
    // Convert recipe to meal format and save
    const mealData = {
      items: [{
        food_name: recipe.name,
        calories: recipe.calories_per_serving,
        protein: recipe.nutrition.protein,
        carbs: recipe.nutrition.carbs,
        fat: recipe.nutrition.fat,
        portion: 1
      }]
    };
    
    // This would call the parent's saveMeal function
    console.log('Cooking recipe:', recipe.name);
  };

  return (
    <div className="recipe-generator">
      <div className="generator-header">
        <h2>👨‍🍳 AI Recipe Generator</h2>
        <p>Create personalized recipes based on your available ingredients</p>
      </div>

      <div className="generator-form">
        {/* Ingredients Section */}
        <div className="form-section">
          <h3>🥕 Available Ingredients</h3>
          <div className="ingredient-input">
            <input
              type="text"
              placeholder="Add an ingredient..."
              value={newIngredient}
              onChange={(e) => setNewIngredient(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addIngredient()}
            />
            <button onClick={addIngredient} className="add-btn">
              ➕ Add
            </button>
          </div>
          
          <div className="ingredients-list">
            {ingredients.map((ingredient, index) => (
              <motion.span
                key={index}
                className="ingredient-tag"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
              >
                {ingredient}
                <button onClick={() => removeIngredient(ingredient)}>✕</button>
              </motion.span>
            ))}
          </div>
        </div>

        {/* Preferences Section */}
        <div className="form-section">
          <h3>🎯 Recipe Preferences</h3>
          <div className="preferences-grid">
            <div className="preference-group">
              <label>Cuisine Type:</label>
              <select value={cuisineType} onChange={(e) => setCuisineType(e.target.value)}>
                {cuisineTypes.map(type => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="preference-group">
              <label>Meal Type:</label>
              <select value={mealType} onChange={(e) => setMealType(e.target.value)}>
                {mealTypes.map(type => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="preference-group">
              <label>Cooking Time:</label>
              <select value={cookingTime} onChange={(e) => setCookingTime(e.target.value)}>
                {cookingTimes.map(time => (
                  <option key={time} value={time}>
                    {time.charAt(0).toUpperCase() + time.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="preference-group">
              <label>Difficulty:</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                {difficulties.map(diff => (
                  <option key={diff} value={diff}>
                    {diff.charAt(0).toUpperCase() + diff.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Dietary Restrictions */}
        <div className="form-section">
          <h3>🚫 Dietary Restrictions</h3>
          <div className="restrictions-grid">
            {commonDietaryRestrictions.map(restriction => (
              <button
                key={restriction}
                className={`restriction-btn ${dietaryRestrictions.includes(restriction) ? 'active' : ''}`}
                onClick={() => toggleDietaryRestriction(restriction)}
              >
                {restriction}
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <div className="generate-section">
          <motion.button
            className="generate-btn"
            onClick={generateRecipes}
            disabled={loading || ingredients.length === 0}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <>
                <div className="loading-spinner small"></div>
                Generating Recipes...
              </>
            ) : (
              <>
                ✨ Generate Recipes
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Generated Recipes */}
      <AnimatePresence>
        {generatedRecipes.length > 0 && (
          <motion.div
            className="generated-recipes"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <h3>🍽️ Generated Recipes ({generatedRecipes.length})</h3>
            <div className="recipes-grid">
              {generatedRecipes.map((recipe, index) => (
                <motion.div
                  key={recipe.id}
                  className="recipe-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="recipe-header">
                    <h4>{recipe.name}</h4>
                    <div className="recipe-meta">
                      <span className="servings">👥 {recipe.servings}</span>
                      <span className="calories">🔥 {recipe.calories_per_serving} cal</span>
                      <span className={`difficulty ${recipe.difficulty}`}>
                        {recipe.difficulty}
                      </span>
                    </div>
                  </div>

                  <p className="recipe-description">{recipe.description}</p>

                  <div className="recipe-times">
                    <span>⏱️ Prep: {recipe.prep_time}</span>
                    <span>🍳 Cook: {recipe.cook_time}</span>
                  </div>

                  <div className="recipe-nutrition">
                    <div className="nutrition-item">
                      <span>Protein: {recipe.nutrition.protein}g</span>
                    </div>
                    <div className="nutrition-item">
                      <span>Carbs: {recipe.nutrition.carbs}g</span>
                    </div>
                    <div className="nutrition-item">
                      <span>Fat: {recipe.nutrition.fat}g</span>
                    </div>
                  </div>

                  <div className="recipe-tags">
                    {recipe.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>

                  <div className="recipe-actions">
                    <button
                      className="view-recipe-btn"
                      onClick={() => setSelectedRecipe(recipe)}
                    >
                      👁️ View Recipe
                    </button>
                    <button
                      className="save-recipe-btn"
                      onClick={() => saveRecipe(recipe)}
                    >
                      💾 Save
                    </button>
                    <button
                      className="cook-recipe-btn"
                      onClick={() => cookRecipe(recipe)}
                    >
                      🍳 Cook Now
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recipe Detail Modal */}
      <AnimatePresence>
        {selectedRecipe && (
          <motion.div
            className="recipe-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedRecipe(null)}
          >
            <motion.div
              className="recipe-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h2>{selectedRecipe.name}</h2>
                <button 
                  className="close-modal"
                  onClick={() => setSelectedRecipe(null)}
                >
                  ✕
                </button>
              </div>

              <div className="modal-content">
                <div className="recipe-overview">
                  <p>{selectedRecipe.description}</p>
                  <div className="recipe-stats">
                    <span>👥 Serves {selectedRecipe.servings}</span>
                    <span>⏱️ {selectedRecipe.prep_time} prep</span>
                    <span>🍳 {selectedRecipe.cook_time} cook</span>
                    <span>🔥 {selectedRecipe.calories_per_serving} cal/serving</span>
                  </div>
                </div>

                <div className="recipe-details">
                  <div className="ingredients-section">
                    <h3>📝 Ingredients</h3>
                    <ul>
                      {selectedRecipe.ingredients.map((ingredient, index) => (
                        <li key={index}>
                          <span className="amount">{ingredient.amount}</span>
                          <span className="name">{ingredient.name}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="instructions-section">
                    <h3>👨‍🍳 Instructions</h3>
                    <ol>
                      {selectedRecipe.instructions.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ol>
                  </div>
                </div>

                <div className="nutrition-breakdown">
                  <h3>📊 Nutrition per serving</h3>
                  <div className="nutrition-grid">
                    <div className="nutrition-item">
                      <span className="label">Calories</span>
                      <span className="value">{selectedRecipe.calories_per_serving}</span>
                    </div>
                    <div className="nutrition-item">
                      <span className="label">Protein</span>
                      <span className="value">{selectedRecipe.nutrition.protein}g</span>
                    </div>
                    <div className="nutrition-item">
                      <span className="label">Carbs</span>
                      <span className="value">{selectedRecipe.nutrition.carbs}g</span>
                    </div>
                    <div className="nutrition-item">
                      <span className="label">Fat</span>
                      <span className="value">{selectedRecipe.nutrition.fat}g</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button 
                  className="action-btn primary"
                  onClick={() => cookRecipe(selectedRecipe)}
                >
                  🍳 Cook This Recipe
                </button>
                <button 
                  className="action-btn secondary"
                  onClick={() => saveRecipe(selectedRecipe)}
                >
                  💾 Save Recipe
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RecipeGenerator;