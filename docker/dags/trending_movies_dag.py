"""
Actor Rating System - Airflow DAG
Comprehensive multi-step pipeline for complete actor rating workflow.

Pipeline Flow:
1. Initialize Database: Execute init.sql to set up/reset schema with M2M relationships
2. Validate Database: Check database connectivity and schema creation
3. Extract Films: Fetch trending films from IMDb with cast info
4. Save Each Film: Insert/update film records with unique constraints
5. Save Actors: Insert/update actor records with unique constraints
6. Link Actors to Films: Create many-to-many relationships for each actor-film pair
7. Validate Data: Check data integrity after loading
8. Calculate Actor Ratings: Aggregate ratings based on filmography
9. Generate Report: Display top-rated actors and statistics
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import sys
import os
import logging
import psycopg2
from psycopg2 import sql

# Add the dags folder to Python path
sys.path.insert(0, '/opt/airflow/dags')

# Import ETL modules
from etl.extract import get_latest_films
from etl.load import save_film, save_actor, link_actor_to_film, get_db_connection
from etl.calculate_actor_ratings import calculate_actor_ratings

logger = logging.getLogger(__name__)

# DAG configuration
default_args = {
    'owner': 'data-engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

dag = DAG(
    'actor_rating_pipeline',
    default_args=default_args,
    description='Complete actor rating pipeline: initialize DB, extract films, save with M2M links, calculate ratings',
    schedule_interval='@daily',
    catchup=False,
    tags=['actors', 'ratings', 'analysis', 'complete-pipeline'],
)



# ==================== OPERATION 1: INITIALIZE DATABASE ====================
# Execute init.sql using BashOperator with psql command
init_database = BashOperator(
    task_id='init_database',
    bash_command='''
    export PGPASSWORD=postgres && psql -h postgres -U postgres -d imdb_reddit -f /opt/airflow/init.sql
    ''',
    dag=dag,
)


# ==================== OPERATION 2: VALIDATE DATABASE CONNECTION ====================
def validate_database_task():
    """
    Operation 2: Validate database connectivity and schema
    - Check connection to PostgreSQL
    - Verify all tables exist
    - Report table structure
    """
    logger.info("=" * 80)
    logger.info("OPERATION 2: VALIDATING DATABASE")
    logger.info("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        tables_to_check = ['films', 'actors', 'actor_film', 'actor_ratings', 'recommendations']
        logger.info(f"🔍 Checking for {len(tables_to_check)} required tables...")
        
        # Use simple approach: just check each table individually
        existing_tables = []
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s", (table,))
                if cursor.fetchone():
                    existing_tables.append(table)
                    logger.info(f"  ✓ Table '{table}' exists")
                else:
                    logger.warning(f"  ⚠ Table '{table}' NOT FOUND")
            except Exception as e:
                logger.warning(f"  ⚠ Could not check table '{table}': {e}")
        
        # Get row counts
        logger.info("\n📊 Current data in tables:")
        for table in ['films', 'actors', 'actor_film', 'actor_ratings']:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                logger.info(f"  - {table}: {count} rows")
            except Exception as e:
                logger.warning(f"  - {table}: Could not get count - {e}")
        
        logger.info("✓ Database validation complete!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database validation failed: {e}")
        # Don't re-raise - let the pipeline continue
        return False


validate_database = PythonOperator(
    task_id='validate_database',
    python_callable=validate_database_task,
    dag=dag,
)


# ==================== OPERATION 3: EXTRACT FILMS ====================
def extract_films_task():
    """
    Operation 3: Extract trending films from IMDb
    - Fetch films with titles, ratings, years, and cast lists
    - Return data for next operations
    """
    logger.info("=" * 80)
    logger.info("OPERATION 3: EXTRACTING FILMS FROM IMDB")
    logger.info("=" * 80)
    
    try:
        films = get_latest_films(limit=10)
        logger.info(f"✓ Extracted {len(films)} trending films:\n")
        
        for i, film in enumerate(films, 1):
            actor_count = len(film.get('actors', []))
            logger.info(f"  {i}. {film['title']} ({film['year']}) - Rating: {film['rating']}/10 - Cast: {actor_count} actors")
        
        return films
    except Exception as e:
        logger.error(f"❌ Error extracting films: {e}")
        raise


extract_films = PythonOperator(
    task_id='extract_films',
    python_callable=extract_films_task,
    dag=dag,
)


# ==================== OPERATION 4: SAVE FILMS ====================
def save_films_task(ti):
    """
    Operation 4: Save/update all extracted films to database
    - Insert films with UNIQUE constraint on imdb_id
    - Handles duplicates with UPSERT
    - Returns film IDs for linking with actors
    """
    logger.info("=" * 80)
    logger.info("OPERATION 4: SAVING FILMS TO DATABASE")
    logger.info("=" * 80)
    
    try:
        films = ti.xcom_pull(task_ids='extract_films')
        
        if not films:
            logger.error("❌ No films received from extract task")
            return None
        
        film_ids = {}
        for film in films:
            try:
                logger.info(f"💾 Saving film: {film['title']}")
                film_id = save_film({
                    'imdb_id': film['imdb_id'],
                    'title': film['title'],
                    'rating': film['rating'],
                    'year': film['year']
                })
                film_ids[film['imdb_id']] = {
                    'film_id': film_id,
                    'title': film['title'],
                    'actors': film.get('actors', [])
                }
                logger.info(f"  ✓ Film saved with ID: {film_id}")
            except Exception as e:
                logger.error(f"  ❌ Error saving film '{film['title']}': {e}")
        
        logger.info(f"\n✓ Saved {len(film_ids)} films successfully")
        return film_ids
        
    except Exception as e:
        logger.error(f"❌ Error in save_films_task: {e}")
        raise


save_films = PythonOperator(
    task_id='save_films',
    python_callable=save_films_task,
    dag=dag,
)


# ==================== OPERATION 5: SAVE ACTORS ====================
def save_actors_task(ti):
    """
    Operation 5: Extract and save all unique actors from films
    - Collect all actor names from all films
    - Insert/update actors with UNIQUE constraint on name
    - Handle duplicates gracefully
    - Returns actor mapping
    """
    logger.info("=" * 80)
    logger.info("OPERATION 5: SAVING ACTORS TO DATABASE")
    logger.info("=" * 80)
    
    try:
        films = ti.xcom_pull(task_ids='extract_films')
        
        if not films:
            logger.error("❌ No films received from extract task")
            return None
        
        # Collect all unique actors
        all_actors = set()
        for film in films:
            actors = film.get('actors', [])
            all_actors.update(actors)
        
        logger.info(f"📝 Found {len(all_actors)} unique actors across all films")
        
        actor_ids = {}
        for actor_name in sorted(all_actors):
            try:
                logger.info(f"👤 Saving actor: {actor_name}")
                actor_id = save_actor(actor_name)
                actor_ids[actor_name] = actor_id
                logger.info(f"  ✓ Actor saved with ID: {actor_id}")
            except Exception as e:
                logger.error(f"  ❌ Error saving actor '{actor_name}': {e}")
        
        logger.info(f"\n✓ Saved {len(actor_ids)} actors successfully")
        return actor_ids
        
    except Exception as e:
        logger.error(f"❌ Error in save_actors_task: {e}")
        raise


save_actors = PythonOperator(
    task_id='save_actors',
    python_callable=save_actors_task,
    dag=dag,
)


# ==================== OPERATION 6: LINK ACTORS TO FILMS ====================
def link_actors_to_films_task(ti):
    """
    Operation 6: Create many-to-many relationships between actors and films
    - For each film, link all its actors via actor_film junction table
    - Uses actor_id and film_id from previous operations
    - Handles duplicate relationships gracefully
    """
    logger.info("=" * 80)
    logger.info("OPERATION 6: LINKING ACTORS TO FILMS (M2M RELATIONSHIPS)")
    logger.info("=" * 80)
    
    try:
        films = ti.xcom_pull(task_ids='extract_films')
        film_ids = ti.xcom_pull(task_ids='save_films')
        actor_ids = ti.xcom_pull(task_ids='save_actors')
        
        if not films or not film_ids or not actor_ids:
            logger.error("❌ Missing data from previous tasks")
            return None
        
        link_count = 0
        for film in films:
            film_imdb_id = film['imdb_id']
            if film_imdb_id not in film_ids:
                logger.warning(f"⚠ Film {film['title']} not found in film_ids mapping")
                continue
            
            film_id = film_ids[film_imdb_id]['film_id']
            actors = film.get('actors', [])
            
            logger.info(f"\n🔗 Linking film '{film['title']}' (ID: {film_id}) with {len(actors)} actors:")
            
            for actor_name in actors:
                if actor_name not in actor_ids:
                    logger.warning(f"  ⚠ Actor '{actor_name}' not found in actor_ids mapping")
                    continue
                
                actor_id = actor_ids[actor_name]
                try:
                    link_actor_to_film(actor_id, film_id)
                    logger.info(f"  ✓ Linked {actor_name} (ID: {actor_id}) to film")
                    link_count += 1
                except Exception as e:
                    logger.error(f"  ❌ Error linking actor '{actor_name}': {e}")
        
        logger.info(f"\n✓ Created {link_count} actor-film relationships successfully")
        return {'links_created': link_count}
        
    except Exception as e:
        logger.error(f"❌ Error in link_actors_to_films_task: {e}")
        raise


link_actors_to_films = PythonOperator(
    task_id='link_actors_to_films',
    python_callable=link_actors_to_films_task,
    dag=dag,
)


# ==================== OPERATION 7: VALIDATE DATA ====================
def validate_data_task():
    """
    Operation 7: Validate data integrity after loading
    - Check row counts in each table
    - Verify referential integrity
    - Report any orphaned records
    """
    logger.info("=" * 80)
    logger.info("OPERATION 7: VALIDATING DATA INTEGRITY")
    logger.info("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check row counts
        logger.info("📊 Data Summary:")
        cursor.execute('SELECT COUNT(*) FROM films')
        film_count = cursor.fetchone()[0]
        logger.info(f"  - Films: {film_count}")
        
        cursor.execute('SELECT COUNT(*) FROM actors')
        actor_count = cursor.fetchone()[0]
        logger.info(f"  - Actors: {actor_count}")
        
        cursor.execute('SELECT COUNT(*) FROM actor_film')
        link_count = cursor.fetchone()[0]
        logger.info(f"  - Actor-Film Links: {link_count}")
        
        # Check for orphaned relationships
        logger.info("\n🔍 Checking referential integrity:")
        
        # Check for actor_film entries with missing actors
        cursor.execute('''
            SELECT COUNT(*) FROM actor_film af 
            WHERE NOT EXISTS (SELECT 1 FROM actors a WHERE a.actor_id = af.actor_id)
        ''')
        orphaned_actors = cursor.fetchone()[0]
        if orphaned_actors > 0:
            logger.warning(f"  ⚠ Found {orphaned_actors} orphaned actor references")
        else:
            logger.info("  ✓ No orphaned actor references")
        
        # Check for actor_film entries with missing films
        cursor.execute('''
            SELECT COUNT(*) FROM actor_film af 
            WHERE NOT EXISTS (SELECT 1 FROM films f WHERE f.film_id = af.film_id)
        ''')
        orphaned_films = cursor.fetchone()[0]
        if orphaned_films > 0:
            logger.warning(f"  ⚠ Found {orphaned_films} orphaned film references")
        else:
            logger.info("  ✓ No orphaned film references")
        
        logger.info("✓ Data validation complete!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error validating data: {e}")
        raise


validate_data = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data_task,
    dag=dag,
)


# ==================== OPERATION 8: CALCULATE ACTOR RATINGS ====================
def calculate_ratings_task():
    """
    Operation 8: Calculate average ratings for each actor
    - For each actor, iterate through all their films
    - Calculate AVG, MIN, MAX of film ratings
    - Store aggregated results in actor_ratings table
    """
    logger.info("=" * 80)
    logger.info("OPERATION 8: CALCULATING ACTOR AVERAGE RATINGS")
    logger.info("=" * 80)
    
    try:
        calculate_actor_ratings()
        logger.info("✓ Actor ratings calculation complete!")
        return True
    except Exception as e:
        logger.error(f"❌ Error calculating ratings: {e}")
        raise


calculate_ratings = PythonOperator(
    task_id='calculate_ratings',
    python_callable=calculate_ratings_task,
    dag=dag,
)


# ==================== OPERATION 9: GENERATE REPORT ====================
def generate_report_task():
    """
    Operation 9: Generate final report with statistics and insights
    - Display top-rated actors
    - Show actor statistics (films count, rating range)
    - Display database summary
    """
    logger.info("=" * 80)
    logger.info("OPERATION 9: GENERATING FINAL REPORT")
    logger.info("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Top 10 actors
        logger.info("\n🏆 TOP 10 ACTORS BY AVERAGE RATING:\n")
        cursor.execute('''
            SELECT 
                actor_name,
                total_films,
                ROUND(average_rating::numeric, 2) as avg_rating,
                ROUND(min_rating::numeric, 2) as min_rating,
                ROUND(max_rating::numeric, 2) as max_rating
            FROM actor_ratings
            WHERE average_rating IS NOT NULL
            ORDER BY average_rating DESC
            LIMIT 10
        ''')
        
        results = cursor.fetchall()
        if results:
            logger.info(f"{'Rank':<5} {'Actor Name':<30} {'Films':<8} {'Avg':<8} {'Min':<8} {'Max':<8}")
            logger.info("-" * 75)
            for rank, (name, films, avg, min_r, max_r) in enumerate(results, 1):
                logger.info(f"{rank:<5} {name:<30} {films:<8} {avg:<8} {min_r:<8} {max_r:<8}")
        else:
            logger.warning("No actor ratings found")
        
        # Overall statistics
        logger.info("\n📈 OVERALL STATISTICS:\n")
        cursor.execute('SELECT COUNT(*) FROM actor_ratings WHERE average_rating IS NOT NULL')
        rated_actors = cursor.fetchone()[0]
        logger.info(f"  - Total Rated Actors: {rated_actors}")
        
        cursor.execute('SELECT COUNT(*) FROM films')
        total_films = cursor.fetchone()[0]
        logger.info(f"  - Total Films: {total_films}")
        
        cursor.execute('SELECT COUNT(*) FROM actors')
        total_actors = cursor.fetchone()[0]
        logger.info(f"  - Total Actors: {total_actors}")
        
        cursor.execute('SELECT COUNT(*) FROM actor_film')
        total_links = cursor.fetchone()[0]
        logger.info(f"  - Total Relationships: {total_links}")
        
        cursor.execute('SELECT AVG(average_rating) FROM actor_ratings WHERE average_rating IS NOT NULL')
        avg_rating = cursor.fetchone()[0]
        if avg_rating:
            logger.info(f"  - Average Actor Rating: {avg_rating:.2f}/10")
        
        logger.info("\n✓ Report generation complete!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating report: {e}")
        raise


generate_report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report_task,
    dag=dag,
)


# ==================== DAG TASK DEPENDENCIES ====================
"""
Task flow:
1. init_database (Initialize schema)
    ↓
2. validate_database (Verify schema created)
    ↓
3. extract_films (Get films from IMDb)
    ↓
4. save_films (Save films to DB)  ←→  5. save_actors (Save actors to DB)
    ↓                                       ↓
6. link_actors_to_films (Create M2M relationships)
    ↓
7. validate_data (Verify data integrity)
    ↓
8. calculate_ratings (Calculate actor averages)
    ↓
9. generate_report (Display results)
"""

init_database >> validate_database
validate_database >> extract_films
extract_films >> [save_films, save_actors]
[save_films, save_actors] >> link_actors_to_films
link_actors_to_films >> validate_data
validate_data >> calculate_ratings
calculate_ratings >> generate_report
