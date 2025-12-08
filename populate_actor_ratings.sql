INSERT INTO actor_ratings (actor_name, total_films, average_rating, min_rating, max_rating)
SELECT 
    a.name as actor_name,
    COUNT(DISTINCT f.imdb_id) as total_films,
    ROUND(AVG(f.rating)::NUMERIC, 2) as average_rating,
    MIN(f.rating) as min_rating,
    MAX(f.rating) as max_rating
FROM actors a
LEFT JOIN films f ON true
WHERE a.films_count > 0
GROUP BY a.name
HAVING COUNT(DISTINCT f.imdb_id) > 0
ON CONFLICT (actor_name) DO UPDATE SET
    total_films = EXCLUDED.total_films,
    average_rating = EXCLUDED.average_rating,
    min_rating = EXCLUDED.min_rating,
    max_rating = EXCLUDED.max_rating,
    last_updated = CURRENT_TIMESTAMP;
