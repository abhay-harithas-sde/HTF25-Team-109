#!/usr/bin/env python3
"""
FoodVision AI Database Creation Script
Creates comprehensive database with all tables and sample data
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

def create_database():
    """Create the complete FoodVision AI database"""
    print("🗄️ Creating FoodVision AI Database...")
    
    # Remove existing database if it exists
    if os.path.exists('foodvision.db'):
        os.remove('foodvision.db')
        print("🗑️ Removed existing database")
    
    conn = sqlite3.connect('foodvision.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    print("📋 Creating database schema...")
    
    # Users table with enhanced profile
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            daily_calorie_goal INTEGER DEFAULT 2000,
            height REAL,
            weight REAL,
            age INTEGER,
            gender TEXT DEFAULT 'other',
            activity_level TEXT DEFAULT 'moderate',
            dietary_restrictions TEXT DEFAULT '[]',
            health_conditions TEXT DEFAULT '[]',
            fitness_goals TEXT DEFAULT '[]',
            timezone TEXT DEFAULT 'UTC',
            preferred_units TEXT DEFAULT 'metric',
            privacy_settings TEXT DEFAULT '{}',
            notification_settings TEXT DEFAULT '{}',
            subscription_tier TEXT DEFAULT 'free',
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Enhanced meals table
    cursor.execute('''
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meal_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            image_hash TEXT,
            total_calories REAL NOT NULL,
            total_protein REAL DEFAULT 0,
            total_carbs REAL DEFAULT 0,
            total_fat REAL DEFAULT 0,
            total_fiber REAL DEFAULT 0,
            total_sugar REAL DEFAULT 0,
            total_sodium REAL DEFAULT 0,
            ai_confidence REAL DEFAULT 0,
            processing_time REAL DEFAULT 0,
            location TEXT,
            mood_rating INTEGER DEFAULT 5,
            notes TEXT,
            is_public BOOLEAN DEFAULT 0,
            likes_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Enhanced food items table
    cursor.execute('''
        CREATE TABLE food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            original_prediction TEXT,
            confidence REAL NOT NULL,
            portion_size REAL NOT NULL,
            calories REAL NOT NULL,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fat REAL DEFAULT 0,
            fiber REAL DEFAULT 0,
            sugar REAL DEFAULT 0,
            sodium REAL DEFAULT 0,
            vitamins TEXT DEFAULT '{}',
            minerals TEXT DEFAULT '{}',
            ai_model_used TEXT DEFAULT 'mobilenet',
            processing_method TEXT DEFAULT 'standard',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE
        )
    ''')
    
    # AI predictions cache table
    cursor.execute('''
        CREATE TABLE ai_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_hash TEXT UNIQUE NOT NULL,
            predictions TEXT NOT NULL,
            model_version TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence_score REAL DEFAULT 0,
            expires_at TIMESTAMP
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, preference_key)
        )
    ''')
    
    # Nutrition insights table
    cursor.execute('''
        CREATE TABLE nutrition_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            insight_type TEXT NOT NULL,
            insight_data TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            relevance_score REAL DEFAULT 0,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Meal plans table
    cursor.execute('''
        CREATE TABLE meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            meal_type TEXT NOT NULL,
            recipe_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, date, meal_type)
        )
    ''')
    
    # Recipes table
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            prep_time INTEGER,
            cook_time INTEGER,
            servings INTEGER,
            calories_per_serving REAL,
            nutrition_data TEXT,
            difficulty TEXT,
            cuisine_type TEXT,
            tags TEXT DEFAULT '[]',
            is_public BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')
    
    # Water intake table
    cursor.execute('''
        CREATE TABLE water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            glasses INTEGER DEFAULT 0,
            ml_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, date)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_type TEXT NOT NULL,
            achievement_data TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Social posts table
    cursor.execute('''
        CREATE TABLE social_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image_path TEXT,
            meal_id INTEGER,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            is_public BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE SET NULL
        )
    ''')
    
    # Social connections table
    cursor.execute('''
        CREATE TABLE social_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (friend_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, friend_id)
        )
    ''')
    
    # Challenges table
    cursor.execute('''
        CREATE TABLE challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            challenge_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            target_value REAL,
            reward_points INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Challenge participants table
    cursor.execute('''
        CREATE TABLE challenge_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            current_progress REAL DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(challenge_id, user_id)
        )
    ''')
    
    print("📊 Creating database indexes...")
    
    # Create indexes for better performance
    indexes = [
        'CREATE INDEX idx_meals_user_date ON meals(user_id, timestamp)',
        'CREATE INDEX idx_food_items_meal ON food_items(meal_id)',
        'CREATE INDEX idx_ai_cache_hash ON ai_cache(image_hash)',
        'CREATE INDEX idx_user_preferences ON user_preferences(user_id, preference_key)',
        'CREATE INDEX idx_meal_plans_user_date ON meal_plans(user_id, date)',
        'CREATE INDEX idx_water_intake_user_date ON water_intake(user_id, date)',
        'CREATE INDEX idx_social_posts_user ON social_posts(user_id, created_at)',
        'CREATE INDEX idx_achievements_user ON achievements(user_id)',
        'CREATE INDEX idx_social_connections ON social_connections(user_id, friend_id)',
        'CREATE INDEX idx_challenge_participants ON challenge_participants(challenge_id, user_id)'
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    print("👥 Creating sample users...")
    
    # Create sample users
    users_data = [
        ('admin', 'admin@foodvision.ai', None, 2200, 175, 75, 28, 'male', 'active', 
         '[]', '[]', '["weight_loss", "muscle_gain"]', 'UTC', 'metric'),
        ('demo_user', 'demo@foodvision.ai', None, 2000, 165, 65, 25, 'female', 'moderate',
         '["vegetarian"]', '[]', '["healthy_eating"]', 'UTC', 'metric'),
        ('john_doe', 'john@example.com', None, 2400, 180, 80, 32, 'male', 'very_active',
         '[]', '[]', '["muscle_gain", "performance"]', 'UTC', 'metric'),
        ('jane_smith', 'jane@example.com', None, 1800, 160, 55, 29, 'female', 'moderate',
         '["gluten_free"]', '["diabetes"]', '["weight_maintenance"]', 'UTC', 'metric'),
        ('alex_rivera', 'alex@example.com', None, 2100, 170, 70, 26, 'other', 'active',
         '["vegan"]', '[]', '["environmental", "health"]', 'UTC', 'metric')
    ]
    
    for user_data in users_data:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, daily_calorie_goal, height, weight, 
                             age, gender, activity_level, dietary_restrictions, health_conditions, 
                             fitness_goals, timezone, preferred_units)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', user_data)
    
    print("🍽️ Creating sample meals...")
    
    # Create sample meals for the past week
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for user_id in range(1, 6):  # For each user
        for days_ago in range(7):  # Past 7 days
            meal_date = datetime.now() - timedelta(days=days_ago)
            
            # Create 2-4 meals per day
            num_meals = random.randint(2, 4)
            for meal_idx in range(num_meals):
                meal_type = meal_types[meal_idx % len(meal_types)]
                
                # Generate realistic meal data
                base_calories = {
                    'breakfast': random.randint(300, 500),
                    'lunch': random.randint(400, 700),
                    'dinner': random.randint(500, 800),
                    'snack': random.randint(100, 300)
                }[meal_type]
                
                total_calories = base_calories + random.randint(-50, 50)
                total_protein = total_calories * random.uniform(0.15, 0.25) / 4
                total_carbs = total_calories * random.uniform(0.45, 0.65) / 4
                total_fat = total_calories * random.uniform(0.20, 0.35) / 9
                total_fiber = random.uniform(3, 12)
                total_sugar = random.uniform(5, 25)
                total_sodium = random.uniform(200, 800)
                
                meal_timestamp = meal_date.replace(
                    hour=random.randint(6, 22),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
                
                cursor.execute('''
                    INSERT INTO meals (user_id, meal_type, timestamp, total_calories, 
                                     total_protein, total_carbs, total_fat, total_fiber,
                                     total_sugar, total_sodium, ai_confidence, processing_time,
                                     mood_rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, meal_type, meal_timestamp, total_calories, total_protein,
                      total_carbs, total_fat, total_fiber, total_sugar, total_sodium,
                      random.uniform(0.7, 0.95), random.uniform(0.5, 2.0), random.randint(3, 5)))
    
    print("🥗 Creating sample food items...")
    
    # Sample foods with nutrition data
    sample_foods = [
        ('chicken_breast', 0.9, 1.0, 165, 31, 0, 3.6, 0, 0, 74),
        ('brown_rice', 0.85, 0.5, 111, 2.6, 23, 0.9, 1.8, 0, 5),
        ('broccoli', 0.8, 1.2, 34, 2.8, 7, 0.4, 2.6, 1.5, 33),
        ('salmon', 0.92, 1.0, 208, 22, 0, 12, 0, 0, 59),
        ('quinoa', 0.88, 0.7, 120, 4.4, 22, 1.9, 2.8, 0, 7),
        ('spinach', 0.75, 1.5, 23, 2.9, 3.6, 0.4, 2.2, 0.4, 79),
        ('sweet_potato', 0.82, 1.0, 86, 1.6, 20, 0.1, 3.0, 4.2, 6),
        ('avocado', 0.87, 0.5, 160, 2, 9, 15, 7, 0.7, 7),
        ('greek_yogurt', 0.9, 1.0, 59, 10, 3.6, 0.4, 0, 3.6, 36),
        ('almonds', 0.85, 0.3, 579, 21, 22, 50, 12, 4.4, 1),
        ('banana', 0.88, 1.0, 89, 1.1, 23, 0.3, 2.6, 12, 1),
        ('oatmeal', 0.83, 0.8, 68, 2.4, 12, 1.4, 1.7, 0, 49),
        ('eggs', 0.91, 2.0, 155, 13, 1.1, 11, 0, 1.1, 124),
        ('tomato', 0.79, 1.5, 18, 0.9, 3.9, 0.2, 1.2, 2.6, 5),
        ('cucumber', 0.76, 1.0, 16, 0.7, 4, 0.1, 0.5, 1.7, 2)
    ]
    
    # Get all meal IDs
    cursor.execute('SELECT id FROM meals')
    meal_ids = [row[0] for row in cursor.fetchall()]
    
    # Add food items to meals
    for meal_id in meal_ids:
        # Each meal has 1-4 food items
        num_foods = random.randint(1, 4)
        selected_foods = random.sample(sample_foods, min(num_foods, len(sample_foods)))
        
        for food_name, confidence, portion, calories, protein, carbs, fat, fiber, sugar, sodium in selected_foods:
            # Adjust values based on portion
            actual_calories = calories * portion
            actual_protein = protein * portion
            actual_carbs = carbs * portion
            actual_fat = fat * portion
            actual_fiber = fiber * portion
            actual_sugar = sugar * portion
            actual_sodium = sodium * portion
            
            cursor.execute('''
                INSERT INTO food_items (meal_id, food_name, confidence, portion_size,
                                      calories, protein, carbs, fat, fiber, sugar, sodium,
                                      ai_model_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (meal_id, food_name, confidence, portion, actual_calories, actual_protein,
                  actual_carbs, actual_fat, actual_fiber, actual_sugar, actual_sodium,
                  random.choice(['mobilenet', 'resnet50', 'inception_v3'])))
    
    print("💧 Creating water intake data...")
    
    # Create water intake data
    for user_id in range(1, 6):
        for days_ago in range(7):
            date = (datetime.now() - timedelta(days=days_ago)).date()
            glasses = random.randint(4, 12)
            ml_amount = glasses * 250  # 250ml per glass
            
            cursor.execute('''
                INSERT INTO water_intake (user_id, date, glasses, ml_amount)
                VALUES (?, ?, ?, ?)
            ''', (user_id, date, glasses, ml_amount))
    
    print("🏆 Creating achievements...")
    
    # Create sample achievements
    achievements_data = [
        (1, 'first_meal', '{"title": "First Meal Logged", "description": "Logged your first meal"}'),
        (1, 'week_streak', '{"title": "Week Warrior", "description": "Logged meals for 7 consecutive days"}'),
        (2, 'first_meal', '{"title": "First Meal Logged", "description": "Logged your first meal"}'),
        (2, 'calorie_goal', '{"title": "Goal Achiever", "description": "Met daily calorie goal"}'),
        (3, 'first_meal', '{"title": "First Meal Logged", "description": "Logged your first meal"}'),
        (4, 'first_meal', '{"title": "First Meal Logged", "description": "Logged your first meal"}'),
        (5, 'first_meal', '{"title": "First Meal Logged", "description": "Logged your first meal"}')
    ]
    
    for user_id, achievement_type, achievement_data in achievements_data:
        cursor.execute('''
            INSERT INTO achievements (user_id, achievement_type, achievement_data)
            VALUES (?, ?, ?)
        ''', (user_id, achievement_type, achievement_data))
    
    print("🎯 Creating challenges...")
    
    # Create sample challenges
    challenges_data = [
        ('30-Day Veggie Challenge', 'Eat 5 servings of vegetables every day for 30 days', 
         'vegetables', (datetime.now() - timedelta(days=10)).date(), 
         (datetime.now() + timedelta(days=20)).date(), 5, 100),
        ('Hydration Hero', 'Drink 8 glasses of water daily for 2 weeks',
         'water', (datetime.now() - timedelta(days=5)).date(),
         (datetime.now() + timedelta(days=9)).date(), 8, 50),
        ('Protein Power Week', 'Meet your protein goals every day this week',
         'protein', (datetime.now() - timedelta(days=2)).date(),
         (datetime.now() + timedelta(days=5)).date(), 100, 75)
    ]
    
    for name, description, challenge_type, start_date, end_date, target_value, reward_points in challenges_data:
        cursor.execute('''
            INSERT INTO challenges (name, description, challenge_type, start_date, end_date,
                                  target_value, reward_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, challenge_type, start_date, end_date, target_value, reward_points))
    
    # Add some challenge participants
    cursor.execute('SELECT id FROM challenges')
    challenge_ids = [row[0] for row in cursor.fetchall()]
    
    for challenge_id in challenge_ids:
        # Random users join challenges
        participants = random.sample(range(1, 6), random.randint(2, 4))
        for user_id in participants:
            progress = random.uniform(0, 1) * 100  # 0-100% progress
            cursor.execute('''
                INSERT INTO challenge_participants (challenge_id, user_id, current_progress)
                VALUES (?, ?, ?)
            ''', (challenge_id, user_id, progress))
    
    print("📱 Creating social posts...")
    
    # Create sample social posts
    social_posts = [
        (1, "Just reached my daily calorie goal! 🎯 Feeling great about my progress.", None, None, 5, 2),
        (2, "Made this amazing quinoa bowl for lunch! 🥗 So colorful and nutritious.", None, None, 8, 3),
        (3, "Week 3 of my fitness journey! Down 5 pounds and feeling stronger every day 💪", None, None, 12, 5),
        (4, "Meal prep Sunday! These overnight oats are going to make my mornings so much easier 🌅", None, None, 6, 1),
        (5, "Trying out a new vegan recipe today. Plant-based eating has been such a game changer! 🌱", None, None, 9, 4)
    ]
    
    for user_id, content, image_path, meal_id, likes_count, comments_count in social_posts:
        cursor.execute('''
            INSERT INTO social_posts (user_id, content, image_path, meal_id, likes_count, comments_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, content, image_path, meal_id, likes_count, comments_count))
    
    print("🤝 Creating social connections...")
    
    # Create some friendships
    friendships = [
        (1, 2, 'accepted'), (1, 3, 'accepted'), (1, 4, 'pending'),
        (2, 3, 'accepted'), (2, 5, 'accepted'),
        (3, 4, 'accepted'), (3, 5, 'pending'),
        (4, 5, 'accepted')
    ]
    
    for user_id, friend_id, status in friendships:
        cursor.execute('''
            INSERT INTO social_connections (user_id, friend_id, status)
            VALUES (?, ?, ?)
        ''', (user_id, friend_id, status))
    
    print("🧠 Creating nutrition insights...")
    
    # Create sample nutrition insights
    insights_data = [
        (1, 'calorie_trend', '{"trend": "increasing", "change": 5.2, "recommendation": "Consider portion control"}', 0.8),
        (1, 'protein_intake', '{"status": "good", "average": 85, "target": 100, "recommendation": "Add more lean proteins"}', 0.7),
        (2, 'vegetable_intake', '{"status": "excellent", "servings": 6, "target": 5, "recommendation": "Keep up the great work!"}', 0.9),
        (3, 'hydration', '{"status": "needs_improvement", "glasses": 5, "target": 8, "recommendation": "Set water reminders"}', 0.6),
        (4, 'fiber_intake', '{"status": "good", "grams": 22, "target": 25, "recommendation": "Add more whole grains"}', 0.7),
        (5, 'macro_balance', '{"protein": 18, "carbs": 55, "fat": 27, "recommendation": "Well balanced macros!"}', 0.8)
    ]
    
    for user_id, insight_type, insight_data, relevance_score in insights_data:
        cursor.execute('''
            INSERT INTO nutrition_insights (user_id, insight_type, insight_data, relevance_score)
            VALUES (?, ?, ?, ?)
        ''', (user_id, insight_type, insight_data, relevance_score))
    
    print("🍳 Creating sample recipes...")
    
    # Create sample recipes
    recipes_data = [
        (1, 'Quinoa Power Bowl', 'A nutritious bowl packed with protein and vegetables',
         '["quinoa", "chickpeas", "spinach", "cherry tomatoes", "avocado", "tahini"]',
         '["Cook quinoa", "Roast chickpeas", "Assemble bowl", "Drizzle with tahini"]',
         15, 20, 2, 450, '{"protein": 18, "carbs": 52, "fat": 16, "fiber": 12}',
         'medium', 'mediterranean', '["healthy", "vegetarian", "high-protein"]'),
        (2, 'Overnight Oats', 'Easy make-ahead breakfast',
         '["oats", "almond milk", "chia seeds", "berries", "honey"]',
         '["Mix ingredients", "Refrigerate overnight", "Top with berries"]',
         5, 0, 1, 280, '{"protein": 8, "carbs": 45, "fat": 6, "fiber": 8}',
         'easy', 'american', '["breakfast", "make-ahead", "healthy"]'),
        (3, 'Grilled Salmon with Vegetables', 'Heart-healthy dinner option',
         '["salmon fillet", "broccoli", "bell peppers", "olive oil", "lemon"]',
         '["Season salmon", "Grill salmon", "Steam vegetables", "Serve with lemon"]',
         10, 15, 2, 520, '{"protein": 35, "carbs": 12, "fat": 28, "fiber": 5}',
         'medium', 'american', '["dinner", "high-protein", "omega-3"]')
    ]
    
    for recipe_data in recipes_data:
        cursor.execute('''
            INSERT INTO recipes (user_id, name, description, ingredients, instructions,
                               prep_time, cook_time, servings, calories_per_serving,
                               nutrition_data, difficulty, cuisine_type, tags, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', recipe_data)
    
    print("⚙️ Creating user preferences...")
    
    # Create user preferences
    preferences_data = [
        (1, 'theme', 'dark'),
        (1, 'notifications', 'true'),
        (1, 'ai_mode', 'advanced'),
        (2, 'theme', 'light'),
        (2, 'units', 'metric'),
        (3, 'notifications', 'false'),
        (4, 'ai_mode', 'basic'),
        (5, 'theme', 'dark')
    ]
    
    for user_id, preference_key, preference_value in preferences_data:
        cursor.execute('''
            INSERT INTO user_preferences (user_id, preference_key, preference_value)
            VALUES (?, ?, ?)
        ''', (user_id, preference_key, preference_value))
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"📊 Database location: {os.path.abspath('foodvision.db')}")
    
    # Display statistics
    conn = sqlite3.connect('foodvision.db')
    cursor = conn.cursor()
    
    print("\n📈 Database Statistics:")
    tables = [
        'users', 'meals', 'food_items', 'water_intake', 'achievements',
        'challenges', 'challenge_participants', 'social_posts', 'social_connections',
        'nutrition_insights', 'recipes', 'user_preferences'
    ]
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} records")
    
    conn.close()
    
    print("\n🎉 Database setup complete! Ready for FoodVision AI!")

if __name__ == '__main__':
    create_database()