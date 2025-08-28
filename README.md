# AltTabWell Website

A wellness website that allows users to upload food images and get nutritional information using the FatSecret API. The dashboard includes calorie intake tracking, step counting, and team collaboration features.

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
FATSECRET_CLIENT_ID=your_fatsecret_client_id
FATSECRET_CLIENT_SECRET=your_fatsecret_client_secret
HOST=0.0.0.0
PORT=5001
```

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