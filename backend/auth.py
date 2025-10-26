"""
Authentication module for FoodVision AI
Handles user registration, login, and JWT token management
"""

import sqlite3
import hashlib
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
import re

auth_bp = Blueprint('auth', __name__)

# Database connection helper
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('foodvision.db')
    conn.row_factory = sqlite3.Row
    return conn

# Password hashing
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return hash_password(password) == hashed_password

# JWT token management
def generate_token(user_id, username):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config.get('SECRET_KEY', 'your-secret-key'), algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication decorator
def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Get user from database
            conn = get_db_connection()
            user = conn.execute(
                'SELECT * FROM users WHERE id = ? AND is_active = 1',
                (payload['user_id'],)
            ).fetchone()
            conn.close()
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Add user info to request context
            request.current_user = dict(user)
            
        except Exception as e:
            return jsonify({'error': 'Token verification failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# Validation helpers
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Add more password requirements if needed
    # if not re.search(r'[A-Z]', password):
    #     return False, "Password must contain at least one uppercase letter"
    # if not re.search(r'[a-z]', password):
    #     return False, "Password must contain at least one lowercase letter"
    # if not re.search(r'\d', password):
    #     return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_username(username):
    """Validate username"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

# Authentication routes
@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Required fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Validate username
        is_valid, message = validate_username(username)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Optional fields with defaults
        height = data.get('height')
        weight = data.get('weight')
        age = data.get('age')
        gender = data.get('gender', 'other')
        activity_level = data.get('activityLevel', 'moderate')
        daily_calorie_goal = data.get('dailyCalorieGoal', 2000)
        dietary_restrictions = json.dumps(data.get('dietaryRestrictions', []))
        fitness_goals = json.dumps(data.get('fitnessGoals', []))
        
        # Validate optional numeric fields
        if height is not None:
            try:
                height = float(height)
                if height < 100 or height > 250:
                    return jsonify({'error': 'Height must be between 100 and 250 cm'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Height must be a valid number'}), 400
        
        if weight is not None:
            try:
                weight = float(weight)
                if weight < 30 or weight > 300:
                    return jsonify({'error': 'Weight must be between 30 and 300 kg'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Weight must be a valid number'}), 400
        
        if age is not None:
            try:
                age = int(age)
                if age < 13 or age > 120:
                    return jsonify({'error': 'Age must be between 13 and 120'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Age must be a valid number'}), 400
        
        try:
            daily_calorie_goal = int(daily_calorie_goal)
            if daily_calorie_goal < 1000 or daily_calorie_goal > 5000:
                return jsonify({'error': 'Daily calorie goal must be between 1000 and 5000'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Daily calorie goal must be a valid number'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Database operations
        conn = get_db_connection()
        
        try:
            # Check if username or email already exists
            existing_user = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            ).fetchone()
            
            if existing_user:
                # Check which field is duplicate
                duplicate_check = conn.execute(
                    'SELECT username, email FROM users WHERE username = ? OR email = ?',
                    (username, email)
                ).fetchone()
                
                if duplicate_check['username'] == username:
                    return jsonify({'error': 'Username already exists'}), 409
                else:
                    return jsonify({'error': 'Email already exists'}), 409
            
            # Create new user
            cursor = conn.execute('''
                INSERT INTO users (
                    username, email, password_hash, height, weight, age, gender,
                    activity_level, daily_calorie_goal, dietary_restrictions,
                    fitness_goals, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, email, password_hash, height, weight, age, gender,
                activity_level, daily_calorie_goal, dietary_restrictions,
                fitness_goals, datetime.utcnow(), datetime.utcnow()
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Get the created user
            user = conn.execute(
                'SELECT id, username, email, created_at, daily_calorie_goal, height, weight, age, gender, activity_level FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            
            # Generate token
            token = generate_token(user_id, username)
            
            # Prepare user data for response (exclude sensitive info)
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'daily_calorie_goal': user['daily_calorie_goal'],
                'height': user['height'],
                'weight': user['weight'],
                'age': user['age'],
                'gender': user['gender'],
                'activity_level': user['activity_level']
            }
            
            return jsonify({
                'message': 'Account created successfully',
                'user': user_data,
                'token': token
            }), 201
            
        except sqlite3.IntegrityError as e:
            return jsonify({'error': 'Username or email already exists'}), 409
        except Exception as e:
            return jsonify({'error': 'Failed to create account'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': 'Invalid request data'}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        conn = get_db_connection()
        
        try:
            # Get user by email
            user = conn.execute(
                'SELECT * FROM users WHERE email = ? AND is_active = 1',
                (email,)
            ).fetchone()
            
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Verify password
            if not verify_password(password, user['password_hash']):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Update last login
            conn.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.utcnow(), user['id'])
            )
            conn.commit()
            
            # Generate token
            token = generate_token(user['id'], user['username'])
            
            # Prepare user data for response (exclude sensitive info)
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'daily_calorie_goal': user['daily_calorie_goal'],
                'height': user['height'],
                'weight': user['weight'],
                'age': user['age'],
                'gender': user['gender'],
                'activity_level': user['activity_level'],
                'last_login': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'message': 'Login successful',
                'user': user_data,
                'token': token
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Login failed'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': 'Invalid request data'}), 400

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        user = request.current_user
        
        # Remove sensitive information
        profile_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at'],
            'daily_calorie_goal': user['daily_calorie_goal'],
            'height': user['height'],
            'weight': user['weight'],
            'age': user['age'],
            'gender': user['gender'],
            'activity_level': user['activity_level'],
            'dietary_restrictions': json.loads(user['dietary_restrictions'] or '[]'),
            'fitness_goals': json.loads(user['fitness_goals'] or '[]'),
            'last_login': user['last_login']
        }
        
        return jsonify({'user': profile_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        # Fields that can be updated
        updatable_fields = {
            'daily_calorie_goal': int,
            'height': float,
            'weight': float,
            'age': int,
            'gender': str,
            'activity_level': str,
            'dietary_restrictions': list,
            'fitness_goals': list
        }
        
        update_data = {}
        
        for field, field_type in updatable_fields.items():
            if field in data:
                value = data[field]
                
                if field_type == list:
                    update_data[field] = json.dumps(value)
                else:
                    try:
                        if value is not None:
                            update_data[field] = field_type(value)
                        else:
                            update_data[field] = None
                    except (ValueError, TypeError):
                        return jsonify({'error': f'Invalid value for {field}'}), 400
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Validate ranges
        if 'height' in update_data and update_data['height'] is not None:
            if update_data['height'] < 100 or update_data['height'] > 250:
                return jsonify({'error': 'Height must be between 100 and 250 cm'}), 400
        
        if 'weight' in update_data and update_data['weight'] is not None:
            if update_data['weight'] < 30 or update_data['weight'] > 300:
                return jsonify({'error': 'Weight must be between 30 and 300 kg'}), 400
        
        if 'age' in update_data and update_data['age'] is not None:
            if update_data['age'] < 13 or update_data['age'] > 120:
                return jsonify({'error': 'Age must be between 13 and 120'}), 400
        
        if 'daily_calorie_goal' in update_data:
            if update_data['daily_calorie_goal'] < 1000 or update_data['daily_calorie_goal'] > 5000:
                return jsonify({'error': 'Daily calorie goal must be between 1000 and 5000'}), 400
        
        # Build update query
        set_clause = ', '.join([f'{field} = ?' for field in update_data.keys()])
        values = list(update_data.values()) + [datetime.utcnow(), user_id]
        
        conn = get_db_connection()
        
        try:
            conn.execute(
                f'UPDATE users SET {set_clause}, updated_at = ? WHERE id = ?',
                values
            )
            conn.commit()
            
            # Get updated user
            user = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            
            # Prepare response data
            profile_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'daily_calorie_goal': user['daily_calorie_goal'],
                'height': user['height'],
                'weight': user['weight'],
                'age': user['age'],
                'gender': user['gender'],
                'activity_level': user['activity_level'],
                'dietary_restrictions': json.loads(user['dietary_restrictions'] or '[]'),
                'fitness_goals': json.loads(user['fitness_goals'] or '[]'),
                'updated_at': user['updated_at']
            }
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': profile_data
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to update profile'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': 'Invalid request data'}), 400

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        conn = get_db_connection()
        
        try:
            # Get current user
            user = conn.execute(
                'SELECT password_hash FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            
            # Verify current password
            if not verify_password(current_password, user['password_hash']):
                return jsonify({'error': 'Current password is incorrect'}), 401
            
            # Hash new password
            new_password_hash = hash_password(new_password)
            
            # Update password
            conn.execute(
                'UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?',
                (new_password_hash, datetime.utcnow(), user_id)
            )
            conn.commit()
            
            return jsonify({'message': 'Password changed successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to change password'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': 'Invalid request data'}), 400

@auth_bp.route('/verify-token', methods=['POST'])
def verify_user_token():
    """Verify if token is valid"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token is required'}), 400
        
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'error': 'Token is invalid or expired'}), 401
        
        # Check if user still exists and is active
        conn = get_db_connection()
        
        try:
            user = conn.execute(
                'SELECT id, username, email FROM users WHERE id = ? AND is_active = 1',
                (payload['user_id'],)
            ).fetchone()
            
            if not user:
                return jsonify({'valid': False, 'error': 'User not found'}), 401
            
            return jsonify({
                'valid': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
            
        except Exception as e:
            return jsonify({'valid': False, 'error': 'Token verification failed'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'valid': False, 'error': 'Invalid request data'}), 400

# Error handlers
@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@auth_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500