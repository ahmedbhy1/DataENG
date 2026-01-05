from etl.extract import get_latest_films
from etl.reddit_extract import get_film_comments
from etl.sentiment import rate_comments
from etl.load import save_film, save_actor, save_recommendation
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute the complete ETL pipeline"""
    print("\n" + "="*60)
    print("MOVIE RECOMMENDATION PIPELINE")
    print("="*60)

    print("\n[STEP 1] Getting movies...")
    films = get_latest_films(limit=5)

    if not films:
        print("No movies found!")
        return False

    print(f"\nFound {len(films)} movies:")
    for i, film in enumerate(films, 1):
        print(f"  {i}. {film['title']} ({film['rating']}/10)")

    # Get Reddit comments and calculate scores
    print(f"\n[STEP 2] Analyzing Reddit sentiment...")
    for film in films:
        title = film['title']
        print(f"  {title}...", end=" ", flush=True)
        
        comments = get_film_comments(title, limit=50)
        reddit_score = rate_comments(comments) if comments else 0
        
        # Save to database
        save_film({
            'imdb_id': film['imdb_id'],
            'title': title,
            'rating': film['rating'],
            'year': film['year']
        })
        
        for actor in film.get('actors', []):
            save_actor({'name': actor, 'films_count': 1})
        
        # Calculate score
        imdb_score = (film['rating'] * 10) if film['rating'] else 0
        rec_score = int(0.6 * imdb_score + 0.4 * reddit_score)
        
        save_recommendation({
            'film_title': title,
            'imdb_rating': film['rating'],
            'reddit_score': reddit_score,
            'recommendation_score': rec_score,
            'comments_count': len(comments)
        })
        
        print(f"Score: {rec_score}/100")

    print("\n" + "="*60)
    print("COMPLETED!")
    print("="*60)
    print("View results: http://localhost:5000\n")
    return True


if __name__ == "__main__":
    run_pipeline()
