#!/usr/bin/env python3
"""
Simplified FoodVision AI Backend for Testing Authentication
Focuses on authentication and basic API endpoints without heavy AI dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime, timedelta
import logging

# Import authentication blueprint
from auth import auth_bp

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'foodvision_hackathon_2024_auth_test'

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database connection helper
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('foodvision.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize basic database if it doesn't exist
def init_basic_db():
    """Initialize basic database structure"""
    if not os.path.exists('foodvision.db'):
        logging.info("Creating basic database...")
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Create basic users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
        
        # Create basic meals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                meal_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                total_calories REAL NOT NULL,
                total_protein REAL DEFAULT 0,
                total_carbs REAL DEFAULT 0,
                total_fat REAL DEFAULT 0,
                total_fiber REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create basic food items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_id INTEGER NOT NULL,
                food_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                portion_size REAL NOT NULL,
                calories REAL NOT NULL,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                fiber REAL DEFAULT 0,
                FOREIGN KEY (meal_id) REFERENCES meals (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Basic database created successfully")

# Initialize database
init_basic_db()

# Basic API endpoints for testing
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'FoodVision AI Backend is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/analyze-food', methods=['POST'])
def analyze_food_mock():
    """Mock food analysis endpoint for testing"""
    try:
        data = request.json
        
        # Mock analysis results
        mock_results = {
            'success': True,
            'predictions': [
                {
                    'food_name': 'apple',
                    'confidence': 0.95,
                    'nutrition': {
                        'calories_per_100g': 52,
                        'protein': 0.3,
                        'carbs': 14,
                        'fat': 0.2,
                        'fiber': 2.4
                    },
                    'estimated_portion': 1.0,
                    'nutritional_values': {
                        'calories': 52,
                        'protein': 0.3,
                        'carbs': 14,
                        'fat': 0.2,
                        'fiber': 2.4
                    }
                }
            ],
            'processing_time': 0.5,
            'ai_confidence': 0.95,
            'image_context': 'A fresh red apple on a white background'
        }
        
        return jsonify(mock_results)
        
    except Exception as e:
        logging.error(f"Error in mock food analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-meal', methods=['POST'])
def save_meal():
    """Save meal endpoint"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        meal_type = data.get('meal_type', 'snack')
        food_items = data.get('items', [])
        
        # Calculate totals
        total_calories = sum(item.get('calories', 0) for item in food_items)
        total_protein = sum(item.get('protein', 0) for item in food_items)
        total_carbs = sum(item.get('carbs', 0) for item in food_items)
        total_fat = sum(item.get('fat', 0) for item in food_items)
        total_fiber = sum(item.get('fiber', 0) for item in food_items)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert meal
        cursor.execute('''
            INSERT INTO meals (user_id, meal_type, total_calories, 
                             total_protein, total_carbs, total_fat, total_fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_type, total_calories, total_protein, 
              total_carbs, total_fat, total_fiber))
        
        meal_id = cursor.lastrowid
        
        # Insert food items
        for item in food_items:
            cursor.execute('''
                INSERT INTO food_items (meal_id, food_name, confidence, portion_size,
                                      calories, protein, carbs, fat, fiber)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (meal_id, item.get('food_name', ''), item.get('confidence', 0),
                  item.get('portion', 1), item.get('calories', 0),
                  item.get('protein', 0), item.get('carbs', 0),
                  item.get('fat', 0), item.get('fiber', 0)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Meal saved successfully',
            'meal_id': meal_id
        })
        
    except Exception as e:
        logging.error(f"Error saving meal: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-stats', methods=['GET'])
def get_daily_stats():
    """Get daily nutrition statistics"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COALESCE(SUM(total_calories), 0) as calories,
                COALESCE(SUM(total_protein), 0) as protein,
                COALESCE(SUM(total_carbs), 0) as carbs,
                COALESCE(SUM(total_fat), 0) as fat,
                COALESCE(SUM(total_fiber), 0) as fiber,
                COUNT(*) as meals_count
            FROM meals 
            WHERE user_id = ? AND DATE(timestamp) = ?
        ''', (user_id, date))
        
        result = cursor.fetchone()
        conn.close()
        
        stats = {
            'calories': result[0],
            'protein': result[1],
            'carbs': result[2],
            'fat': result[3],
            'fiber': result[4],
            'meals_count': result[5],
            'water': 8,  # Mock data
            'steps': 8500  # Mock data
        }
        
        return jsonify({
            'success': True,
            'stats': stats,
            'date': date
        })
        
    except Exception as e:
        logging.error(f"Error getting daily stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-history', methods=['GET'])
def get_meal_history():
    """Get meal history"""
    try:
        days = request.args.get('days', 7, type=int)
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get meals from last N days
        cursor.execute('''
            SELECT m.*, GROUP_CONCAT(fi.food_name) as food_names
            FROM meals m
            LEFT JOIN food_items fi ON m.id = fi.meal_id
            WHERE m.user_id = ? AND m.timestamp >= datetime('now', '-{} days')
            GROUP BY m.id
            ORDER BY m.timestamp DESC
        '''.format(days), (user_id,))
        
        meals = cursor.fetchall()
        
        # Format response
        history = {}
        for meal in meals:
            date = meal[3].split(' ')[0]  # Extract date from timestamp
            if date not in history:
                history[date] = []
            
            history[date].append({
                'id': meal[0],
                'meal_type': meal[2],
                'time': meal[3].split(' ')[1][:5],  # Extract time
                'total_calories': meal[5],
                'total_protein': meal[6],
                'total_carbs': meal[7],
                'total_fat': meal[8],
                'total_fiber': meal[9],
                'food_items': meal[10].split(',') if meal[10] else []
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logging.error(f"Error getting meal history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logging.info("Starting FoodVision AI Backend (Simple Mode)")
    logging.info("Authentication endpoints available at /api/auth/*")
    logging.info("Health check available at /api/health")
    app.run(debug=True, host='0.0.0.0', port=5000)