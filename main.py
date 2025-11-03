from etl.extract import get_film_data
from etl.reddit_extract import get_reddit_comments
from etl.sentiment import compute_sentiment
from etl.load import load_dim_film, load_dim_actor, load_fact

movies = ["Inception", "Interstellar", "The Matrix"]

def run_pipeline():
    for title in movies:
        film = get_film_data(title)
        if not film:
            continue
        comments = get_reddit_comments(title)
        avg_sentiment, num_comments = compute_sentiment(comments)

        load_dim_film(film)
        for actor in film['actors']:
            load_dim_actor({"actor_name": actor["name"], "birth_date": None, "gender": None, "nationality": None, "num_films": 1})

        actor_film_score = (0.7 * film['imdb_rating'] if film['imdb_rating'] else 0) + (0.3 * avg_sentiment)
        fact = {
            "film_id": None,
            "actor_id": None,
            "date_id": 1,
            "avg_sentiment_score": avg_sentiment,
            "num_comments": num_comments,
            "actor_film_score": actor_film_score,
            "film_rating_imdb": film['imdb_rating'],
            "calculated_actor_rating": actor_film_score
        }
        load_fact(fact)
