# Google OAuth Setup Guide

## Step 1: Set Up Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it

## Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Set application type to "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (for development)
   - `https://yourdomain.com/auth/google/callback` (for production)
5. Click "Create"
6. Copy the Client ID and Client Secret

## Step 3: Configure Environment Variables

1. Rename `config.env` to `.env`
2. Update the `.env` file with your actual values:

```env
# Flask Configuration
SECRET_KEY=your_generated_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 4: Generate a Secure Secret Key

Run this command to generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Test the Implementation

1. Start your Flask app:
```bash
python app.py
```

2. Navigate to `http://localhost:8000/login` or `http://localhost:8000/register`
3. Click the "Continue with Google" button
4. You should be redirected to Google's OAuth consent screen
5. After successful authentication, you'll be redirected to the dashboard

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error**:
   - Make sure the redirect URI in Google Cloud Console exactly matches `http://localhost:8000/auth/google/callback`
   - Check for extra spaces or typos

2. **"Client ID not found" error**:
   - Verify your `GOOGLE_CLIENT_ID` in the `.env` file
   - Make sure the `.env` file is in the same directory as `app.py`

3. **"Client secret not found" error**:
   - Verify your `GOOGLE_CLIENT_SECRET` in the `.env` file
   - Make sure there are no extra spaces around the `=` sign

4. **Import errors**:
   - Make sure you've installed all dependencies: `pip install -r requirements.txt`
   - Check that you're using Python 3.7+

### Security Notes:

- Never commit your `.env` file to version control
- Use different OAuth credentials for development and production
- Regularly rotate your secret keys
- Use HTTPS in production

## Production Deployment

When deploying to production:

1. Update the redirect URI in Google Cloud Console to your production domain
2. Set `FLASK_ENV=production` and `FLASK_DEBUG=False` in your `.env` file
3. Use a strong, unique `SECRET_KEY`
4. Enable HTTPS on your domain
5. Consider using environment variables instead of a `.env` file for better security
