"""
Calculate average actor ratings based on all films they acted in.
This script aggregates film ratings by actor using SQL joins through the M2M junction table.
"""

import psycopg2
from psycopg2 import sql
import logging
import os

logger = logging.getLogger(__name__)

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'imdb_reddit')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def calculate_actor_ratings():
    """
    Calculate and store average ratings for each actor based on their filmography.
    
    Algorithm:
    1. Join actors -> actor_film junction -> films
    2. GROUP BY actor and calculate AVG, MIN, MAX of film ratings
    3. UPSERT results into actor_ratings table
    4. Display top 10 actors
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("📊 Starting actor ratings calculation...")
        
        # Main calculation query with M2M joins
        logger.info("🔍 Calculating average ratings for each actor...")
        cursor.execute('''
            WITH actor_statistics AS (
                SELECT 
                    a.actor_id,
                    a.name as actor_name,
                    COUNT(DISTINCT f.film_id) as total_films,
                    ROUND(AVG(f.rating)::numeric, 2) as average_rating,
                    MIN(f.rating) as min_rating,
                    MAX(f.rating) as max_rating
                FROM actors a
                INNER JOIN actor_film af ON a.actor_id = af.actor_id
                INNER JOIN films f ON af.film_id = f.film_id
                GROUP BY a.actor_id, a.name
                HAVING COUNT(DISTINCT f.film_id) > 0
                ORDER BY average_rating DESC
            )
            INSERT INTO actor_ratings (actor_id, actor_name, total_films, average_rating, min_rating, max_rating)
            SELECT actor_id, actor_name, total_films, average_rating, min_rating, max_rating
            FROM actor_statistics
            ON CONFLICT (actor_id) DO UPDATE
            SET actor_name = EXCLUDED.actor_name,
                total_films = EXCLUDED.total_films,
                average_rating = EXCLUDED.average_rating,
                min_rating = EXCLUDED.min_rating,
                max_rating = EXCLUDED.max_rating,
                last_updated = CURRENT_TIMESTAMP
        ''')
        
        conn.commit()
        logger.info("✓ Actor ratings calculated and stored")
        
        # Display top 10 actors
        logger.info("\n🏆 TOP 10 ACTORS BY AVERAGE RATING:\n")
        cursor.execute('''
            SELECT 
                actor_name,
                total_films,
                average_rating,
                min_rating,
                max_rating
            FROM actor_ratings
            WHERE average_rating IS NOT NULL
            ORDER BY average_rating DESC
            LIMIT 10
        ''')
        
        results = cursor.fetchall()
        if results:
            for rank, (name, films, avg, min_r, max_r) in enumerate(results, 1):
                logger.info(f"{rank}. {name:<30} | Films: {films} | Avg: {avg}/10 | Range: {min_r}-{max_r}")
        else:
            logger.warning("No actor ratings found. Make sure films and actors are linked.")
        
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error calculating actor ratings: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    calculate_actor_ratings()
