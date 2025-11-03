-- Dim_Film
CREATE TABLE IF NOT EXISTS Dim_Film (
    film_id SERIAL PRIMARY KEY,
    film_title VARCHAR(255),
    release_year INT,
    genre VARCHAR(100),
    duration INT,
    director VARCHAR(255),
    language VARCHAR(50),
    country VARCHAR(50),
    imdb_rating FLOAT,
    box_office FLOAT
);

-- Dim_Actor
CREATE TABLE IF NOT EXISTS Dim_Actor (
    actor_id SERIAL PRIMARY KEY,
    actor_name VARCHAR(255),
    birth_date DATE,
    gender VARCHAR(10),
    nationality VARCHAR(50),
    num_films INT
);

-- Dim_Date
CREATE TABLE IF NOT EXISTS Dim_Date (
    date_id SERIAL PRIMARY KEY,
    date DATE,
    year INT,
    month INT,
    day INT
);

-- Dim_RedditSource
CREATE TABLE IF NOT EXISTS Dim_RedditSource (
    reddit_id SERIAL PRIMARY KEY,
    subreddit VARCHAR(255),
    data_source VARCHAR(255),
    collection_date DATE
);

-- Fact_FilmSentiment
CREATE TABLE IF NOT EXISTS Fact_FilmSentiment (
    film_id INT REFERENCES Dim_Film(film_id),
    actor_id INT REFERENCES Dim_Actor(actor_id),
    date_id INT REFERENCES Dim_Date(date_id),
    avg_sentiment_score FLOAT,
    num_comments INT,
    actor_film_score FLOAT,
    film_rating_imdb FLOAT,
    calculated_actor_rating FLOAT
);
