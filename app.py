from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests
import os
from dotenv import load_dotenv
import random
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from models import db, User, WellnessRecord, StepRecord, NutritionRecord, Department, DepartmentNutrition
from datetime import datetime
import json

# --- EXPLICITLY LOAD .env FILE ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
# ------------------------------------

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///altabwell.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = 'http://localhost:8000/auth/google/callback'

# --- NEW: Gemini API Configuration ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# ------------------------------------

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    wellness_quotes = [
        {"text": "Take care of your body. It’s the only place you have to live.", "author": "Jim Rohn"},
        {"text": "A calm mind brings inner strength and self-confidence.", "author": "Dalai Lama"},
        {"text": "The greatest wealth is health.", "author": "Virgil"},
    ]
    quote = random.choice(wellness_quotes)
    return render_template('index.html', quote=quote)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        return redirect(url_for('google_auth'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        return redirect(url_for('google_auth'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/auth/google')
def google_auth():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/auth/google/callback')
def google_auth_callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, google_requests.Request(), GOOGLE_CLIENT_ID
    )
    
    user = User.query.filter_by(google_id=id_info['sub']).first()
    
    if not user:
        user = User(
            email=id_info['email'],
            name=id_info.get('name', ''),
            google_id=id_info['sub'],
            profile_picture=id_info.get('picture', ''),
            last_login=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Welcome to AltTabWell! Please select your department.', 'success')
        return redirect(url_for('select_department'))
    else:
        user.last_login = datetime.utcnow()
        db.session.commit()
        flash('Welcome back!', 'success')
        login_user(user)
        return redirect(url_for('dashboard'))

@app.route('/select-department', methods=['GET', 'POST'])
@login_required
def select_department():
    if request.method == 'POST':
        department_id = request.form.get('department')
        if department_id:
            current_user.department_id = department_id
            db.session.commit()
            flash('Department saved successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please select a department.', 'danger')
    
    departments = Department.query.all()
    return render_template('select_department.html', departments=departments)

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.department_id:
        flash('Please select your department to continue.', 'info')
        return redirect(url_for('select_department'))

    nutrition_data = session.get('nutrition_data', None)
    today = datetime.utcnow().date()
    wellness_record = WellnessRecord.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    step_record = StepRecord.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    # Get today's nutrition records for calorie total
    nutrition_records = NutritionRecord.query.filter_by(
        user_id=current_user.id,
        date=today
    ).all()
    
    total_calories = sum(record.calories or 0 for record in nutrition_records)
    
    # Get monthly calorie total
    first_day_of_month = today.replace(day=1)
    monthly_nutrition_records = NutritionRecord.query.filter(
        NutritionRecord.user_id == current_user.id,
        NutritionRecord.date >= first_day_of_month
    ).all()
    total_monthly_calories = sum(record.calories or 0 for record in monthly_nutrition_records)
    
    return render_template('dashboard.html', 
                         nutrition_data=nutrition_data,
                         wellness_record=wellness_record,
                         step_record=step_record,
                         nutrition_records=nutrition_records,
                         total_calories=total_calories,
                         total_monthly_calories=total_monthly_calories)

@app.route('/leaderboard')
def leaderboard():
    from sqlalchemy import func
    from datetime import timedelta
    
    week_ago = datetime.utcnow().date() - timedelta(days=7)
    
    top_users = db.session.query(
        User.name,
        func.sum(StepRecord.steps).label('total_steps')
    ).join(StepRecord).filter(
        StepRecord.date >= week_ago
    ).group_by(User.id).order_by(
        func.sum(StepRecord.steps).desc()
    ).limit(10).all()
    
    return render_template('leaderboard.html', top_users=top_users)

@app.route('/therapy')
@login_required
def therapy():
    from datetime import timedelta
    
    week_ago = datetime.utcnow().date() - timedelta(days=7)
    wellness_records = WellnessRecord.query.filter_by(
        user_id=current_user.id
    ).filter(
        WellnessRecord.date >= week_ago
    ).order_by(WellnessRecord.date.desc()).all()
    
    return render_template('therapy.html', wellness_records=wellness_records)

# --- NEW: Gemini API route for food search ---
@app.route('/api/gemini/search', methods=['GET'])
def gemini_search():
    food_name = request.args.get('foodName')
    
    if not food_name:
        return jsonify({"success": False, "error": "foodName parameter is required"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "error": "Gemini API key not configured. Check .env file."}), 500

    # The prompt is crafted to ask for a concise, single-line response with just the calorie number.
    prompt = f"Provide ONLY the calorie number (just the number) for {food_name}. Example: For '1 medium apple' just respond with '95'"
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        
        # Extract the text from the Gemini response
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        
        # Try to extract just the number
        import re
        calorie_match = re.search(r'\d+', text_response)
        calories = int(calorie_match.group()) if calorie_match else 0
        
        return jsonify({
            "success": True, 
            "description": f"{food_name}: {calories} calories",
            "calories": calories,
            "food_name": food_name
        })

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        return jsonify({"success": False, "error": "API returned an error. Check server logs."}), 502
    except (KeyError, IndexError) as e:
        print(f"Error parsing Gemini response: {e}")
        return jsonify({"success": False, "error": "Could not parse API response."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500

@app.route('/upload-food', methods=['POST'])
@login_required
def upload_food():
    if 'food_image' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['food_image']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))
    
    if file:
        image_bytes = file.read()
        import base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        if not GEMINI_API_KEY:
            flash('Gemini API key not configured.', 'danger')
            return redirect(url_for('dashboard'))
        
        prompt = "Analyze this food image and provide ONLY the estimated calorie count as a number. For example, if it's a burger, just respond with '650'."
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": file.content_type,
                            "data": image_base64
                        }
                    }
                ]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            text_response = data['candidates'][0]['content']['parts'][0]['text']
            import re
            calorie_match = re.search(r'\d+', text_response)
            calories = int(calorie_match.group()) if calorie_match else 0
            
            food_name = os.path.splitext(file.filename)[0] or "Food from image"
            today = datetime.utcnow().date()
            
            # Add to user's nutrition record
            nutrition_record = NutritionRecord(
                user_id=current_user.id,
                date=today,
                food_name=food_name,
                calories=calories,
                meal_type='snack'
            )
            db.session.add(nutrition_record)
            
            # Add to department's nutrition record
            department_nutrition = DepartmentNutrition.query.filter_by(
                department_id=current_user.department_id,
                date=today
            ).first()
            
            if not department_nutrition:
                department_nutrition = DepartmentNutrition(
                    department_id=current_user.department_id,
                    date=today,
                    total_calories=calories
                )
                db.session.add(department_nutrition)
            else:
                department_nutrition.total_calories += calories
            
            db.session.commit()
            
            flash(f'Added {food_name} ({calories} calories) to your daily intake', 'success')
            
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            flash('API returned an error. Check server logs.', 'danger')
        except (KeyError, IndexError) as e:
            print(f"Error parsing Gemini response: {e}")
            flash('Could not parse API response.', 'danger')
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An internal server error occurred.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/add-food', methods=['POST'])
@login_required
def add_food():
    food_name = request.form.get('food_name')
    calories = request.form.get('calories', type=float, default=0)
    
    if not food_name or calories <= 0:
        flash('Invalid food data provided', 'danger')
        return redirect(url_for('dashboard'))
    
    today = datetime.utcnow().date()
    
    # Add to user's nutrition record
    nutrition_record = NutritionRecord(
        user_id=current_user.id,
        date=today,
        food_name=food_name,
        calories=calories,
        meal_type='snack'
    )
    db.session.add(nutrition_record)
    
    # Add to department's nutrition record
    department_nutrition = DepartmentNutrition.query.filter_by(
        department_id=current_user.department_id,
        date=today
    ).first()
    
    if not department_nutrition:
        department_nutrition = DepartmentNutrition(
            department_id=current_user.department_id,
            date=today,
            total_calories=calories
        )
        db.session.add(department_nutrition)
    else:
        department_nutrition.total_calories += calories
        
    db.session.commit()
    
    flash(f'Added {food_name} ({calories} calories) to your daily intake', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add-wellness', methods=['POST'])
@login_required
def add_wellness():
    today = datetime.utcnow().date()
    
    wellness_record = WellnessRecord.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    if not wellness_record:
        wellness_record = WellnessRecord(
            user_id=current_user.id,
            date=today
        )
        db.session.add(wellness_record)
    
    wellness_record.mood_score = request.form.get('mood_score', type=int)
    wellness_record.sleep_hours = request.form.get('sleep_hours', type=float)
    wellness_record.water_intake = request.form.get('water_intake', type=float)
    wellness_record.stress_level = request.form.get('stress_level', type=int)
    wellness_record.notes = request.form.get('notes')
    
    db.session.commit()
    flash('Wellness data updated successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add-steps', methods=['POST'])
@login_required
def add_steps():
    today = datetime.utcnow().date()
    steps = request.form.get('steps', type=int, default=0)
    
    step_record = StepRecord.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    if not step_record:
        step_record = StepRecord(
            user_id=current_user.id,
            date=today,
            steps=steps
        )
        db.session.add(step_record)
    else:
        step_record.steps = steps
    
    db.session.commit()
    flash(f'Steps updated: {steps:,} steps!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

