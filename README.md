# Movie Sentiment Analysis & Actor Ratings Pipeline

![Insalogo](./images/insa.txt)

Project [DATA Engineering](https://www.riccardotommasini.com/courses/dataeng-insa-ot/) is provided by [INSA Lyon](https://www.insa-lyon.fr/).

### Abstract

An ETL pipeline that extracts movie data with actor information, fetches Reddit comments, performs sentiment analysis, and calculates actor ratings based on their filmography. Uses Apache Airflow for orchestration and PostgreSQL for data storage with deduplication via UPSERT operations.

## Architecture Overview

**Stack:** Python 3.10+ | Apache Airflow 2.7.2 | PostgreSQL 15 | Docker | Flask Web App

## Data Pipeline Components

### 1. Extract Layer (`extract.py`)
- **Primary Source:** Curated movie dataset (15 real films with verified cast data)
- **Fallback APIs:** JustWatch API (free, no key required)
- **Data Extracted:** Film title, IMDb ID, rating, release year, 10 actors per film
- **Movies Included:** The Godfather trilogy, Dark Knight trilogy, Inception, Matrix trilogy, classic films
- **Actor Overlap:** Deliberate curation ensures actors appear in multiple films (e.g., Al Pacino in both Godfather films)
- **Execution Time:** 0.01 seconds (cached dataset)

### 2. Reddit Comments Extraction (`reddit_extract.py`)
- **API Used:** Reddit API via PRAW (anonymous/public)
- **Data Extracted:** 5-10 comments per film
- **Purpose:** Real user sentiment about movies
- **Execution Time:** ~2-3 seconds per film

### 3. Sentiment Analysis (`sentiment.py`)
- **Method:** Text processing with sentiment scoring (0-100 scale)
- **Output:** Average sentiment score per film, individual comment analysis
- **Execution Time:** ~0.5 seconds per 10 comments

### 4. Load Layer (`load.py`)
- **Database:** PostgreSQL 15 with UPSERT operations
- **Deduplication Strategy:**
  - Films: `ON CONFLICT (imdb_id) DO UPDATE` - prevents duplicate movies
  - Actors: `ON CONFLICT (name) DO UPDATE` - prevents duplicate actors
  - Relationships: `ON CONFLICT (actor_id, film_id) DO NOTHING` - prevents duplicate links
- **Database Tables:** 
  - `films` - movie metadata
  - `actors` - actor names
  - `actor_film` - many-to-many relationships
  - `actor_ratings` - calculated average ratings per actor

### 5. Pipeline Orchestration (`run_pipeline.py`)
- **Flow:** Extract films → Fetch Reddit comments → Analyze sentiment → Save to database
- **Idempotent:** Safe to run multiple times (UPSERT prevents duplicates)
- **Total Execution Time:** 15-20 seconds for 3-5 films

### 6. Web Application (`web_app.py`)
- **Framework:** Flask on port 5000
- **Features:** Actor ratings display, film statistics, API endpoints
- **Routes:** 
  - `/` - Top actors by rating visualization
  - `/api/actor-ratings` - JSON actor data
  - `/api/films` - All films sorted by rating
  - `/api/stats` - Pipeline statistics

## Data Schema

```
films (10 rows)
├── film_id (PK)
├── imdb_id (UNIQUE)
├── title
├── rating
└── year

actors (90 rows)
├── actor_id (PK)
├── name (UNIQUE)
└── created_at

actor_film (100 rows) - Junction table
├── actor_id (FK)
├── film_id (FK)
└── UNIQUE(actor_id, film_id)

actor_ratings (90 rows) - Calculated
├── actor_name
├── total_films
├── average_rating
├── min_rating
└── max_rating
```

## Deleted Components

**Removed Unused Tables:**
- `recommendations` - No recommendation logic implemented
- `dim_actor`, `dim_film`, `dim_date`, `dim_redditsource` - Empty dimension tables
- `fact_filmsentiment` - Unused fact table
- `reddit_comments` - Removed from storage (comments still analyzed)

**Removed Functions:**
- `save_reddit_comments()` - Comments analyzed but not persisted
- `save_recommendation()` - Recommendation logic removed

## Setup & Execution

### Docker Deployment
```bash
cd docker
docker-compose up -d
```

Services Started:
- PostgreSQL on `localhost:5432`
- pgAdmin on `localhost:5050`
- Apache Airflow on `localhost:8080`
- Flask app on `localhost:5000`

### Run Pipeline
```bash
python docker/dags/run_pipeline.py
```

## Key Features

✓ **No Duplicates:** Database-level UPSERT constraints ensure data integrity  
✓ **Actor Overlap:** Multiple actors appear in multiple films for better ratings  
✓ **Real Data:** Curated dataset of famous films instead of TV shows  
✓ **Idempotent:** Run pipeline unlimited times without data duplication  
✓ **Fast Extraction:** 0.01 seconds for films (cached), ~15-20 seconds full pipeline  
✓ **Web Visualization:** Flask app displays actor ratings and film statistics  

## APIs Used

| API | Purpose | Status | Fallback |
|-----|---------|--------|----------|
| JustWatch | Movie data | Available (free) | Curated dataset |
| Reddit (PRAW) | Comments | Active | N/A |
| TMDB | Movie details | Unavailable (invalid key) | Curated dataset |
| IMDb | Top 250 movies | Blocked (anti-bot) | Curated dataset |

## Performance Metrics

- **Film Extraction:** 0.01 seconds (cached dataset)
- **Reddit Comments:** 2-3 seconds per film
- **Sentiment Analysis:** 0.5 seconds per 10 comments
- **Database Save:** 1-2 seconds per batch
- **Total per Run:** 15-20 seconds (3-5 films)

## Notes

- Database uses PostgreSQL 15 with transactions and UPSERT for consistency
- All timestamps recorded via `created_at` columns
- Airflow system tables (`ab_*`, `dag_*`, `task_*`) preserved for workflow tracking
- Cache optimized: repeated runs update existing data without growth 
