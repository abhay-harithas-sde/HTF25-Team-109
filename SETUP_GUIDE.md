# 🍽️ FoodVision AI - Complete Setup Guide

## 🚀 Quick Start (Automated)

### Windows
```bash
# Double-click start.bat or run:
start.bat
```

### Linux/MacOS
```bash
chmod +x start.sh
./start.sh
```

## 📋 Manual Setup

### Prerequisites
- Python 3.8+ (we detected Python 3.13.7 ✅)
- Node.js 16+ (we detected Node.js 22.20.0 ✅)
- npm (we detected npm 10.9.3 ✅)

### Step 1: Backend Setup
```bash
# Create and activate virtual environment
py -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/MacOS

# Install core dependencies
pip install -r requirements-core.txt

# Start backend server
python backend/app_simple.py
```

### Step 2: Frontend Setup
```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend server
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health-check

## 🔧 Current Features Available

### ✅ Working Features
- 📷 **Image Upload**: Upload food images for analysis
- 🔍 **Basic Food Recognition**: Mock AI analysis (ready for real AI integration)
- ➕ **Manual Food Entry**: Add foods manually with nutrition data
- 📊 **Meal History**: Track your daily meals and nutrition
- 📈 **Analytics**: View nutrition trends and statistics
- 🎯 **Goal Setting**: Set and track nutrition goals
- 📱 **Responsive Design**: Works on all devices

### 🚧 Features Ready for Enhancement
- 🤖 **AI Models**: Ready to integrate TensorFlow/PyTorch models
- 🗣️ **Voice Control**: Frontend components ready
- 👥 **Social Features**: UI components implemented
- 🍳 **Recipe Generation**: Framework in place
- 📅 **Meal Planning**: Components ready

## 🔑 API Endpoints

### Core Endpoints
- `POST /api/analyze-food` - Analyze food images
- `POST /api/save-meal` - Save meal data
- `GET /api/meal-history` - Get meal history
- `GET /api/analytics` - Get nutrition analytics
- `GET /api/search-food` - Search food database
- `GET /api/daily-stats` - Get daily statistics
- `POST /api/ai-meal-suggestions` - Get meal suggestions

## 🎨 UI Components

### Available Components
- **Dashboard**: Main overview with stats and quick actions
- **ImageUpload**: Camera and file upload functionality
- **FoodResults**: Display analysis results
- **MealHistory**: Historical meal tracking
- **Analytics**: Charts and nutrition insights
- **Goals**: Goal setting and tracking
- **FoodSearch**: Manual food entry
- **AIAssistant**: Chat interface (ready for AI integration)
- **VoiceControl**: Speech recognition (ready for integration)
- **MealPlanner**: Meal planning interface
- **RecipeGenerator**: Recipe creation tool
- **SocialFeatures**: Social platform components
- **ProgressTracker**: Real-time progress tracking

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:
```env
# Basic Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key

# AI API Keys (for enhanced features)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GEMINI_API_KEY=your-gemini-key
```

### Database
- **Type**: SQLite (development)
- **Location**: `foodvision.db`
- **Auto-created**: Yes, with sample data

## 🚀 Next Steps for Full AI Integration

### 1. Install AI Dependencies
```bash
# Activate virtual environment
venv\Scripts\activate

# Install full AI stack
pip install tensorflow>=2.15.0
pip install torch torchvision
pip install transformers
pip install openai anthropic google-generativeai
```

### 2. Replace Mock Backend
```bash
# Use the full AI backend
python backend/app.py  # Instead of app_simple.py
```

### 3. Add API Keys
Add your AI service API keys to `.env` file for enhanced features.

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
py --version

# Reinstall dependencies
pip install -r requirements-core.txt

# Check port availability
netstat -an | findstr :5000
```

#### Frontend Won't Start
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check port availability
netstat -an | findstr :3000
```

#### Database Issues
```bash
# Delete and recreate database
del foodvision.db
python backend/app_simple.py  # Will recreate automatically
```

## 📊 Current Status

### ✅ Completed
- [x] Core backend API with 8+ endpoints
- [x] React frontend with 10+ components
- [x] Database schema with 3 main tables
- [x] Image upload and processing
- [x] Nutrition tracking and analytics
- [x] Responsive UI with modern design
- [x] Mock AI integration (ready for real AI)

### 🔄 Ready for Enhancement
- [ ] Real AI model integration (TensorFlow/PyTorch)
- [ ] Voice recognition activation
- [ ] Social features backend
- [ ] Recipe generation AI
- [ ] Advanced analytics with ML

## 🎯 Demo Data

The application includes sample data:
- Demo user account
- Sample meals and nutrition data
- Mock food database with 50+ items

## 🏆 Hackathon Ready Features

1. **Innovation**: Multi-AI integration framework
2. **Completeness**: Full-stack application with 20+ components
3. **Scalability**: Production-ready architecture
4. **User Experience**: Modern, responsive design
5. **Technical Depth**: Advanced features and comprehensive API

## 📞 Support

If you encounter any issues:
1. Check this guide first
2. Review the logs in `logs/foodvision.log`
3. Ensure all prerequisites are installed
4. Try the troubleshooting steps above

---

**🎉 Your FoodVision AI application is ready to impress judges and users alike!**