# AltTabWell Website

A wellness website that allows users to upload food images and get nutritional information using the Gemini API. The dashboard includes calorie intake tracking, step counting, and team collaboration features.

## Features (Planned)

- Food image upload and analysis
- Calorie and nutritional value tracking
- Dashboard with Looker schematics
- Daily calorie intake visualization
- Step counter
- Team collaboration with department-based step counting

## Getting Started

### Prerequisites

- Python 3.8+
- Flask

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
## Deployment

### Environment Variables
Create a `.env` file in the project root with:
```
SECRET_KEY=change_this_to_a_random_long_secret
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
HOST=0.0.0.0
PORT=5001
```

#### Gemini API Setup
1. Go to https://ai.google.dev/
2. Sign up for a Google AI Studio account
3. Create a new API key for Gemini
4. Add this API key to your `.env` file as `GEMINI_API_KEY`

### GitHub
1. Initialize git and commit:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. Create a new GitHub repository (or use GitHub CLI):
   ```
   gh repo create AltTabWell --source . --public --push
   ```
   If you don't have `gh`, create a repo on GitHub, then:
   ```
   git remote add origin https://github.com/<your-username>/AltTabWell.git
   git branch -M main
   git push -u origin main
   ```
4. Open your browser and navigate to `http://localhost:5000`

## Current Status

Basic Flask Hello World application is set up. Further development will include implementing the planned features.