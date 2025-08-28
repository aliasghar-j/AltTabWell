from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
import json
import time
import base64
import hashlib
import os
from urllib.parse import quote
from oauthlib.oauth1 import Client as OAuthClient
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# FatSecret API Configuration
FATSECRET_API_URL = 'https://platform.fatsecret.com/rest/server.api'
FATSECRET_CLIENT_ID = os.environ.get('FATSECRET_CLIENT_ID', '0bc6f5fdb62a4e3b8800f1389560e2e2')  # User has the API ID
FATSECRET_CLIENT_SECRET = os.environ.get('FATSECRET_CLIENT_SECRET', 'f32fc9432d3547e3936dd733b3370294')  # User has the API secret

# FatSecret OAuth Helper Functions
def get_oauth_params(method, url, params):
    oauth_client = OAuthClient(FATSECRET_CLIENT_ID, FATSECRET_CLIENT_SECRET)
    uri, headers, body = oauth_client.sign(url, method, None, {'Content-Type': 'application/json'}, params)
    return uri, headers

@app.route('/')
def index():
    wellness_quotes = [
        {"text": "Take care of your body. It’s the only place you have to live.", "author": "Jim Rohn"},
        {"text": "A calm mind brings inner strength and self-confidence.", "author": "Dalai Lama"},
        {"text": "The greatest wealth is health.", "author": "Virgil"},
        {"text": "Health is not about the weight you lose, but the life you gain.", "author": "Unknown"},
        {"text": "Fall in love with taking care of yourself.", "author": "Unknown"},
        {"text": "Small steps every day lead to big changes.", "author": "Unknown"},
        {"text": "Self-care is how you take your power back.", "author": "Lalah Delia"},
        {"text": "Wellness is a connection of paths: knowledge and action.", "author": "Joshua Holtz"}
    ]
    quote = random.choice(wellness_quotes)
    return render_template('index.html', quote=quote)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic would go here
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Registration logic would go here
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    # Get nutrition data from session if available
    nutrition_data = session.get('nutrition_data', None)
    return render_template('dashboard.html', nutrition_data=nutrition_data)

@app.route('/leaderboard')
def leaderboard():
    # Leaderboard data would be fetched here
    return render_template('leaderboard.html')

@app.route('/therapy')
def therapy():
    # Therapy page logic would go here
    return render_template('therapy.html')

@app.route('/search-food', methods=['POST'])
def search_food():
    food_query = request.form.get('food_query')
    if not food_query:
        return redirect(url_for('dashboard'))
    
    # Prepare parameters for FatSecret API
    params = {
        'method': 'foods.search',
        'search_expression': food_query,
        'format': 'json',
        'max_results': 5
    }
    
    try:
        # Get OAuth parameters
        uri, headers = get_oauth_params('POST', FATSECRET_API_URL, params)
        
        # Make the API request
        response = requests.post(uri, headers=headers, data=params)
        data = response.json()
        
        # Process the response
        if 'foods' in data and 'food' in data['foods']:
            # Store the nutrition data in session
            session['nutrition_data'] = data['foods']['food']
        else:
            session['nutrition_data'] = None
            
    except Exception as e:
        print(f"Error searching for food: {e}")
        session['nutrition_data'] = None
    
    return redirect(url_for('dashboard'))

@app.route('/upload-food', methods=['POST'])
def upload_food():
    # This would handle food image uploads and analysis
    # For now, just redirect to food search
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', '5001')), debug=True, use_reloader=False)