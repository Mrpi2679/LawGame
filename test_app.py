# Quick Test Script
# Run this to verify the application works correctly

import requests
import sys

def test_app():
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test if app is running
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✓ Application is running and accessible")
            return True
        else:
            print(f"✗ Application returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Application is not running. Please start with: python app.py")
        return False
    except Exception as e:
        print(f"✗ Error accessing application: {e}")
        return False

if __name__ == "__main__":
    if test_app():
        print("\nTo test signup and login:")
        print("1. Open browser to: http://127.0.0.1:5000")
        print("2. Click 'Sign up' to create an account")
        print("3. Try logging in with your new credentials")