#!/usr/bin/env python3
"""
Initialize authentication database for FoodVision AI
Ensures users table exists with proper schema
"""

import sqlite3
import os
from datetime import datetime

def init_auth_database():
    """Initialize authentication database"""
    print("🔐 Initializing authentication database...")
    
    # Connect to the existing database
    conn = sqlite3.connect('foodvision.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Check if users table exists and has the required columns
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Required columns for authentication
    required_columns = [
        'id', 'username', 'email', 'password_hash', 'created_at', 'updated_at',
        'daily_calorie_goal', 'height', 'weight', 'age', 'gender', 'activity_level',
        'dietary_restrictions', 'health_conditions', 'fitness_goals', 'timezone',
        'preferred_units', 'privacy_settings', 'notification_settings', 
        'subscription_tier', 'last_login', 'is_active'
    ]
    
    missing_columns = []
    for col in required_columns:
        if col not in column_names:
            missing_columns.append(col)
    
    if missing_columns:
        print(f"⚠️  Missing columns in users table: {missing_columns}")
        print("🔧 Adding missing columns...")
        
        # Add missing columns
        column_definitions = {
            'password_hash': 'TEXT',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'health_conditions': 'TEXT DEFAULT "[]"',
            'privacy_settings': 'TEXT DEFAULT "{}"',
            'notification_settings': 'TEXT DEFAULT "{}"',
            'subscription_tier': 'TEXT DEFAULT "free"',
            'last_login': 'TIMESTAMP',
            'is_active': 'BOOLEAN DEFAULT 1'
        }
        
        for col in missing_columns:
            if col in column_definitions:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {col} {column_definitions[col]}')
                    print(f"✅ Added column: {col}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Could not add column {col}: {e}")
    
    # Create indexes for better performance if they don't exist
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
        'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
        'CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)',
        'CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)'
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    # Update existing users to have is_active = 1 if NULL
    cursor.execute('UPDATE users SET is_active = 1 WHERE is_active IS NULL')
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Authentication database initialized successfully!")
    print(f"📊 Database location: {os.path.abspath('foodvision.db')}")

if __name__ == '__main__':
    init_auth_database()