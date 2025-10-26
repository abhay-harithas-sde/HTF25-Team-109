# 🔐 FoodVision AI Authentication System

A comprehensive authentication system with login, signup, and user management features integrated with the FoodVision AI database.

## 🚀 Features

### Frontend Authentication
- **Modern React Components**: Beautiful, responsive login and signup forms
- **Form Validation**: Real-time validation with user-friendly error messages
- **Password Security**: Secure password handling with visibility toggles
- **User Profiles**: Comprehensive user profile management
- **Responsive Design**: Mobile-first design with dark mode support
- **Animation**: Smooth transitions and micro-interactions using Framer Motion

### Backend Authentication
- **JWT Tokens**: Secure JSON Web Token authentication
- **Password Hashing**: SHA-256 password hashing for security
- **Database Integration**: Full SQLite database integration
- **RESTful API**: Clean REST API endpoints
- **Input Validation**: Comprehensive server-side validation
- **Error Handling**: Robust error handling and logging

### User Management
- **User Registration**: Complete signup with optional profile information
- **User Login**: Secure login with email and password
- **Profile Management**: Update user preferences and personal information
- **Password Changes**: Secure password change functionality
- **Token Verification**: JWT token validation and refresh

## 📁 File Structure

```
HTF25-Team-109/
├── frontend/src/components/
│   ├── Auth.js                 # Main authentication component
│   └── Auth.css               # Authentication styles
├── frontend/src/
│   ├── AppWithAuth.js         # App wrapper with authentication
│   ├── AppWithAuth.css        # Authentication wrapper styles
│   └── index.js               # Updated entry point
├── backend/
│   ├── auth.py                # Authentication routes and logic
│   └── app.py                 # Updated Flask app with auth
├── init_auth_db.py            # Database initialization script
├── test_auth.py               # Authentication testing script
└── AUTH_SETUP.md              # This documentation
```

## 🛠️ Setup Instructions

### 1. Database Setup

Initialize the authentication database:

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Initialize authentication database
python init_auth_db.py
```

### 2. Backend Setup

The authentication routes are automatically integrated into the Flask app. Make sure you have the required dependencies:

```bash
pip install flask flask-cors pyjwt
```

### 3. Frontend Setup

The authentication components are integrated into the React app. Make sure you have the required dependencies:

```bash
cd frontend
npm install framer-motion lucide-react
```

### 4. Environment Configuration

Set up your Flask app secret key in `backend/app.py`:

```python
app.config['SECRET_KEY'] = 'your-secure-secret-key-here'
```

## 🔌 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | User registration |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/profile` | Get user profile |
| PUT | `/api/auth/profile` | Update user profile |
| POST | `/api/auth/change-password` | Change password |
| POST | `/api/auth/verify-token` | Verify JWT token |

### Request/Response Examples

#### Signup Request
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "age": 25,
  "height": 175,
  "weight": 70,
  "gender": "male",
  "activityLevel": "moderate",
  "dailyCalorieGoal": 2200,
  "dietaryRestrictions": ["vegetarian"],
  "fitnessGoals": ["weight_loss"]
}
```

#### Login Request
```json
{
  "email": "john@example.com",
  "password": "securepass123"
}
```

#### Success Response
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "daily_calorie_goal": 2200,
    "height": 175,
    "weight": 70,
    "age": 25,
    "gender": "male",
    "activity_level": "moderate"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🧪 Testing

### Automated Testing

Run the authentication test script:

```bash
# Make sure the Flask server is running first
python backend/app.py

# In another terminal, run the tests
python test_auth.py
```

### Manual Testing

1. **Start the Backend Server**:
   ```bash
   cd backend
   python app.py
   ```

2. **Start the Frontend Development Server**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test the Authentication Flow**:
   - Visit `http://localhost:3000`
   - Click "Get Started" or "Sign In"
   - Test signup with new user credentials
   - Test login with existing credentials
   - Verify user menu and logout functionality

## 🔒 Security Features

### Password Security
- **Hashing**: Passwords are hashed using SHA-256
- **Validation**: Minimum 6 characters required
- **No Storage**: Plain text passwords are never stored

### JWT Security
- **Expiration**: Tokens expire after 7 days
- **Verification**: All protected routes verify tokens
- **Secure Storage**: Tokens stored in localStorage with proper cleanup

### Input Validation
- **Email Format**: Valid email format required
- **Username Rules**: 3-50 characters, alphanumeric and underscores only
- **Data Sanitization**: All inputs are validated and sanitized

### Database Security
- **Prepared Statements**: All queries use parameterized statements
- **Foreign Keys**: Proper foreign key constraints
- **Indexes**: Optimized database indexes for performance

## 🎨 UI/UX Features

### Design Elements
- **Modern Interface**: Clean, professional design
- **Responsive Layout**: Works on all device sizes
- **Dark Mode Support**: Automatic dark mode detection
- **Accessibility**: WCAG compliant with proper ARIA labels
- **Loading States**: Smooth loading indicators and feedback

### User Experience
- **Real-time Validation**: Instant feedback on form inputs
- **Error Handling**: Clear, actionable error messages
- **Success Feedback**: Confirmation messages for successful actions
- **Smooth Animations**: Framer Motion powered transitions
- **Keyboard Navigation**: Full keyboard accessibility

## 🔧 Configuration Options

### User Preferences
- **Theme**: Light/Dark mode preference
- **Units**: Metric/Imperial unit system
- **Notifications**: Email and push notification settings
- **Privacy**: Privacy and data sharing preferences

### Dietary Information
- **Restrictions**: Vegetarian, vegan, gluten-free, etc.
- **Allergies**: Food allergy tracking
- **Goals**: Weight loss, muscle gain, maintenance
- **Activity Level**: Sedentary to very active

## 🚨 Error Handling

### Common Errors
- **Invalid Credentials**: Clear messaging for login failures
- **Duplicate Users**: Helpful messages for existing accounts
- **Network Errors**: Graceful handling of connection issues
- **Validation Errors**: Specific field-level error messages

### Error Codes
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid credentials/token)
- `409`: Conflict (duplicate username/email)
- `500`: Internal Server Error

## 📱 Mobile Support

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Touch-Friendly**: Large touch targets and gestures
- **Keyboard Support**: Proper mobile keyboard handling
- **Performance**: Optimized for mobile networks

## 🔄 Integration with Main App

### Context Integration
- **User State**: Global user state management
- **Authentication State**: Persistent login state
- **Profile Data**: Seamless profile data integration
- **API Integration**: Automatic token inclusion in API calls

### Navigation
- **Protected Routes**: Automatic redirection for unauthenticated users
- **User Menu**: Integrated user menu in main navigation
- **Logout Flow**: Clean logout with state cleanup

## 🎯 Future Enhancements

### Planned Features
- **Social Login**: Google, Facebook, Apple sign-in
- **Two-Factor Authentication**: SMS and app-based 2FA
- **Password Recovery**: Email-based password reset
- **Account Verification**: Email verification for new accounts
- **OAuth Integration**: Third-party app integrations

### Security Improvements
- **Rate Limiting**: API rate limiting for security
- **Session Management**: Advanced session handling
- **Audit Logging**: User action logging and monitoring
- **GDPR Compliance**: Data privacy and deletion features

## 📞 Support

For issues or questions about the authentication system:

1. **Check the logs**: Look at browser console and server logs
2. **Verify database**: Ensure the database is properly initialized
3. **Test API endpoints**: Use the test script to verify backend functionality
4. **Check network**: Ensure frontend can communicate with backend

## 🏆 Best Practices

### Development
- **Environment Variables**: Use environment variables for secrets
- **Error Logging**: Comprehensive error logging and monitoring
- **Code Review**: Regular security code reviews
- **Testing**: Automated testing for all authentication flows

### Deployment
- **HTTPS**: Always use HTTPS in production
- **Secret Management**: Secure secret key management
- **Database Security**: Proper database access controls
- **Monitoring**: Authentication event monitoring and alerting

---

**Built with ❤️ for FoodVision AI - Making nutrition tracking secure and user-friendly!**