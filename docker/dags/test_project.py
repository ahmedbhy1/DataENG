#!/usr/bin/env python
"""
Complete Project Testing Guide
Test your trending movies recommendation system
"""

import subprocess
import sys

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    print_section("PROJECT TESTING SUITE")
    
    print("""
QUICK TESTING COMMANDS
======================

1. TEST EXTRACT MODULE (Get trending movies):
   python -c "from etl.extract import get_latest_films; movies = get_latest_films(3); print(f'Found {len(movies)} movies'); [print(f'  {m[\"title\"]} - Rating {m[\"rating\"]}') for m in movies]"

2. TEST REDDIT MODULE (Get comments):
   python -c "from etl.reddit_extract import get_film_comments; c = get_film_comments('Frankenstein', 5); print(f'Found {len(c)} comments')"

3. TEST SENTIMENT MODULE (Analyze comments):
   python -c "from etl.sentiment import rate_comments; test = [{'text': 'Amazing movie!'}]; print(f'Sentiment score: {rate_comments(test)}/100')"

4. TEST DATABASE CONNECTION:
   python -c "from sqlalchemy import create_engine; e = create_engine('postgresql://postgres:postgres@localhost:5432/imdb_reddit'); print('Database connected')"

5. RUN COMPLETE PIPELINE (Real data, ~5 min):
   python run_pipeline.py

6. VIEW RESULTS:
   python show_results.py

7. START WEB DASHBOARD:
   python web_app.py
   Visit: http://localhost:5000

8. CHECK DATABASE RECORDS:
   python -c "import pandas as pd; from sqlalchemy import create_engine; e = create_engine('postgresql://postgres:postgres@localhost:5432/imdb_reddit'); df = pd.read_sql('SELECT film_title, recommendation_score FROM recommendations ORDER BY recommendation_score DESC LIMIT 5', e); print(df)"


WHAT EACH TEST DOES
===================

TEST 1: Extract Module
- Fetches real trending movies from IMDb
- Tests web scraping functionality
- Returns movie titles, ratings, year

TEST 2: Reddit Module  
- Fetches real Reddit comments
- Tests Reddit API integration
- Returns actual user comments

TEST 3: Sentiment Module
- Analyzes comment sentiment
- Tests TextBlob NLP
- Returns sentiment score 0-100

TEST 4: Load Module
- Saves data to PostgreSQL
- Tests database connection
- Verifies data persistence

TEST 5: Complete Pipeline
- Runs all steps: extract -> comments -> sentiment -> save
- Analyzes 5 real trending 2025 movies
- Takes ~3-5 minutes
- Saves results to database

TEST 6: Database Check
- Verifies all data saved correctly
- Shows recommendation scores
- Confirms pipeline success

TEST 7: Web Dashboard
- Starts Flask server
- Displays recommendations visually
- Accessible at http://localhost:5000

TEST 8: Results Display
- Shows top recommendations
- Shows sentiment analysis results
- Displays scores and ratings


TESTING ORDER
=============

1. Start simple: Test individual modules
2. Test database connection
3. Run complete pipeline
4. View results
5. Check web dashboard


EXPECTED OUTPUT
===============

Trending Movies (2025):
- Zootopie 2 (7.7/10)
- Frankenstein (7.5/10)
- Train Dreams (7.5/10)
- Wicked: Partie II (7.0/10)
- Une bataille apres l'autre (8.0/10)

Sentiment Analysis:
- Real Reddit comments extracted
- Polarity scores calculated
- Recommendations scored 60% IMDb + 40% sentiment

Database:
- Films saved
- Recommendations saved
- Scores calculated
    """)

if __name__ == "__main__":
    main()

