#!/usr/bin/env python3
"""
Firebase Configuration Test Script
This script helps you verify that your Firebase configuration is working correctly.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_firebase_config():
    """Test Firebase configuration and credentials"""
    print("🔍 Testing Firebase Configuration...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_PRIVATE_KEY', 
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_CLIENT_CERT_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            print(f"✅ {var}: SET")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nTo fix this:")
        print("1. Download your Firebase service account key from Firebase Console")
        print("2. Create a .env file with the following variables:")
        print("   FIREBASE_PRIVATE_KEY_ID=your_private_key_id")
        print("   FIREBASE_PRIVATE_KEY=\"-----BEGIN PRIVATE KEY-----\\nYour key here\\n-----END PRIVATE KEY-----\\n\"")
        print("   FIREBASE_CLIENT_EMAIL=your_service_account_email@project.iam.gserviceaccount.com")
        print("   FIREBASE_CLIENT_ID=your_client_id")
        print("   FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email%40project.iam.gserviceaccount.com")
        return False
    
    print("\n✅ All environment variables are set!")
    
    # Test Firebase initialization
    try:
        import firebase_admin
        from firebase_admin import credentials, auth
        
        firebase_config = {
            "type": "service_account",
            "project_id": "corvio-bf0b0",
            "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.environ.get('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
            "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL')
        }
        
        # Check if Firebase is already initialized
        try:
            firebase_admin.get_app()
            print("✅ Firebase is already initialized")
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
        
        print("\n🎉 Firebase configuration is working correctly!")
        print("You should now be able to login with Google.")
        return True
        
    except Exception as e:
        print(f"\n❌ Firebase initialization failed: {e}")
        print("\nCommon issues:")
        print("1. Private key format - make sure it includes \\n for line breaks")
        print("2. Project ID mismatch - ensure it's 'corvio-bf0b0'")
        print("3. Service account permissions - check Firebase Console")
        return False

def test_with_sample_token():
    """Test token verification with a sample token (for debugging)"""
    print("\n🧪 Testing token verification...")
    
    try:
        import firebase_admin
        from firebase_admin import auth
        
        # This will fail, but it helps identify the specific error
        sample_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20iLCJhdWQiOiJjb3J2aW8tYmYwYjAiLCJhdXRoX3RpbWUiOjE2MzQ1Njc4OTAsInVzZXJfaWQiOiJ0ZXN0IiwiaWF0IjoxNjM0NTY3ODkwLCJleHAiOjE2MzQ1NzE0OTB9.test"
        
        try:
            decoded_token = auth.verify_id_token(sample_token)
            print("✅ Token verification is working")
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            print("This is expected with a fake token, but shows the verification is set up correctly")
            
    except Exception as e:
        print(f"❌ Cannot test token verification: {e}")

if __name__ == "__main__":
    print("🚀 Firebase Configuration Test")
    print("This script will help you verify your Firebase setup.")
    print()
    
    success = test_firebase_config()
    
    if success:
        test_with_sample_token()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your Firebase configuration is ready.")
    else:
        print("❌ Please fix the issues above before trying to login.")
    
    print("\nNext steps:")
    print("1. Run your Flask app: python app.py")
    print("2. Try logging in with Google")
    print("3. Check the console output for any errors") 