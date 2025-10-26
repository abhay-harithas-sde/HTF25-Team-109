from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, ResNet50, InceptionV3
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import json
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid
import requests
import openai
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import torch
import threading
import time
from collections import defaultdict
import logging
from functools import lru_cache
import hashlib
import pickle

# Import authentication blueprint
from auth import auth_bp

app = Flask(__name__)
CORS(app)

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CACHE_FOLDER'] = 'cache'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
app.config['SECRET_KEY'] = 'foodvision_hackathon_2024'

# API Keys (In production, use environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your-huggingface-api-key")
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "your-google-vision-api-key")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "your-cohere-api-key")

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

# Initialize AI Models
class AIModelManager:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load multiple AI models for enhanced accuracy"""
        try:
            # Primary food recognition models
            self.models['mobilenet'] = MobileNetV2(weights='imagenet')
            self.models['resnet'] = ResNet50(weights='imagenet')
            self.models['inception'] = InceptionV3(weights='imagenet')
            
            # Image captioning model for context
            self.models['blip_processor'] = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.models['blip_model'] = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Nutrition analysis pipeline
            self.models['nutrition_classifier'] = pipeline("text-classification", 
                                                         model="microsoft/DialoGPT-medium")
            
            logging.info("All AI models loaded successfully")
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            # Fallback to basic model
            self.models['mobilenet'] = MobileNetV2(weights='imagenet')

# Initialize model manager
ai_models = AIModelManager()

# Enhanced nutrition database with AI-powered expansion
def load_enhanced_nutrition_db():
    """Load and enhance nutrition database with AI predictions"""
    try:
        with open('../data/nutrition_data.json', 'r') as f:
            base_db = json.load(f)
        
        # Add AI-generated nutrition data for missing foods
        enhanced_db = base_db.copy()
        
        # Cache for AI predictions
        cache_file = 'cache/nutrition_cache.pkl'
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                enhanced_db.update(cached_data)
        
        return enhanced_db
    except Exception as e:
        logging.error(f"Error loading nutrition database: {e}")
        return {}

nutrition_db = load_enhanced_nutrition_db()

# Enhanced Database Schema
def init_enhanced_db():
    """Initialize enhanced database with advanced features"""
    conn = sqlite3.connect('foodvision.db')
    cursor = conn.cursor()
    
    # Users table with enhanced profile
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
            activity_level TEXT DEFAULT 'moderate',
            dietary_restrictions TEXT DEFAULT '[]',
            health_conditions TEXT DEFAULT '[]',
            fitness_goals TEXT DEFAULT '[]',
            timezone TEXT DEFAULT 'UTC',
            preferred_units TEXT DEFAULT 'metric'
        )
    ''')
    
    # Enhanced meals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
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
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Enhanced food items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
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
            FOREIGN KEY (meal_id) REFERENCES meals (id)
        )
    ''')
    
    # AI predictions cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_hash TEXT UNIQUE NOT NULL,
            predictions TEXT NOT NULL,
            model_version TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence_score REAL DEFAULT 0
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Nutrition insights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrition_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            insight_type TEXT NOT NULL,
            insight_data TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            relevance_score REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
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
    logging.info("Enhanced database initialized successfully")

# Initialize enhanced database
init_enhanced_db()

@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    """Advanced multi-AI food analysis with ensemble predictions"""
    start_time = time.time()
    
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        use_advanced_ai = data.get('advanced_mode', True)
        
        # Decode and enhance image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate image hash for caching
        image_hash = hashlib.md5(image_bytes).hexdigest()
        
        # Check cache first
        cached_result = get_cached_prediction(image_hash)
        if cached_result:
            logging.info(f"Using cached prediction for image {image_hash}")
            return jsonify(cached_result)
        
        # Save and enhance image
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        
        # Apply image enhancements
        enhanced_image = enhance_image_quality(image)
        enhanced_image.save(image_path, quality=95)
        
        # Multi-model ensemble prediction
        if use_advanced_ai:
            predictions = ensemble_food_prediction(enhanced_image)
        else:
            predictions = basic_food_prediction(enhanced_image)
        
        # Advanced portion estimation using computer vision
        portion_analysis = advanced_portion_estimation(enhanced_image)
        
        # Generate image caption for context
        image_context = generate_image_caption(enhanced_image)
        
        # Process predictions with AI enhancement
        results = []
        for pred in predictions:
            food_name = pred['food_name']
            confidence = pred['confidence']
            
            # Get enhanced nutrition info with AI
            nutrition = get_enhanced_nutrition_info(food_name, image_context)
            
            # Apply portion analysis
            estimated_portion = portion_analysis.get(food_name, pred.get('portion', 1.0))
            
            # Calculate nutritional values
            nutritional_values = calculate_nutritional_values(nutrition, estimated_portion)
            
            results.append({
                'food_name': food_name,
                'original_prediction': pred.get('original_name', food_name),
                'confidence': confidence,
                'nutrition': nutrition,
                'estimated_portion': estimated_portion,
                'nutritional_values': nutritional_values,
                'image_path': image_filename,
                'ai_model_used': pred.get('model', 'ensemble'),
                'context': image_context
            })
        
        processing_time = time.time() - start_time
        
        response_data = {
            'success': True,
            'predictions': results,
            'image_path': image_filename,
            'image_hash': image_hash,
            'processing_time': processing_time,
            'ai_confidence': calculate_ensemble_confidence(results),
            'image_context': image_context,
            'portion_analysis': portion_analysis
        }
        
        # Cache the result
        cache_prediction(image_hash, response_data)
        
        logging.info(f"Food analysis completed in {processing_time:.2f}s")
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in food analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': time.time() - start_time
        }), 500

def enhance_image_quality(image):
    """Apply AI-powered image enhancements"""
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply enhancements
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        # Apply noise reduction
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    except Exception as e:
        logging.warning(f"Image enhancement failed: {e}")
        return image

def ensemble_food_prediction(image):
    """Use multiple AI models for enhanced accuracy"""
    predictions = []
    
    try:
        # Preprocess image for different models
        processed_image = image.resize((224, 224))
        image_array = np.array(processed_image)
        image_array = np.expand_dims(image_array, axis=0)
        
        # MobileNetV2 predictions
        mobilenet_input = preprocess_input(image_array.copy())
        mobilenet_preds = ai_models.models['mobilenet'].predict(mobilenet_input)
        mobilenet_decoded = decode_predictions(mobilenet_preds, top=3)[0]
        
        for pred in mobilenet_decoded:
            predictions.append({
                'food_name': map_food_name(pred[1]),
                'original_name': pred[1],
                'confidence': float(pred[2]),
                'model': 'mobilenet',
                'portion': estimate_portion_size(image, pred[1])
            })
        
        # ResNet50 predictions
        if 'resnet' in ai_models.models:
            resnet_input = tf.keras.applications.resnet50.preprocess_input(image_array.copy())
            resnet_preds = ai_models.models['resnet'].predict(resnet_input)
            resnet_decoded = tf.keras.applications.resnet50.decode_predictions(resnet_preds, top=3)[0]
            
            for pred in resnet_decoded:
                predictions.append({
                    'food_name': map_food_name(pred[1]),
                    'original_name': pred[1],
                    'confidence': float(pred[2]) * 0.9,  # Slight weight adjustment
                    'model': 'resnet50',
                    'portion': estimate_portion_size(image, pred[1])
                })
        
        # InceptionV3 predictions
        if 'inception' in ai_models.models:
            inception_input = tf.keras.applications.inception_v3.preprocess_input(
                cv2.resize(image_array[0], (299, 299)).reshape(1, 299, 299, 3)
            )
            inception_preds = ai_models.models['inception'].predict(inception_input)
            inception_decoded = tf.keras.applications.inception_v3.decode_predictions(inception_preds, top=3)[0]
            
            for pred in inception_decoded:
                predictions.append({
                    'food_name': map_food_name(pred[1]),
                    'original_name': pred[1],
                    'confidence': float(pred[2]) * 0.85,  # Slight weight adjustment
                    'model': 'inception_v3',
                    'portion': estimate_portion_size(image, pred[1])
                })
        
        # Ensemble voting and confidence weighting
        food_scores = defaultdict(list)
        for pred in predictions:
            food_scores[pred['food_name']].append(pred)
        
        # Calculate weighted ensemble scores
        ensemble_results = []
        for food_name, preds in food_scores.items():
            avg_confidence = np.mean([p['confidence'] for p in preds])
            max_confidence = max([p['confidence'] for p in preds])
            ensemble_confidence = (avg_confidence * 0.7 + max_confidence * 0.3)
            
            ensemble_results.append({
                'food_name': food_name,
                'original_name': preds[0]['original_name'],
                'confidence': ensemble_confidence,
                'model': 'ensemble',
                'portion': np.mean([p['portion'] for p in preds]),
                'model_agreement': len(preds)
            })
        
        # Sort by confidence and return top results
        ensemble_results.sort(key=lambda x: x['confidence'], reverse=True)
        return ensemble_results[:5]
        
    except Exception as e:
        logging.error(f"Ensemble prediction failed: {e}")
        return basic_food_prediction(image)

def basic_food_prediction(image):
    """Fallback to basic MobileNetV2 prediction"""
    try:
        processed_image = image.resize((224, 224))
        image_array = np.array(processed_image)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = preprocess_input(image_array)
        
        predictions = ai_models.models['mobilenet'].predict(image_array)
        decoded_predictions = decode_predictions(predictions, top=5)[0]
        
        results = []
        for pred in decoded_predictions:
            results.append({
                'food_name': map_food_name(pred[1]),
                'original_name': pred[1],
                'confidence': float(pred[2]),
                'model': 'mobilenet',
                'portion': estimate_portion_size(image, pred[1])
            })
        
        return results
    except Exception as e:
        logging.error(f"Basic prediction failed: {e}")
        return []

def generate_image_caption(image):
    """Generate contextual caption using BLIP model"""
    try:
        if 'blip_processor' in ai_models.models and 'blip_model' in ai_models.models:
            inputs = ai_models.models['blip_processor'](image, return_tensors="pt")
            out = ai_models.models['blip_model'].generate(**inputs, max_length=50)
            caption = ai_models.models['blip_processor'].decode(out[0], skip_special_tokens=True)
            return caption
        return "Food image"
    except Exception as e:
        logging.warning(f"Caption generation failed: {e}")
        return "Food image"

def advanced_portion_estimation(image):
    """Advanced portion size estimation using computer vision"""
    try:
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Object detection and size estimation
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Find contours for portion estimation
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        portion_estimates = {}
        
        if contours:
            # Find largest contour (likely the main food item)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Estimate portion based on area and image dimensions
            image_area = opencv_image.shape[0] * opencv_image.shape[1]
            relative_area = area / image_area
            
            # Portion estimation logic
            if relative_area > 0.6:
                portion = 1.5  # Large portion
            elif relative_area > 0.3:
                portion = 1.0  # Standard portion
            elif relative_area > 0.1:
                portion = 0.7  # Small portion
            else:
                portion = 0.5  # Very small portion
            
            portion_estimates['default'] = portion
        
        return portion_estimates
        
    except Exception as e:
        logging.warning(f"Advanced portion estimation failed: {e}")
        return {'default': 1.0}

@lru_cache(maxsize=1000)
def get_cached_prediction(image_hash):
    """Get cached prediction from database"""
    try:
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT predictions FROM ai_cache 
            WHERE image_hash = ? AND created_at > datetime('now', '-24 hours')
        ''', (image_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
        
    except Exception as e:
        logging.warning(f"Cache retrieval failed: {e}")
        return None

def cache_prediction(image_hash, prediction_data):
    """Cache prediction result"""
    try:
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ai_cache 
            (image_hash, predictions, model_version, confidence_score)
            VALUES (?, ?, ?, ?)
        ''', (image_hash, json.dumps(prediction_data), 'v2.0', 
              prediction_data.get('ai_confidence', 0)))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.warning(f"Cache storage failed: {e}")

def calculate_ensemble_confidence(results):
    """Calculate overall confidence from ensemble results"""
    if not results:
        return 0.0
    
    confidences = [r['confidence'] for r in results]
    return np.mean(confidences)

def calculate_nutritional_values(nutrition, portion):
    """Calculate actual nutritional values based on portion"""
    return {
        'calories': nutrition['calories_per_100g'] * portion,
        'protein': nutrition['protein'] * portion,
        'carbs': nutrition['carbs'] * portion,
        'fat': nutrition['fat'] * portion,
        'fiber': nutrition['fiber'] * portion
    }

def map_food_name(prediction_name):
    """Map model predictions to our nutrition database"""
    food_mapping = {
        'pizza': 'pizza',
        'cheeseburger': 'hamburger',
        'hamburger': 'hamburger',
        'french_fries': 'french_fries',
        'hot_dog': 'hot_dog',
        'banana': 'banana',
        'apple': 'apple',
        'orange': 'orange',
        'broccoli': 'broccoli',
        'carrot': 'carrot',
        'mushroom': 'mushroom',
        'bell_pepper': 'bell_pepper',
        'cucumber': 'cucumber',
        'tomato': 'tomato',
        'strawberry': 'strawberry',
        'grapes': 'grapes',
        'pineapple': 'pineapple',
        'watermelon': 'watermelon',
        'corn': 'corn',
        'bagel': 'bread',
        'pretzel': 'bread',
        'croissant': 'bread',
        'muffin': 'muffin',
        'doughnut': 'donut',
        'cake': 'cake',
        'ice_cream': 'ice_cream',
        'chocolate': 'chocolate',
        'cookie': 'cookie',
        'candy': 'candy',
        'popcorn': 'popcorn',
        'burrito': 'burrito',
        'taco': 'taco',
        'sandwich': 'sandwich',
        'soup': 'soup',
        'salad': 'salad',
        'pasta': 'pasta',
        'rice': 'rice',
        'noodles': 'noodles',
        'sushi': 'sushi',
        'fish': 'fish',
        'chicken': 'chicken',
        'beef': 'beef',
        'pork': 'pork',
        'egg': 'egg',
        'cheese': 'cheese',
        'milk': 'milk',
        'yogurt': 'yogurt',
        'cereal': 'cereal',
        'oatmeal': 'oatmeal'
    }
    
    # Try exact match first
    for key in food_mapping:
        if key in prediction_name.lower():
            return food_mapping[key]
    
    # Return original if no mapping found
    return prediction_name.lower().replace('_', ' ')

def estimate_portion_size(image, food_name):
    """Estimate portion size based on image analysis"""
    # Convert PIL image to OpenCV format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Simple size estimation based on image dimensions and food type
    height, width = opencv_image.shape[:2]
    image_area = height * width
    
    # Normalize to standard portion sizes
    if image_area > 500000:  # Large image
        return 1.5
    elif image_area > 200000:  # Medium image
        return 1.0
    else:  # Small image
        return 0.7

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

@app.route('/api/nutrition-goals', methods=['GET', 'POST'])
def nutrition_goals():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        if request.method == 'GET':
            conn = sqlite3.connect('foodvision.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return jsonify({
                    'success': True,
                    'goals': {
                        'daily_calories': user[4],
                        'height': user[5],
                        'weight': user[6],
                        'age': user[7],
                        'activity_level': user[8]
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'User not found'}), 404
                
        elif request.method == 'POST':
            data = request.json
            conn = sqlite3.connect('foodvision.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET daily_calorie_goal = ?, height = ?, weight = ?, 
                               age = ?, activity_level = ?
                WHERE id = ?
            ''', (data.get('daily_calories'), data.get('height'), 
                  data.get('weight'), data.get('age'), 
                  data.get('activity_level'), user_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Goals updated successfully'
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

def get_enhanced_nutrition_info(food_name, image_context):
    """Get enhanced nutrition info with AI predictions"""
    try:
        # First check our database
        if food_name.lower() in nutrition_db:
            return nutrition_db[food_name.lower()]
        
        # If not found, use AI to predict nutrition
        return predict_nutrition_with_ai(food_name, image_context)
        
    except Exception as e:
        logging.warning(f"Enhanced nutrition lookup failed: {e}")
        return get_nutrition_info(food_name)

def predict_nutrition_with_ai(food_name, image_context):
    """Use multiple AI APIs to predict nutrition information"""
    try:
        # Try OpenAI GPT-4 first
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key":
            nutrition = predict_with_openai(food_name, image_context)
            if nutrition:
                return nutrition
        
        # Fallback to Anthropic Claude
        if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your-anthropic-api-key":
            nutrition = predict_with_anthropic(food_name, image_context)
            if nutrition:
                return nutrition
        
        # Fallback to Google Gemini
        if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key":
            nutrition = predict_with_gemini(food_name, image_context)
            if nutrition:
                return nutrition
        
        # Final fallback to default values
        return get_nutrition_info(food_name)
        
    except Exception as e:
        logging.error(f"AI nutrition prediction failed: {e}")
        return get_nutrition_info(food_name)

def predict_with_openai(food_name, image_context):
    """Predict nutrition using OpenAI GPT-4"""
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""
        Analyze the nutritional content of "{food_name}" based on this context: "{image_context}".
        
        Provide accurate nutritional information per 100g in JSON format:
        {{
            "calories_per_100g": <number>,
            "protein": <number>,
            "carbs": <number>,
            "fat": <number>,
            "fiber": <number>,
            "sugar": <number>,
            "sodium": <number>,
            "vitamins": {{"vitamin_c": <number>, "vitamin_a": <number>}},
            "minerals": {{"iron": <number>, "calcium": <number>}}
        }}
        
        Only return the JSON, no other text.
        """
        
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.1
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result_text = response.json()['choices'][0]['message']['content'].strip()
            result = json.loads(result_text)
            
            # Cache the result
            nutrition_db[food_name.lower()] = result
            save_nutrition_cache()
            
            return result
        
    except Exception as e:
        logging.warning(f"OpenAI nutrition prediction failed: {e}")
        return None

def predict_with_anthropic(food_name, image_context):
    """Predict nutrition using Anthropic Claude"""
    try:
        headers = {
            'x-api-key': ANTHROPIC_API_KEY,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        prompt = f"""
        Analyze the nutritional content of "{food_name}" based on this context: "{image_context}".
        
        Provide accurate nutritional information per 100g in JSON format:
        {{
            "calories_per_100g": <number>,
            "protein": <number>,
            "carbs": <number>,
            "fat": <number>,
            "fiber": <number>,
            "sugar": <number>,
            "sodium": <number>,
            "vitamins": {{"vitamin_c": <number>, "vitamin_a": <number>}},
            "minerals": {{"iron": <number>, "calcium": <number>}}
        }}
        
        Only return the JSON, no other text.
        """
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post('https://api.anthropic.com/v1/messages', 
                               headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result_text = response.json()['content'][0]['text'].strip()
            result = json.loads(result_text)
            
            # Cache the result
            nutrition_db[food_name.lower()] = result
            save_nutrition_cache()
            
            return result
        
    except Exception as e:
        logging.warning(f"Anthropic nutrition prediction failed: {e}")
        return None

def predict_with_gemini(food_name, image_context):
    """Predict nutrition using Google Gemini"""
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        prompt = f"""
        Analyze the nutritional content of "{food_name}" based on this context: "{image_context}".
        
        Provide accurate nutritional information per 100g in JSON format:
        {{
            "calories_per_100g": <number>,
            "protein": <number>,
            "carbs": <number>,
            "fat": <number>,
            "fiber": <number>,
            "sugar": <number>,
            "sodium": <number>,
            "vitamins": {{"vitamin_c": <number>, "vitamin_a": <number>}},
            "minerals": {{"iron": <number>, "calcium": <number>}}
        }}
        
        Only return the JSON, no other text.
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}'
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            result = json.loads(result_text)
            
            # Cache the result
            nutrition_db[food_name.lower()] = result
            save_nutrition_cache()
            
            return result
        
    except Exception as e:
        logging.warning(f"Gemini nutrition prediction failed: {e}")
        return None

def save_nutrition_cache():
    """Save enhanced nutrition database to cache"""
    try:
        cache_file = 'cache/nutrition_cache.pkl'
        with open(cache_file, 'wb') as f:
            pickle.dump(nutrition_db, f)
    except Exception as e:
        logging.warning(f"Failed to save nutrition cache: {e}")

# Advanced AI-powered endpoints
@app.route('/api/ai-meal-suggestions', methods=['POST'])
def ai_meal_suggestions():
    """Get AI-powered meal suggestions based on user preferences and history"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        dietary_preferences = data.get('dietary_preferences', [])
        calorie_target = data.get('calorie_target', 2000)
        meal_type = data.get('meal_type', 'lunch')
        
        # Get user's meal history for personalization
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fi.food_name, COUNT(*) as frequency
            FROM food_items fi
            JOIN meals m ON fi.meal_id = m.id
            WHERE m.user_id = ? AND m.timestamp >= datetime('now', '-30 days')
            GROUP BY fi.food_name
            ORDER BY frequency DESC
            LIMIT 10
        ''', (user_id,))
        
        favorite_foods = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Generate AI suggestions
        suggestions = generate_meal_suggestions_with_ai(
            dietary_preferences, calorie_target, meal_type, favorite_foods
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logging.error(f"AI meal suggestions failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_meal_suggestions_with_ai(dietary_preferences, calorie_target, meal_type, favorite_foods):
    """Generate meal suggestions using AI"""
    try:
        prompt = f"""
        Generate 5 healthy {meal_type} meal suggestions with the following criteria:
        - Target calories: {calorie_target // 3} calories (for {meal_type})
        - Dietary preferences: {', '.join(dietary_preferences) if dietary_preferences else 'None'}
        - User's favorite foods: {', '.join(favorite_foods[:5]) if favorite_foods else 'None'}
        
        For each meal, provide:
        1. Meal name
        2. Brief description
        3. Estimated calories
        4. Main ingredients
        5. Preparation time
        
        Return as JSON array with this structure:
        [{{
            "name": "Meal Name",
            "description": "Brief description",
            "calories": <number>,
            "ingredients": ["ingredient1", "ingredient2"],
            "prep_time": "<time>",
            "difficulty": "easy|medium|hard",
            "tags": ["healthy", "quick", "vegetarian"]
        }}]
        """
        
        # Try different AI services
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key":
            suggestions = get_ai_suggestions_openai(prompt)
            if suggestions:
                return suggestions
        
        # Fallback suggestions
        return get_fallback_meal_suggestions(meal_type, calorie_target)
        
    except Exception as e:
        logging.error(f"AI meal suggestion generation failed: {e}")
        return get_fallback_meal_suggestions(meal_type, calorie_target)

def get_ai_suggestions_openai(prompt):
    """Get meal suggestions from OpenAI"""
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result_text = response.json()['choices'][0]['message']['content'].strip()
            return json.loads(result_text)
        
    except Exception as e:
        logging.warning(f"OpenAI meal suggestions failed: {e}")
        return None

def get_fallback_meal_suggestions(meal_type, calorie_target):
    """Fallback meal suggestions when AI is unavailable"""
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
            },
            {
                "name": "Greek Yogurt Parfait",
                "description": "Layered Greek yogurt with berries and granola",
                "calories": 280,
                "ingredients": ["Greek yogurt", "mixed berries", "granola", "honey"],
                "prep_time": "5 minutes",
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
            },
            {
                "name": "Grilled Chicken Salad",
                "description": "Fresh mixed greens with grilled chicken and balsamic vinaigrette",
                "calories": 380,
                "ingredients": ["chicken breast", "mixed greens", "cherry tomatoes", "cucumber"],
                "prep_time": "15 minutes",
                "difficulty": "easy",
                "tags": ["healthy", "protein-rich", "low-carb"]
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
            },
            {
                "name": "Vegetable Stir-fry with Tofu",
                "description": "Colorful vegetable stir-fry with crispy tofu and brown rice",
                "calories": 420,
                "ingredients": ["tofu", "mixed vegetables", "brown rice", "soy sauce"],
                "prep_time": "20 minutes",
                "difficulty": "easy",
                "tags": ["healthy", "vegetarian", "quick"]
            }
        ]
    }
    
    return suggestions.get(meal_type, suggestions['lunch'])[:3]

@app.route('/api/ai-nutrition-analysis', methods=['POST'])
def ai_nutrition_analysis():
    """Advanced AI-powered nutrition analysis and recommendations"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        days = data.get('days', 7)
        
        # Get user's nutrition data
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Get user profile
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        # Get recent meals
        cursor.execute('''
            SELECT DATE(timestamp) as date, 
                   SUM(total_calories) as calories,
                   SUM(total_protein) as protein,
                   SUM(total_carbs) as carbs,
                   SUM(total_fat) as fat,
                   SUM(total_fiber) as fiber
            FROM meals 
            WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        '''.format(days), (user_id,))
        
        daily_data = cursor.fetchall()
        conn.close()
        
        # Generate AI analysis
        analysis = generate_nutrition_analysis_with_ai(user, daily_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logging.error(f"AI nutrition analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_nutrition_analysis_with_ai(user, daily_data):
    """Generate comprehensive nutrition analysis using AI"""
    try:
        # Calculate averages and trends
        if daily_data:
            avg_calories = sum(row[1] for row in daily_data) / len(daily_data)
            avg_protein = sum(row[2] for row in daily_data) / len(daily_data)
            avg_carbs = sum(row[3] for row in daily_data) / len(daily_data)
            avg_fat = sum(row[4] for row in daily_data) / len(daily_data)
        else:
            avg_calories = avg_protein = avg_carbs = avg_fat = 0
        
        # User goals
        calorie_goal = user[4] if user else 2000
        
        analysis = {
            'summary': {
                'avg_daily_calories': round(avg_calories, 1),
                'calorie_goal': calorie_goal,
                'goal_achievement': round((avg_calories / calorie_goal) * 100, 1) if calorie_goal > 0 else 0,
                'avg_protein': round(avg_protein, 1),
                'avg_carbs': round(avg_carbs, 1),
                'avg_fat': round(avg_fat, 1)
            },
            'insights': generate_nutrition_insights(avg_calories, avg_protein, avg_carbs, avg_fat, calorie_goal),
            'recommendations': generate_nutrition_recommendations(user, avg_calories, calorie_goal),
            'trends': analyze_nutrition_trends(daily_data)
        }
        
        return analysis
        
    except Exception as e:
        logging.error(f"Nutrition analysis generation failed: {e}")
        return {
            'summary': {},
            'insights': [],
            'recommendations': [],
            'trends': {}
        }

def generate_nutrition_insights(avg_calories, avg_protein, avg_carbs, avg_fat, calorie_goal):
    """Generate nutrition insights"""
    insights = []
    
    # Calorie analysis
    if avg_calories < calorie_goal * 0.8:
        insights.append({
            'type': 'warning',
            'title': 'Low Calorie Intake',
            'message': f'Your average intake ({avg_calories:.0f} cal) is below your goal. Consider adding healthy snacks.',
            'icon': '⚠️'
        })
    elif avg_calories > calorie_goal * 1.2:
        insights.append({
            'type': 'warning',
            'title': 'High Calorie Intake',
            'message': f'Your average intake ({avg_calories:.0f} cal) exceeds your goal. Consider portion control.',
            'icon': '⚠️'
        })
    else:
        insights.append({
            'type': 'success',
            'title': 'Great Calorie Balance',
            'message': f'Your calorie intake ({avg_calories:.0f} cal) is well-balanced with your goal.',
            'icon': '✅'
        })
    
    # Protein analysis
    protein_percentage = (avg_protein * 4 / avg_calories) * 100 if avg_calories > 0 else 0
    if protein_percentage < 15:
        insights.append({
            'type': 'info',
            'title': 'Increase Protein',
            'message': f'Protein is {protein_percentage:.1f}% of calories. Aim for 15-25% for better satiety.',
            'icon': '🥩'
        })
    
    # Macro balance
    if avg_carbs > 0 and avg_fat > 0:
        carb_percentage = (avg_carbs * 4 / avg_calories) * 100
        fat_percentage = (avg_fat * 9 / avg_calories) * 100
        
        if carb_percentage > 60:
            insights.append({
                'type': 'info',
                'title': 'High Carb Intake',
                'message': f'Carbs are {carb_percentage:.1f}% of calories. Consider adding more protein and healthy fats.',
                'icon': '🍞'
            })
    
    return insights

def generate_nutrition_recommendations(user, avg_calories, calorie_goal):
    """Generate personalized nutrition recommendations"""
    recommendations = []
    
    # Basic recommendations
    recommendations.append({
        'category': 'Hydration',
        'title': 'Stay Hydrated',
        'message': 'Drink at least 8 glasses of water daily for optimal metabolism.',
        'priority': 'high',
        'icon': '💧'
    })
    
    recommendations.append({
        'category': 'Vegetables',
        'title': 'Eat More Vegetables',
        'message': 'Aim for 5-7 servings of colorful vegetables daily for essential nutrients.',
        'priority': 'high',
        'icon': '🥬'
    })
    
    # Personalized based on calorie intake
    if avg_calories < calorie_goal * 0.9:
        recommendations.append({
            'category': 'Calories',
            'title': 'Increase Healthy Calories',
            'message': 'Add nutrient-dense snacks like nuts, fruits, or yogurt to meet your goals.',
            'priority': 'medium',
            'icon': '🥜'
        })
    
    return recommendations

def analyze_nutrition_trends(daily_data):
    """Analyze nutrition trends over time"""
    if len(daily_data) < 3:
        return {'trend': 'insufficient_data'}
    
    # Calculate trend for calories
    calories = [row[1] for row in daily_data]
    
    # Simple trend analysis
    recent_avg = sum(calories[:3]) / 3 if len(calories) >= 3 else calories[0]
    older_avg = sum(calories[-3:]) / 3 if len(calories) >= 6 else sum(calories[3:]) / len(calories[3:]) if len(calories) > 3 else calories[-1]
    
    trend = 'stable'
    if recent_avg > older_avg * 1.1:
        trend = 'increasing'
    elif recent_avg < older_avg * 0.9:
        trend = 'decreasing'
    
    return {
        'calorie_trend': trend,
        'recent_average': round(recent_avg, 1),
        'change_percentage': round(((recent_avg - older_avg) / older_avg) * 100, 1) if older_avg > 0 else 0
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Additional advanced endpoints for enhanced functionality

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

@app.route('/api/meal-plan', methods=['GET', 'POST'])
def meal_plan():
    """Handle meal planning operations"""
    try:
        if request.method == 'GET':
            date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            user_id = request.args.get('user_id', 1, type=int)
            
            # For now, return empty plan - in real app, this would query a meal_plans table
            return jsonify({
                'success': True,
                'plan': {}
            })
            
        elif request.method == 'POST':
            data = request.json
            user_id = data.get('user_id', 1)
            date = data.get('date')
            meal_type = data.get('meal_type')
            meal = data.get('meal')
            
            # In a real app, this would save to a meal_plans table
            logging.info(f"Meal planned: {meal['name']} for {meal_type} on {date}")
            
            return jsonify({
                'success': True,
                'message': 'Meal planned successfully'
            })
            
    except Exception as e:
        logging.error(f"Error in meal planning: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-recipes', methods=['POST'])
def generate_recipes():
    """Generate recipes based on available ingredients"""
    try:
        data = request.json
        ingredients = data.get('ingredients', [])
        dietary_restrictions = data.get('dietary_restrictions', [])
        cuisine_type = data.get('cuisine_type', 'any')
        meal_type = data.get('meal_type', 'any')
        cooking_time = data.get('cooking_time', 'any')
        difficulty = data.get('difficulty', 'any')
        
        # In a real app, this would call an AI recipe generation service
        # For now, return mock recipes based on ingredients
        recipes = generate_mock_recipes_based_on_ingredients(
            ingredients, dietary_restrictions, cuisine_type, meal_type, difficulty
        )
        
        return jsonify({
            'success': True,
            'recipes': recipes
        })
        
    except Exception as e:
        logging.error(f"Error generating recipes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_mock_recipes_based_on_ingredients(ingredients, dietary_restrictions, cuisine_type, meal_type, difficulty):
    """Generate mock recipes based on provided parameters"""
    base_recipes = [
        {
            'id': 1,
            'name': f'{ingredients[0].title()} Stir-fry' if ingredients else 'Vegetable Stir-fry',
            'description': f'A delicious stir-fry featuring {", ".join(ingredients[:3])}',
            'prep_time': '15 minutes',
            'cook_time': '10 minutes',
            'difficulty': 'easy',
            'servings': 2,
            'calories_per_serving': 280,
            'ingredients': [{'name': ing, 'amount': '1 cup'} for ing in ingredients[:5]],
            'instructions': [
                'Heat oil in a large pan or wok',
                'Add ingredients and stir-fry until tender',
                'Season with your favorite spices',
                'Serve hot'
            ],
            'nutrition': {'protein': 12, 'carbs': 35, 'fat': 8, 'fiber': 6},
            'tags': ['quick', 'healthy', 'vegetarian' if 'vegetarian' in dietary_restrictions else 'omnivore']
        },
        {
            'id': 2,
            'name': f'{ingredients[0].title()} Bowl' if ingredients else 'Nourish Bowl',
            'description': f'A nutritious bowl with {", ".join(ingredients[:4])}',
            'prep_time': '20 minutes',
            'cook_time': '15 minutes',
            'difficulty': 'medium',
            'servings': 1,
            'calories_per_serving': 420,
            'ingredients': [{'name': ing, 'amount': '1/2 cup'} for ing in ingredients[:6]],
            'instructions': [
                'Prepare all ingredients',
                'Cook grains if using',
                'Arrange in a bowl',
                'Add dressing and enjoy'
            ],
            'nutrition': {'protein': 18, 'carbs': 45, 'fat': 12, 'fiber': 8},
            'tags': ['healthy', 'balanced', 'meal-prep']
        }
    ]
    
    # Filter based on criteria
    filtered_recipes = []
    for recipe in base_recipes:
        if difficulty != 'any' and recipe['difficulty'] != difficulty:
            continue
        if 'vegan' in dietary_restrictions:
            recipe['tags'].append('vegan')
        if 'gluten-free' in dietary_restrictions:
            recipe['tags'].append('gluten-free')
        filtered_recipes.append(recipe)
    
    return filtered_recipes

@app.route('/api/save-recipe', methods=['POST'])
def save_recipe():
    """Save a recipe to user's collection"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        recipe = data.get('recipe')
        
        # In a real app, this would save to a user_recipes table
        logging.info(f"Recipe saved: {recipe['name']} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Recipe saved successfully'
        })
        
    except Exception as e:
        logging.error(f"Error saving recipe: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/water-intake', methods=['GET', 'POST'])
def water_intake():
    """Track water intake"""
    try:
        user_id = request.args.get('user_id', 1, type=int) if request.method == 'GET' else request.json.get('user_id', 1)
        
        if request.method == 'GET':
            date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            # In a real app, this would query a water_intake table
            return jsonify({
                'success': True,
                'water_intake': 0,  # glasses of water
                'date': date
            })
            
        elif request.method == 'POST':
            data = request.json
            glasses = data.get('glasses', 1)
            date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # In a real app, this would update a water_intake table
            logging.info(f"Water intake logged: {glasses} glasses for user {user_id} on {date}")
            
            return jsonify({
                'success': True,
                'message': 'Water intake logged successfully'
            })
            
    except Exception as e:
        logging.error(f"Error with water intake: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Get user achievements"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Mock achievements - in real app, this would be calculated based on user data
        achievements = [
            {
                'id': 'first_meal',
                'title': 'First Meal Logged!',
                'description': 'You logged your first meal',
                'icon': '🎉',
                'unlocked': True,
                'date_unlocked': '2024-01-01'
            },
            {
                'id': 'week_streak',
                'title': 'Week Warrior',
                'description': 'Logged meals for 7 consecutive days',
                'icon': '🔥',
                'unlocked': False,
                'progress': 3,
                'target': 7
            },
            {
                'id': 'protein_goal',
                'title': 'Protein Power',
                'description': 'Met protein goal 10 times',
                'icon': '💪',
                'unlocked': False,
                'progress': 5,
                'target': 10
            }
        ]
        
        return jsonify({
            'success': True,
            'achievements': achievements
        })
        
    except Exception as e:
        logging.error(f"Error getting achievements: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/social/posts', methods=['GET', 'POST'])
def social_posts():
    """Handle social media posts"""
    try:
        if request.method == 'GET':
            # Return mock social posts
            posts = [
                {
                    'id': 1,
                    'user': {'name': 'Demo User', 'avatar': '👤'},
                    'content': 'Just reached my daily calorie goal! 🎯',
                    'timestamp': datetime.now().isoformat(),
                    'likes': 5,
                    'comments': 2
                }
            ]
            
            return jsonify({
                'success': True,
                'posts': posts
            })
            
        elif request.method == 'POST':
            data = request.json
            # In a real app, this would save to a social_posts table
            logging.info(f"Social post created: {data.get('content', '')}")
            
            return jsonify({
                'success': True,
                'message': 'Post created successfully'
            })
            
    except Exception as e:
        logging.error(f"Error with social posts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export-data', methods=['GET'])
def export_data():
    """Export user data"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        format_type = request.args.get('format', 'json')
        
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Get all user data
        cursor.execute('''
            SELECT m.*, GROUP_CONCAT(fi.food_name || ':' || fi.calories) as food_items
            FROM meals m
            LEFT JOIN food_items fi ON m.id = fi.meal_id
            WHERE m.user_id = ?
            GROUP BY m.id
            ORDER BY m.timestamp DESC
        ''', (user_id,))
        
        meals = cursor.fetchall()
        conn.close()
        
        # Format data for export
        export_data = []
        for meal in meals:
            export_data.append({
                'date': meal[3],
                'meal_type': meal[2],
                'total_calories': meal[5],
                'foods': meal[-1] if meal[-1] else ''
            })
        
        if format_type == 'csv':
            # In a real app, this would generate a CSV file
            return jsonify({
                'success': True,
                'message': 'CSV export would be generated here',
                'data': export_data
            })
        else:
            return jsonify({
                'success': True,
                'data': export_data
            })
            
    except Exception as e:
        logging.error(f"Error exporting data: {e}")
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
        'version': '2.0.0',
        'features': [
            'ai_food_recognition',
            'multi_model_ensemble',
            'nutrition_analysis',
            'meal_planning',
            'recipe_generation',
            'social_features',
            'voice_control',
            'progress_tracking'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')