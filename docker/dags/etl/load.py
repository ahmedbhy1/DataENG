"""
ETL Load module - handles database operations
Uses psycopg2 for direct database operations with UPSERT support
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


def save_film(film_data):
    """
    Save or update a film in the database.
    Uses UPSERT to handle duplicates based on imdb_id.
    
    Args:
        film_data: dict with keys {imdb_id, title, rating, year}
    
    Returns:
        film_id: The database ID of the saved film
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # UPSERT: Insert or update if imdb_id already exists
        cursor.execute('''
            INSERT INTO films (imdb_id, title, rating, year)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (imdb_id) DO UPDATE
            SET title = EXCLUDED.title,
                rating = EXCLUDED.rating,
                year = EXCLUDED.year
            RETURNING film_id
        ''', (film_data['imdb_id'], film_data['title'], film_data['rating'], film_data['year']))
        
        film_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"✓ Saved film: {film_data['title']} (ID: {film_id})")
        return film_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error saving film: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def save_actor(actor_name):
    """
    Save or retrieve an actor in the database.
    Uses UPSERT to handle duplicates based on name.
    
    Args:
        actor_name: str - The actor's name
    
    Returns:
        actor_id: The database ID of the actor
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # UPSERT: Insert or return existing actor
        cursor.execute('''
            INSERT INTO actors (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE
            SET name = EXCLUDED.name
            RETURNING actor_id
        ''', (actor_name,))
        
        actor_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"✓ Saved/Retrieved actor: {actor_name} (ID: {actor_id})")
        return actor_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error saving actor: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def link_actor_to_film(actor_id, film_id):
    """
    Create a many-to-many relationship between an actor and a film.
    
    Args:
        actor_id: int - The actor's database ID
        film_id: int - The film's database ID
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert into junction table or ignore if already exists
        cursor.execute('''
            INSERT INTO actor_film (actor_id, film_id)
            VALUES (%s, %s)
            ON CONFLICT (actor_id, film_id) DO NOTHING
        ''', (actor_id, film_id))
        
        conn.commit()
        logger.info(f"✓ Linked actor {actor_id} to film {film_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error linking actor to film: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def save_film_with_actors(film_data, actor_names):
    """
    Complete workflow: Save film, save/retrieve actors, and link them together.
    
    Args:
        film_data: dict with keys {imdb_id, title, rating, year}
        actor_names: list of actor names
    
    Returns:
        dict with film_id and actor_ids
    """
    try:
        # Step 1: Save the film
        film_id = save_film(film_data)
        
        # Step 2: Save each actor and create M2M link
        actor_ids = []
        for actor_name in actor_names:
            actor_id = save_actor(actor_name)
            actor_ids.append(actor_id)
            
            # Step 3: Link actor to film
            link_actor_to_film(actor_id, film_id)
        
        logger.info(f"✓ Completed: Film {film_data['title']} linked with {len(actor_ids)} actors")
        return {'film_id': film_id, 'actor_ids': actor_ids}
        
    except Exception as e:
        logger.error(f"❌ Error in save_film_with_actors: {e}")
        raise


# Removed: save_reddit_comments and save_recommendation functions (tables no longer used)
