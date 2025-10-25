#!/usr/bin/env python3
"""
FoodVision AI Setup Script
Automated setup for the Advanced AI-Based Calorie & Dish Identifier
"""

import os
import subprocess
import sys
import sqlite3
import json
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_system_requirements():
    """Check if system meets requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check Node.js
    success, output = run_command("node --version")
    if not success:
        print("❌ Node.js is not installed. Please install Node.js 16+ first.")
        return False
    
    node_version = output.strip().replace('v', '')
    print(f"✅ Node.js {node_version} detected")
    
    # Check npm
    success, output = run_command("npm --version")
    if not success:
        print("❌ npm is not installed")
        return False
    
    print(f"✅ npm {output.strip()} detected")
    
    return True

def setup_environment():
    """Setup environment variables and configuration"""
    print("🔧 Setting up environment...")
    
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# FoodVision AI Environment Variables
# Replace with your actual API keys

# OpenAI API Key (for GPT-4 nutrition analysis)
OPENAI_API_KEY=your-openai-api-key

# Anthropic API Key (for Claude nutrition analysis)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Google Gemini API Key
GEMINI_API_KEY=your-gemini-api-key

# Cohere API Key
COHERE_API_KEY=your-cohere-api-key

# Hugging Face API Key
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Google Vision API Key
GOOGLE_VISION_API_KEY=your-google-vision-api-key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///foodvision.db

# Security
SECRET_KEY=your-secret-key-change-this-in-production
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
    else:
        print("✅ .env file already exists")

def create_config_files():
    """Create configuration files"""
    print("📝 Creating configuration files...")
    
    # Create config directory
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    # AI models configuration
    ai_config = {
        "models": {
            "primary": "mobilenet_v2",
            "ensemble": ["mobilenet_v2", "resnet50", "inception_v3"],
            "text_analysis": "blip",
            "nutrition_ai": ["openai", "anthropic", "gemini"]
        },
        "confidence_threshold": 0.3,
        "max_predictions": 5,
        "cache_enabled": True,
        "cache_duration_hours": 24
    }
    
    with open(config_dir / 'ai_config.json', 'w') as f:
        json.dump(ai_config, f, indent=2)
    
    # App configuration
    app_config = {
        "app_name": "FoodVision AI",
        "version": "2.0.0",
        "features": {
            "ai_recognition": True,
            "voice_control": True,
            "social_features": True,
            "meal_planning": True,
            "recipe_generation": True,
            "progress_tracking": True,
            "dark_mode": True,
            "offline_mode": False
        },
        "limits": {
            "max_file_size_mb": 32,
            "max_daily_uploads": 100,
            "max_meal_items": 20
        }
    }
    
    with open(config_dir / 'app_config.json', 'w') as f:
        json.dump(app_config, f, indent=2)
    
    print("✅ Configuration files created")

def setup_advanced_database():
    """Setup advanced database with all tables"""
    print("🗄️ Setting up advanced database...")
    
    conn = sqlite3.connect('foodvision.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Users table with enhanced profile
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
    
    # Enhanced meals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE
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
            confidence_score REAL DEFAULT 0,
            expires_at TIMESTAMP
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, preference_key)
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
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Meal plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
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
        CREATE TABLE IF NOT EXISTS recipes (
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
        CREATE TABLE IF NOT EXISTS water_intake (
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
        CREATE TABLE IF NOT EXISTS achievements (
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
        CREATE TABLE IF NOT EXISTS social_posts (
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
    
    # Create indexes for better performance
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_meals_user_date ON meals(user_id, timestamp)',
        'CREATE INDEX IF NOT EXISTS idx_food_items_meal ON food_items(meal_id)',
        'CREATE INDEX IF NOT EXISTS idx_ai_cache_hash ON ai_cache(image_hash)',
        'CREATE INDEX IF NOT EXISTS idx_user_preferences ON user_preferences(user_id, preference_key)',
        'CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date ON meal_plans(user_id, date)',
        'CREATE INDEX IF NOT EXISTS idx_water_intake_user_date ON water_intake(user_id, date)',
        'CREATE INDEX IF NOT EXISTS idx_social_posts_user ON social_posts(user_id, created_at)'
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    # Create default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, email, daily_calorie_goal, gender, age, height, weight)
            VALUES ('admin', 'admin@foodvision.ai', 2000, 'other', 25, 170, 70)
        ''')
        
        cursor.execute('''
            INSERT INTO users (username, email, daily_calorie_goal, gender, age, height, weight)
            VALUES ('demo_user', 'demo@foodvision.ai', 2000, 'other', 30, 165, 65)
        ''')
    
    conn.commit()
    conn.close()
    print("✅ Advanced database setup completed")

def setup_backend():
    """Setup Python backend dependencies"""
    print("🐍 Setting up Python backend...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        # Try different Python commands
        python_commands = ['py', 'python3', 'python']
        success = False
        for cmd in python_commands:
            success, output = run_command(f"{cmd} -m venv venv")
            if success:
                break
        
        if not success:
            print(f"❌ Failed to create virtual environment: {output}")
            return False
        print("✅ Virtual environment created")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip.exe"
        python_cmd = "venv\\Scripts\\python.exe"
    else:  # Unix/Linux/MacOS
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    print("📦 Installing Python dependencies...")
    # Try to upgrade pip, but don't fail if it doesn't work
    success, output = run_command(f"{pip_cmd} install --upgrade pip")
    if not success:
        print(f"⚠️ Could not upgrade pip: {output}")
        print("📦 Continuing with existing pip version...")
    
    success, output = run_command(f"{pip_cmd} install -r requirements.txt")
    if not success:
        print(f"❌ Failed to install Python dependencies: {output}")
        return False
    
    print("✅ Python dependencies installed successfully")
    
    # Initialize advanced database
    setup_advanced_database()
    
    return True

def setup_frontend():
    """Setup React frontend dependencies"""
    print("⚛️ Setting up React frontend...")
    
    frontend_path = "frontend"
    
    # Check if npm is installed
    success, _ = run_command("npm --version")
    if not success:
        print("❌ npm is not installed. Please install Node.js and npm first.")
        return False
    
    # Clear npm cache
    print("🧹 Clearing npm cache...")
    run_command("npm cache clean --force", cwd=frontend_path)
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    success, output = run_command("npm install", cwd=frontend_path)
    if not success:
        print(f"❌ Failed to install frontend dependencies: {output}")
        # Try with legacy peer deps flag
        print("🔄 Retrying with legacy peer deps...")
        success, output = run_command("npm install --legacy-peer-deps", cwd=frontend_path)
        if not success:
            print(f"❌ Failed to install frontend dependencies: {output}")
            return False
    
    # Install additional development dependencies
    print("🛠️ Installing development tools...")
    dev_deps = [
        "@types/react",
        "@types/react-dom",
        "eslint-plugin-react-hooks",
        "prettier",
        "autoprefixer",
        "postcss"
    ]
    
    for dep in dev_deps:
        run_command(f"npm install --save-dev {dep}", cwd=frontend_path)
    
    print("✅ Frontend dependencies installed successfully")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "uploads",
        "models",
        "logs",
        "cache",
        "config",
        "data/exports",
        "data/backups",
        "static/images",
        "static/audio",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .gitkeep files for empty directories
    gitkeep_dirs = ["uploads", "cache", "temp", "logs"]
    for directory in gitkeep_dirs:
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write("# This file keeps the directory in git\n")

def download_ai_models():
    """Download and setup AI models"""
    print("🤖 Setting up AI models...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Create model info file
    model_info = {
        "models": {
            "mobilenet_v2": {
                "status": "built-in",
                "description": "Primary food recognition model"
            },
            "resnet50": {
                "status": "built-in", 
                "description": "Secondary food recognition model"
            },
            "inception_v3": {
                "status": "built-in",
                "description": "Tertiary food recognition model"
            },
            "blip": {
                "status": "download_required",
                "description": "Image captioning model",
                "size": "990MB"
            }
        },
        "setup_date": str(datetime.now()),
        "version": "2.0.0"
    }
    
    with open(models_dir / "model_info.json", 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print("✅ AI models configuration created")
    print("ℹ️  Some models will be downloaded automatically on first use")

def display_instructions():
    """Display setup completion instructions"""
    print("\n" + "="*80)
    print("🎉 FoodVision AI Setup Complete!")
    print("="*80)
    print("\n🚀 QUICK START:")
    print("\n1. 🐍 Start the AI backend server:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python backend\\app.py")
    else:  # Unix/Linux/MacOS
        print("   venv/bin/python backend/app.py")
    print("\n2. ⚛️ In a new terminal, start the React frontend:")
    print("   cd frontend")
    print("   npm start")
    print("\n3. 🌐 Open your browser and navigate to:")
    print("   http://localhost:3000")
    print("\n" + "="*80)
    print("🔥 ADVANCED FEATURES INCLUDED:")
    print("="*80)
    print("🤖 AI & Machine Learning:")
    print("   • Multi-model ensemble food recognition")
    print("   • GPT-4/Claude/Gemini nutrition analysis")
    print("   • Computer vision portion estimation")
    print("   • Image enhancement and preprocessing")
    print("   • Contextual food understanding")
    print("\n🎯 Smart Features:")
    print("   • AI-powered meal suggestions")
    print("   • Intelligent recipe generation")
    print("   • Voice control and commands")
    print("   • Real-time progress tracking")
    print("   • Personalized nutrition insights")
    print("\n📱 User Experience:")
    print("   • Modern responsive design")
    print("   • Dark/light mode support")
    print("   • Smooth animations and transitions")
    print("   • Progressive Web App capabilities")
    print("   • Offline functionality (partial)")
    print("\n👥 Social & Gamification:")
    print("   • Social feed and sharing")
    print("   • Achievement system")
    print("   • Challenge participation")
    print("   • Friend connections")
    print("   • Leaderboards")
    print("\n📊 Analytics & Insights:")
    print("   • Advanced nutrition analytics")
    print("   • Trend analysis and predictions")
    print("   • Goal tracking and recommendations")
    print("   • Export capabilities")
    print("   • Health insights dashboard")
    print("\n" + "="*80)
    print("⚙️ CONFIGURATION:")
    print("="*80)
    print("📝 Edit .env file to add your API keys:")
    print("   • OpenAI API key for GPT-4 analysis")
    print("   • Anthropic API key for Claude analysis")
    print("   • Google Gemini API key")
    print("   • Other AI service keys")
    print("\n🔧 Configuration files created:")
    print("   • config/ai_config.json - AI model settings")
    print("   • config/app_config.json - Application settings")
    print("   • .env - Environment variables")
    print("\n" + "="*80)
    print("💡 PRO TIPS:")
    print("="*80)
    print("📷 For best food recognition:")
    print("   • Use good lighting and clear images")
    print("   • Center food items in the frame")
    print("   • Avoid cluttered backgrounds")
    print("\n🎯 For accurate tracking:")
    print("   • Set up your personal profile and goals")
    print("   • Log meals consistently")
    print("   • Review AI suggestions and insights")
    print("\n🚀 For optimal performance:")
    print("   • Add your AI API keys for enhanced features")
    print("   • Enable notifications for reminders")
    print("   • Use voice commands for hands-free logging")
    print("\n" + "="*80)
    print("🆘 NEED HELP?")
    print("="*80)
    print("📚 Check the documentation in the README.md")
    print("🐛 Report issues on GitHub")
    print("💬 Join our community for support")
    print("\n🎊 Ready to revolutionize your nutrition tracking!")
    print("="*80)

def main():
    """Main setup function"""
    print("🍽️ FoodVision AI - Advanced Nutrition Tracker Setup")
    print("=" * 60)
    print("🚀 Setting up your AI-powered nutrition companion...")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Create configuration files
    create_config_files()
    
    # Create directories
    create_directories()
    
    # Download AI models
    download_ai_models()
    
    # Setup backend
    print("\n🔧 Setting up backend services...")
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    print("\n🔧 Setting up frontend application...")
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Final setup steps
    print("\n🔧 Finalizing setup...")
    
    # Create sample data
    create_sample_data()
    
    # Display instructions
    display_instructions()

def create_sample_data():
    """Create sample data for demonstration"""
    print("📊 Creating sample data...")
    
    try:
        conn = sqlite3.connect('foodvision.db')
        cursor = conn.cursor()
        
        # Add sample nutrition data if not exists
        cursor.execute('SELECT COUNT(*) FROM meals WHERE user_id = 2')
        if cursor.fetchone()[0] == 0:
            # Add sample meals for demo user
            sample_meals = [
                (2, 'breakfast', '2024-01-15 08:00:00', '', 450, 25, 45, 18, 8, 5, 200),
                (2, 'lunch', '2024-01-15 13:00:00', '', 620, 35, 55, 22, 12, 8, 350),
                (2, 'dinner', '2024-01-15 19:00:00', '', 580, 40, 35, 28, 15, 6, 400),
                (2, 'breakfast', '2024-01-16 08:30:00', '', 380, 20, 50, 15, 6, 4, 180),
                (2, 'lunch', '2024-01-16 12:45:00', '', 520, 28, 48, 20, 10, 7, 320)
            ]
            
            for meal in sample_meals:
                cursor.execute('''
                    INSERT INTO meals (user_id, meal_type, timestamp, image_path, 
                                     total_calories, total_protein, total_carbs, total_fat, 
                                     total_fiber, total_sugar, total_sodium)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', meal)
        
        conn.commit()
        conn.close()
        print("✅ Sample data created")
        
    except Exception as e:
        print(f"⚠️ Could not create sample data: {e}")

# Add missing import
from datetime import datetime

if __name__ == "__main__":
    main()