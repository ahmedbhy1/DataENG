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

# TMDB API Configuration (The Movie Database - Best Real Movie Data)
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '2b8db8e7c0b6aa1dc37eca5ccf33a1f3')  # Free public key

# Reddit API Configuration (Optional - use empty if you don't have credentials)
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = 'imdb_sentiment_project/1.0'

# ETL Configuration
MOVIES_LIST = ['Inception', 'Interstellar', 'The Matrix', 'Oppenheimer', 'Dune']
REDDIT_SUBREDDIT = os.getenv('REDDIT_SUBREDDIT', 'movies')
REDDIT_LIMIT = int(os.getenv('REDDIT_LIMIT', '50'))
