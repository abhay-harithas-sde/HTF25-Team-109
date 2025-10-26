#!/usr/bin/env python3
"""
Test authentication system for FoodVision AI
"""

import requests
import json

# Test configuration
BASE_URL = 'http://localhost:5000/api/auth'
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'testpass123',
    'age': 25,
    'height': 170,
    'weight': 70,
    'gender': 'other',
    'activityLevel': 'moderate',
    'dailyCalorieGoal': 2000,
    'dietaryRestrictions': ['vegetarian'],
    'fitnessGoals': ['weight_maintenance']
}

def test_signup():
    """Test user signup"""
    print("🔐 Testing user signup...")
    
    try:
        response = requests.post(f'{BASE_URL}/signup', json=TEST_USER)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Signup successful!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Username: {data['user']['username']}")
            print(f"   Token: {data['token'][:20]}...")
            return data['token']
        else:
            print(f"❌ Signup failed: {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🔑 Testing user login...")
    
    try:
        login_data = {
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        }
        
        response = requests.post(f'{BASE_URL}/login', json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   Username: {data['user']['username']}")
            print(f"   Token: {data['token'][:20]}...")
            return data['token']
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_profile(token):
    """Test getting user profile"""
    print("\n👤 Testing profile retrieval...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/profile', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Profile retrieved successfully!")
            print(f"   Username: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Daily Calorie Goal: {data['user']['daily_calorie_goal']}")
            return True
        else:
            print(f"❌ Profile retrieval failed: {response.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_token_verification(token):
    """Test token verification"""
    print("\n🔍 Testing token verification...")
    
    try:
        response = requests.post(f'{BASE_URL}/verify-token', json={'token': token})
        
        if response.status_code == 200:
            data = response.json()
            if data['valid']:
                print("✅ Token is valid!")
                print(f"   User: {data['user']['username']}")
                return True
            else:
                print(f"❌ Token is invalid: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Token verification failed: {response.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("🧪 FoodVision AI Authentication System Test")
    print("=" * 50)
    
    # Test signup
    token = test_signup()
    if not token:
        # If signup fails, try login (user might already exist)
        token = test_login()
    
    if token:
        # Test profile retrieval
        test_profile(token)
        
        # Test token verification
        test_token_verification(token)
        
        print("\n🎉 All authentication tests completed!")
    else:
        print("\n❌ Authentication tests failed - no valid token obtained")

if __name__ == '__main__':
    main()