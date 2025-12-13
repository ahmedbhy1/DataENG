import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'imdb_reddit')

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# ==== TMDB API Configuration (REAL Movie Data) ====
# Get your FREE API key from: https://www.themoviedb.org/settings/api
# This provides real trending movies, cast info, ratings, and more
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '2b8db8e7c0b6aa1dc37eca5ccf33a1f3')  # Public demo key
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# ==== Reddit API Configuration (REAL Comments Data) ====
# Optional - use empty if you don't have credentials
# Get Reddit credentials from: https://www.reddit.com/prefs/apps
# Step 1: Go to https://www.reddit.com/prefs/apps
# Step 2: Create "script" app
# Step 3: Copy Client ID and Client Secret
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = 'imdb_sentiment_project/1.0 (by your_reddit_username)'

# ETL Configuration
MOVIES_LIST = ['Inception', 'Interstellar', 'The Matrix', 'Oppenheimer', 'Dune']
REDDIT_SUBREDDIT = os.getenv('REDDIT_SUBREDDIT', 'movies')
REDDIT_LIMIT = int(os.getenv('REDDIT_LIMIT', '50'))

# ===== IMPORTANT NOTES =====
# 1. TMDB_API_KEY: Already includes a free public key, but you can get your own
# 2. REDDIT credentials: Optional but recommended for better comment extraction
# 3. Set these in your .env file for production deployments
# 4. DO NOT commit credentials to version control
