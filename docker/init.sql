-- Drop existing tables to start fresh
DROP TABLE IF EXISTS actor_film CASCADE;
DROP TABLE IF EXISTS actor_ratings CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS films CASCADE;
DROP TABLE IF EXISTS actors CASCADE;

-- Films Table with UNIQUE constraint on title and imdb_id
CREATE TABLE films (
    film_id SERIAL PRIMARY KEY,
    imdb_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL UNIQUE,
    rating FLOAT,
    year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Actors Table with UNIQUE constraint on name
CREATE TABLE actors (
    actor_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-Many Junction Table between Actors and Films
CREATE TABLE actor_film (
    actor_film_id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL,
    film_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES films(film_id) ON DELETE CASCADE,
    UNIQUE(actor_id, film_id)
);

-- Actor Ratings Table - stores calculated average ratings per actor
CREATE TABLE actor_ratings (
    actor_rating_id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL UNIQUE,
    actor_name VARCHAR(255) NOT NULL,
    total_films INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0,
    min_rating FLOAT,
    max_rating FLOAT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id) ON DELETE CASCADE
);

-- Recommendations Table (kept for backwards compatibility)
CREATE TABLE recommendations (
    rec_id SERIAL PRIMARY KEY,
    film_title VARCHAR(255),
    imdb_rating FLOAT,
    reddit_score INT,
    recommendation_score INT,
    comments_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_films_imdb_id ON films(imdb_id);
CREATE INDEX IF NOT EXISTS idx_films_title ON films(title);
CREATE INDEX IF NOT EXISTS idx_actors_name ON actors(name);
CREATE INDEX IF NOT EXISTS idx_actor_film_actor ON actor_film(actor_id);
CREATE INDEX IF NOT EXISTS idx_actor_film_film ON actor_film(film_id);
CREATE INDEX IF NOT EXISTS idx_actor_ratings_average ON actor_ratings(average_rating DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON recommendations(recommendation_score DESC);
