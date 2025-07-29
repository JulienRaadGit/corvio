# Firebase Setup Guide

## Problem
You're getting "Erreur de vérification du token" (Token verification error) when trying to login with Google. This happens because Firebase Admin SDK is not properly configured.

## Solution

### Step 1: Get Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `corvio-bf0b0`
3. Go to **Project Settings** (gear icon)
4. Click on **Service accounts** tab
5. Click **Generate new private key**
6. Download the JSON file

### Step 2: Set Environment Variables

You need to set these environment variables. You can do this in several ways:

#### Option A: Create a `.env` file (Recommended for development)

Create a file named `.env` in your project root:

```env
FIREBASE_PRIVATE_KEY_ID=your_private_key_id_from_json
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_service_account_email@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email%40project.iam.gserviceaccount.com
SECRET_KEY=your-secret-key-change-this
```

#### Option B: Set environment variables in your system

**Windows (PowerShell):**
```powershell
$env:FIREBASE_PRIVATE_KEY_ID="your_private_key_id"
$env:FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
$env:FIREBASE_CLIENT_EMAIL="your_service_account_email@project.iam.gserviceaccount.com"
$env:FIREBASE_CLIENT_ID="your_client_id"
$env:FIREBASE_CLIENT_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email%40project.iam.gserviceaccount.com"
```

**Windows (Command Prompt):**
```cmd
set FIREBASE_PRIVATE_KEY_ID=your_private_key_id
set FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
set FIREBASE_CLIENT_EMAIL=your_service_account_email@project.iam.gserviceaccount.com
set FIREBASE_CLIENT_ID=your_client_id
set FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email%40project.iam.gserviceaccount.com
```

### Step 3: Install python-dotenv (if using .env file)

```bash
pip install python-dotenv
```

Then add this to the top of your `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 4: Test the Setup

1. Run your Flask app
2. Check the console output - you should see:
   - ✅ Firebase Admin SDK initialized successfully
3. Try logging in with Google

### Troubleshooting

#### If you still get errors:

1. **Check the console output** when starting the app - it will tell you which credentials are missing
2. **Verify your Firebase project ID** matches `corvio-bf0b0`
3. **Make sure the private key** includes the `\n` characters for line breaks
4. **Check that your Firebase project** has Google Sign-In enabled in Authentication settings

#### Common Issues:

- **Private key format**: Make sure to include the `\n` characters for line breaks
- **Project ID mismatch**: Ensure your Firebase project ID is `corvio-bf0b0`
- **Missing quotes**: The private key should be wrapped in quotes
- **Service account permissions**: Make sure your service account has the necessary permissions

### Security Notes

- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore` file
- Use different service accounts for development and production
- Regularly rotate your service account keys

### Alternative: Quick Test

If you want to test without setting up all the environment variables, you can temporarily modify the `verify-token` endpoint to accept any token for testing:

```python
@app.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase ID token - TESTING VERSION"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No token provided'}), 400
        
        # TEMPORARY: Skip Firebase verification for testing
        # decoded_token = auth.verify_id_token(id_token)
        
        # Store user info in session (mock data)
        session['user'] = {
            'uid': 'test-user-123',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': ''
        }
        
        return jsonify({'success': True, 'user': session['user']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 401
```

**⚠️ WARNING**: This is only for testing. Remove this code before deploying to production! 