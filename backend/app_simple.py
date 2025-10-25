from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import json
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid
import requests
import threading
import time
from collections import defaultdict
import logging
from functools import lru_cache
import hashlib
import pickle

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CACHE_FOLDER'] = 'cache'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
app.config['SECRET_KEY'] = 'foodvision_hackathon_2024'

# Create directories
for folder in ['uploads', 'cache', 'models', 'logs']:
    os.makedirs(folder, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/foodvision.log'),
        logging.StreamHandler()
    ]
)

# Load nutrition database
def load_nutrition_db():
    """Load nutrition database"""
    try:
        with open('../data/nutrition_data.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading nutrition database: {e}")
        return {}

nutrition_db = load_nutrition_db()

# Initialize Database
def init_db():
    """Initialize database with basic tables"""
    conn = sqlite3.connect('foodvision.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            daily_calorie_goal INTEGER DEFAULT 2000,
            height REAL,
            weight REAL,
            age INTEGER,
            gender TEXT DEFAULT 'other',
            activity_level TEXT DEFAULT 'moderate'
        )
    ''')
    
    # Meals table
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
    
    # Food items table
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
    
    # Create default user if not exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, email, daily_calorie_goal, gender, age, height, weight)
            VALUES ('demo_user', 'demo@foodvision.com', 2000, 'other', 25, 170, 70)
        ''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

# Initialize database
init_db()

@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    """Basic food analysis without AI models"""
    start_time = time.time()
    
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        
        # Decode image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save image
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path, quality=95)
        
        # Mock food recognition (replace with actual AI when models are available)
        mock_predictions = [
            {
                'food_name': 'mixed_salad',
                'confidence': 0.85,
                'nutrition': get_nutrition_info('mixed_salad'),
                'estimated_portion': 1.0,
                'nutritional_values': calculate_nutritional_values(get_nutrition_info('mixed_salad'), 1.0)
            },
            {
                'food_name': 'chicken_breast',
                'confidence': 0.75,
                'nutrition': get_nutrition_info('chicken_breast'),
                'estimated_portion': 0.8,
                'nutritional_values': calculate_nutritional_values(get_nutrition_info('chicken_breast'), 0.8)
            }
        ]
        
        processing_time = time.time() - start_time
        
        response_data = {
            'success': True,
            'predictions': mock_predictions,
            'image_path': image_filename,
            'processing_time': processing_time,
            'ai_confidence': 0.8,
            'image_context': 'Healthy meal with vegetables and protein'
        }
        
        logging.info(f"Food analysis completed in {processing_time:.2f}s")
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in food analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': time.time() - start_time
        }), 500

def get_nutrition_info(food_name):
    """Get nutritional information for a food item"""
    default_nutrition = {
        'calories_per_100g': 200,
        'protein': 10,
        'carbs': 30,
        'fat': 8,
        'fiber': 3
    }
    
    return nutrition_db.get(food_name.lower(), default_nutrition)

def calculate_nutritional_values(nutrition, portion):
    """Calculate actual nutritional values based on portion"""
    return {
        'calories': nutrition['calories_per_100g'] * portion,
        'protein': nutrition['protein'] * portion,
        'carbs': nutrition['carbs'] * portion,
        'fat': nutrition['fat'] * portion,
        'fiber': nutrition['fiber'] * portion
    }

@app.route('/api/save-meal', methods=['POST'])
def save_meal():
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        meal_type = data.get('meal_type', 'snack')
        food_items = data.get('items', [])
        image_path = data.get('image_path', '')
        
        # Calculate totals
        total_calories = sum(item.get('calories', 0) for item in food_items)
        total_protein = sum(item.get('protein', 0) for item in food_items)
        total_carbs = sum(item.get('carbs', 0) for item in food_items)
        total_fat = sum(item.get('fat', 0) for item in food_items)
        total_fiber = sum(item.get('fiber', 0) for item in food_items)
        
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Insert meal
        cursor.execute('''
            INSERT INTO meals (user_id, meal_type, image_path, total_calories, 
                             total_protein, total_carbs, total_fat, total_fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_type, image_path, total_calories, total_protein, 
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-history', methods=['GET'])
def get_meal_history():
    try:
        days = request.args.get('days', 7, type=int)
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Get meals from last N days
        cursor.execute('''
            SELECT m.id, m.user_id, m.meal_type, 
                   strftime('%Y-%m-%d %H:%M:%S', m.timestamp) as timestamp_str,
                   m.image_path, m.total_calories, m.total_protein, m.total_carbs, 
                   m.total_fat, m.total_fiber, GROUP_CONCAT(fi.food_name) as food_names
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
            # Now timestamp is already a string from the query
            timestamp_str = meal[3]  # This is now timestamp_str from the query
            date = timestamp_str.split(' ')[0]
            time = timestamp_str.split(' ')[1][:5]
            
            if date not in history:
                history[date] = []
            
            history[date].append({
                'id': meal[0],
                'meal_type': meal[2],
                'time': time,
                'total_calories': meal[5],
                'total_protein': meal[6],
                'total_carbs': meal[7],
                'total_fat': meal[8],
                'total_fiber': meal[9],
                'food_items': meal[10].split(',') if meal[10] else [],
                'image_path': meal[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        days = request.args.get('days', 30, type=int)
        
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Daily calorie trends
        cursor.execute('''
            SELECT DATE(timestamp) as date, SUM(total_calories) as daily_calories
            FROM meals 
            WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        '''.format(days), (user_id,))
        
        daily_calories = [{'date': row[0], 'calories': row[1]} for row in cursor.fetchall()]
        
        # Macro breakdown
        cursor.execute('''
            SELECT SUM(total_protein) as protein, SUM(total_carbs) as carbs, 
                   SUM(total_fat) as fat, SUM(total_fiber) as fiber
            FROM meals 
            WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
        '''.format(days), (user_id,))
        
        macros = cursor.fetchone()
        
        # Most frequent foods
        cursor.execute('''
            SELECT fi.food_name, COUNT(*) as frequency
            FROM food_items fi
            JOIN meals m ON fi.meal_id = m.id
            WHERE m.user_id = ? AND m.timestamp >= datetime('now', '-{} days')
            GROUP BY fi.food_name
            ORDER BY frequency DESC
            LIMIT 10
        '''.format(days), (user_id,))
        
        frequent_foods = [{'food': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'analytics': {
                'daily_calories': daily_calories,
                'macros': {
                    'protein': macros[0] or 0,
                    'carbs': macros[1] or 0,
                    'fat': macros[2] or 0,
                    'fiber': macros[3] or 0
                },
                'frequent_foods': frequent_foods
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search-food', methods=['GET'])
def search_food():
    try:
        query = request.args.get('q', '').lower()
        
        # Search in nutrition database
        results = []
        for food_name, nutrition in nutrition_db.items():
            if query in food_name.lower():
                results.append({
                    'food_name': food_name,
                    'nutrition': nutrition
                })
        
        return jsonify({
            'success': True,
            'results': results[:10]  # Limit to 10 results
        })
        
    except Exception as e:
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
        
        conn = sqlite3.connect('foodvision.db')
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
            'water': 0,  # This would come from a separate water tracking table
            'steps': 0   # This would integrate with fitness trackers
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

@app.route('/api/ai-meal-suggestions', methods=['POST'])
def ai_meal_suggestions():
    """Mock AI meal suggestions"""
    try:
        data = request.json
        meal_type = data.get('meal_type', 'lunch')
        
        # Mock suggestions based on meal type
        suggestions = {
            'breakfast': [
                {
                    "name": "Avocado Toast with Eggs",
                    "description": "Whole grain toast topped with mashed avocado and poached eggs",
                    "calories": 350,
                    "ingredients": ["whole grain bread", "avocado", "eggs", "tomato"],
                    "prep_time": "10 minutes",
                    "difficulty": "easy",
                    "tags": ["healthy", "protein-rich", "quick"]
                }
            ],
            'lunch': [
                {
                    "name": "Quinoa Buddha Bowl",
                    "description": "Nutritious bowl with quinoa, roasted vegetables, and tahini dressing",
                    "calories": 450,
                    "ingredients": ["quinoa", "sweet potato", "chickpeas", "spinach", "tahini"],
                    "prep_time": "25 minutes",
                    "difficulty": "medium",
                    "tags": ["healthy", "vegetarian", "filling"]
                }
            ],
            'dinner': [
                {
                    "name": "Salmon with Roasted Vegetables",
                    "description": "Baked salmon fillet with seasonal roasted vegetables",
                    "calories": 520,
                    "ingredients": ["salmon fillet", "broccoli", "bell peppers", "olive oil"],
                    "prep_time": "30 minutes",
                    "difficulty": "medium",
                    "tags": ["healthy", "omega-3", "protein-rich"]
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'suggestions': suggestions.get(meal_type, suggestions['lunch'])
        })
        
    except Exception as e:
        logging.error(f"AI meal suggestions failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health-check', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-simple',
        'features': [
            'basic_food_recognition',
            'nutrition_analysis',
            'meal_tracking',
            'analytics'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')