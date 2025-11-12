from imdb import IMDb

ia = IMDb()

def get_film_data(title):
    results = ia.search_movie(title)
    if not results:
        return None
    movie = ia.get_movie(results[0].movieID)
    actors = movie.get('cast', [])[:10]  # top 10 actors
    actors_data = [{"id": a.personID, "name": a['name']} for a in actors]
    return {
        "imdb_id": movie.movieID,
        "title": movie.get('title'),
        "year": movie.get('year'),
        "genre": ', '.join(movie.get('genres', [])),
        "duration": movie.get('runtimes', [None])[0],
        "director": ', '.join([d['name'] for d in movie.get('director', [])]),
        "actors": actors_data,
        "imdb_rating": movie.get('rating'),
        "box_office": movie.get('box office', {}).get('Cumulative Worldwide Gross')
    }
