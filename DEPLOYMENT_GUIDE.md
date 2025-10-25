# 🚀 FoodVision AI - Deployment Guide

## 🌐 Quick Deployment Options

### 1. 🔥 Vercel (Frontend) + Railway (Backend)

#### Frontend on Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

#### Backend on Railway
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the backend folder
4. Add environment variables
5. Deploy automatically

### 2. 🐳 Docker Deployment

#### Create Dockerfile for Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-core.txt .
RUN pip install -r requirements-core.txt

COPY backend/ ./backend/
COPY data/ ./data/
COPY create_database.py .

RUN python create_database.py

EXPOSE 5000
CMD ["python", "backend/app_simple.py"]
```

#### Create Dockerfile for Frontend
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: 
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### 3. ☁️ Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: python backend/app_simple.py" > Procfile

# Deploy
heroku create foodvision-ai
git push heroku main
```

#### AWS EC2
```bash
# Launch EC2 instance
# Install dependencies
sudo apt update
sudo apt install python3-pip nodejs npm

# Clone and setup
git clone your-repo-url
cd foodvision-ai
python setup.py

# Use PM2 for process management
npm install -g pm2
pm2 start backend/app_simple.py --interpreter python3
pm2 start "npm start" --name frontend
```

#### Google Cloud Platform
```bash
# Create app.yaml
runtime: python39
service: backend

# Deploy
gcloud app deploy
```

## 🔧 Environment Configuration

### Production Environment Variables
```env
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-production-key

# Database (upgrade to PostgreSQL for production)
DATABASE_URL=postgresql://user:password@host:port/database

# AI API Keys
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-anthropic-key
GEMINI_API_KEY=your-production-gemini-key

# Security
CORS_ORIGINS=https://your-frontend-domain.com

# Performance
CACHE_TYPE=redis
REDIS_URL=redis://your-redis-instance:6379/0
```

### Frontend Environment
```env
REACT_APP_API_URL=https://your-backend-domain.com
REACT_APP_ENVIRONMENT=production
```

## 📊 Database Migration

### SQLite to PostgreSQL
```python
# migration_script.py
import sqlite3
import psycopg2
import json

def migrate_to_postgresql():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('foodvision.db')
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(
        host="your-host",
        database="your-db",
        user="your-user",
        password="your-password"
    )
    
    # Migration logic here
    # ... (detailed migration code)
```

## 🔒 Security Checklist

### Production Security
- [ ] Change default secret keys
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable database encryption
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Regular security updates

### API Security
```python
# Add to Flask app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 📈 Performance Optimization

### Backend Optimization
```python
# Add caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/analytics')
@cache.cached(timeout=300)  # 5 minutes
def get_analytics():
    # Your analytics code
    pass
```

### Frontend Optimization
```javascript
// Code splitting
import { lazy, Suspense } from 'react';

const Analytics = lazy(() => import('./components/Analytics'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Analytics />
    </Suspense>
  );
}
```

## 📊 Monitoring Setup

### Application Monitoring
```python
# Add to Flask app
import logging
from flask.logging import default_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# Health check endpoint
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

### Database Monitoring
```sql
-- PostgreSQL monitoring queries
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;
```

## 🚀 CI/CD Pipeline

### GitHub Actions (Already included)
- Automated testing on push
- Security scanning
- Deployment to staging/production

### Manual Deployment Commands
```bash
# Build and deploy
npm run build
python -m pytest
docker build -t foodvision-ai .
docker push your-registry/foodvision-ai:latest
```

## 🌍 CDN Setup

### Static Assets
```javascript
// Configure CDN for static assets
const CDN_URL = 'https://your-cdn.com';

// In your React app
<img src={`${CDN_URL}/images/logo.png`} alt="Logo" />
```

## 📱 Mobile App Deployment

### PWA Configuration
```javascript
// public/manifest.json (already included)
{
  "name": "FoodVision AI",
  "short_name": "FoodVision",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#667eea",
  "background_color": "#ffffff"
}
```

## 🔄 Backup Strategy

### Database Backups
```bash
# PostgreSQL backup
pg_dump -h hostname -U username database_name > backup.sql

# Automated backups
crontab -e
0 2 * * * pg_dump -h hostname -U username database_name > /backups/$(date +\%Y\%m\%d).sql
```

## 📞 Support & Maintenance

### Monitoring Checklist
- [ ] Application uptime monitoring
- [ ] Database performance monitoring
- [ ] Error tracking and alerting
- [ ] Security vulnerability scanning
- [ ] Regular backups verification
- [ ] SSL certificate renewal
- [ ] Dependency updates

### Maintenance Schedule
- **Daily**: Check error logs and performance metrics
- **Weekly**: Review security alerts and update dependencies
- **Monthly**: Database optimization and backup verification
- **Quarterly**: Security audit and performance review

## 🎊 Go Live Checklist

### Pre-Launch
- [ ] All tests passing
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL certificates installed
- [ ] Domain configured
- [ ] CDN setup (if applicable)

### Launch
- [ ] Deploy to production
- [ ] Verify all endpoints working
- [ ] Test critical user flows
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Announce launch

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Address any issues
- [ ] Collect user feedback
- [ ] Plan next iteration

---

**🚀 Your FoodVision AI is ready for the world!**

*Choose the deployment option that best fits your needs and budget. All options will showcase your amazing AI-powered nutrition platform!*