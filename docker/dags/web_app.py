from flask import Flask, render_template, jsonify, request
from etl.extract import get_latest_films
from etl.load import save_film, save_actor
from etl.calculate_actor_ratings import calculate_actor_ratings
import logging
from sqlalchemy import create_engine
from config import DATABASE_URL
import pandas as pd
import os

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Database connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.route('/')
def index():
    """Home page - list top rated actors"""
    try:
        df = pd.read_sql(
            "SELECT actor_name, total_films, average_rating, min_rating, max_rating FROM actor_ratings ORDER BY average_rating DESC LIMIT 20",
            engine
        )
        actors = df.to_dict('records')
        return render_template('actor_ratings.html', actors=actors)
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template('actor_ratings.html', actors=[])

@app.route('/api/actor-ratings')
def get_actor_ratings():
    """Get all actor ratings as JSON"""
    try:
        df = pd.read_sql(
            "SELECT actor_name, total_films, average_rating, min_rating, max_rating FROM actor_ratings ORDER BY average_rating DESC",
            engine
        )
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-actors')
def get_top_actors():
    """Get top 10 actors by average rating"""
    try:
        df = pd.read_sql(
            "SELECT actor_name, total_films, average_rating FROM actor_ratings ORDER BY average_rating DESC LIMIT 10",
            engine
        )
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/films')
def get_films():
    """Get all films as JSON"""
    try:
        df = pd.read_sql("SELECT * FROM films ORDER BY rating DESC", engine)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/actor/<actor_name>')
def get_actor_detail(actor_name):
    """Get detailed info about an actor"""
    try:
        actor_df = pd.read_sql(
            f"SELECT * FROM actor_ratings WHERE actor_name = '{actor_name}'",
            engine
        )
        return jsonify(actor_df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    """Run the pipeline: extract films, rate them, store actors, calculate actor ratings"""
    try:
        print("🚀 Starting Actor Rating Pipeline...")
        
        # Step 1: Extract films
        films = get_latest_films(limit=5)
        print(f"✓ Extracted {len(films)} films")
        
        # Step 2: Rate and store films
        for film in films:
            save_film({
                'imdb_id': film['imdb_id'],
                'title': film['title'],
                'rating': film['rating'],
                'year': film['year']
            })
            print(f"✓ Rated film: {film['title']} ({film['rating']}/10)")
        
        # Step 3: Store actors separately
        total_actors = 0
        for film in films:
            for actor in film['actors']:
                save_actor({'name': actor, 'films_count': 1})
                total_actors += 1
        print(f"✓ Stored {total_actors} actor records")
        
        # Step 4: Calculate average actor ratings
        calculate_actor_ratings()
        print("✓ Actor ratings calculated")
        
        return jsonify({
            'status': 'success',
            'message': f'Pipeline completed! Processed {len(films)} films and calculated ratings for all actors'
        })
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get pipeline statistics"""
    try:
        films_count = pd.read_sql("SELECT COUNT(*) as count FROM films", engine)['count'][0]
        actors_count = pd.read_sql("SELECT COUNT(*) as count FROM actors", engine)['count'][0]
        rated_actors = pd.read_sql("SELECT COUNT(*) as count FROM actor_ratings", engine)['count'][0]
        avg_rating = pd.read_sql("SELECT AVG(average_rating) as avg FROM actor_ratings", engine)['avg'][0]
        
        return jsonify({
            'total_films': int(films_count),
            'total_actors': int(actors_count),
            'rated_actors': int(rated_actors),
            'average_actor_rating': round(float(avg_rating), 2) if avg_rating else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=True, host='0.0.0.0', port=port)

