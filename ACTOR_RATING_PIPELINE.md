# Actor Rating Pipeline - New Architecture

## Overview
You've shifted focus from movie recommendations to **actor performance analysis**. The system now:

1. **Extracts** trending films from IMDb
2. **Rates** each film based on IMDb rating
3. **Stores** actors separately in the database
4. **Calculates** average ratings for each actor based on their filmography

---

## Pipeline Flow

```
┌─────────────────┐
│  Extract Films  │  (from IMDb)
└────────┬────────┘
         │
         ├─► Film 1: Rating 8.5
         ├─► Film 2: Rating 7.8  
         └─► Film 3: Rating 8.2
         │
         ▼
┌─────────────────┐
│  Rate Each Film │  (Store imdb_id, title, rating, year)
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ Store Actors     │  (From each film's cast)
│ Separately       │  (Actor names → actors table)
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────┐
│ Calculate Actor Average Ratings│  (SQL-based aggregation)
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│   actor_ratings Table          │  (Final Output)
│  ┌──────────────────────────┐  │
│  │ Actor A: 8.35 avg rating │  │
│  │ Actor B: 7.90 avg rating │  │
│  │ Actor C: 8.10 avg rating │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
         │
         ▼
   Web Dashboard
   (http://localhost:5000)
```

---

## Airflow DAG Tasks

### New DAG Name: `actor_rating_pipeline`

**Task Sequence:**

1. **extract_films** (Python Operator)
   - Fetches 10 trending movies from IMDb
   - Returns: List of films with title, imdb_id, rating, year, actors

2. **rate_film_1/2/3** (Python Operators - Parallel)
   - Rates each film
   - Saves to `films` table
   - Input: Film data with IMDb rating

3. **store_actors_1/2/3** (Python Operators - Parallel)
   - Stores actors from each film
   - Saves to `actors` table
   - Runs after film rating complete

4. **calculate_actor_ratings** (Bash Operator - Final)
   - Executes SQL aggregation
   - Creates/updates `actor_ratings` table
   - Calculates: average_rating, min_rating, max_rating per actor

---

## Database Schema

### Tables Used:

#### 1. **films** (Existing)
```
imdb_id | title | rating | year
---------|-------|--------|------
tt1234567 | Film A | 8.5 | 2025
tt7654321 | Film B | 7.8 | 2025
```

#### 2. **actors** (Existing)
```
name | films_count
------|-------------
Actor A | 1
Actor B | 1
```

#### 3. **actor_ratings** (NEW)
```
actor_name | total_films | average_rating | min_rating | max_rating | last_updated
------------|-------------|----------------|------------|------------|------------------
Actor A    | 2          | 8.35           | 8.3        | 8.4        | 2025-12-08
Actor B    | 1          | 7.90           | 7.9        | 7.9        | 2025-12-08
```

**Why this table?**
- Denormalized design for fast queries
- Direct average calculations
- No need for dimensional tables
- Focus on actor performance, not film analysis

---

## Web Dashboard

### Location: http://localhost:5000

### Features:

1. **Statistics Panel**
   - Total Films analyzed
   - Total Actors extracted
   - Rated Actors count
   - Average rating across all actors

2. **Top Rated Actors Table**
   - Rank | Actor Name | Films | Avg Rating | Min | Max
   - Sortable by average rating
   - Shows min/max ratings for context

3. **Control Buttons**
   - "Run Pipeline" - Executes full workflow
   - "Refresh" - Reloads actor ratings

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Home page with top actors |
| `/api/actor-ratings` | GET | All actor ratings as JSON |
| `/api/top-actors` | GET | Top 10 actors |
| `/api/films` | GET | All rated films |
| `/api/actor/<name>` | GET | Individual actor details |
| `/api/run-pipeline` | POST | Execute full pipeline |
| `/api/stats` | GET | Summary statistics |

---

## Key SQL Query

The core actor rating calculation:

```sql
-- Calculate average rating for each actor based on their films
WITH actor_film_ratings AS (
    SELECT 
        a.name as actor_name,
        COUNT(f.imdb_id) as film_count,
        AVG(f.rating) as avg_rating,
        MIN(f.rating) as min_rating,
        MAX(f.rating) as max_rating
    FROM actors a
    LEFT JOIN films f ON true
    WHERE a.films_count > 0
    GROUP BY a.name
)
INSERT INTO actor_ratings 
    (actor_name, total_films, average_rating, min_rating, max_rating)
SELECT actor_name, film_count, ROUND(avg_rating::NUMERIC, 2), min_rating, max_rating
FROM actor_film_ratings
ON CONFLICT (actor_name) DO UPDATE SET
    total_films = EXCLUDED.total_films,
    average_rating = EXCLUDED.average_rating,
    min_rating = EXCLUDED.min_rating,
    max_rating = EXCLUDED.max_rating,
    last_updated = CURRENT_TIMESTAMP;
```

---

## Removed Components

❌ **reddit_extract.py** - No longer needed (sentiment analysis removed)
❌ **sentiment.py** - Replaced with SQL aggregation
❌ **recommendations table** - Replaced with actor_ratings table
❌ **Dimensional tables** (dim_film, dim_actor, dim_date, fact_filmsentiment)
   - Simplification: Focus on actors, not analytics warehouse

---

## How to Use

### 1. Start the System
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 2. Start the Web App
```bash
cd docker/dags
python web_app.py
```

### 3. Access Dashboard
- Dashboard: http://localhost:5000
- Airflow: http://localhost:8080
- Database: localhost:5432

### 4. Run the Pipeline
Click "Run Pipeline" button on the web dashboard, or trigger from Airflow UI:
```bash
airflow dags trigger actor_rating_pipeline
```

### 5. View Results
Top-rated actors appear in the dashboard table, sorted by average rating.

---

## Example Output

```
🏆 TOP RATED ACTORS:
Rank | Actor Name      | Films | Avg Rating | Min | Max
-----|-----------------|-------|------------|-----|-----
#1   | Tom Hanks       | 3     | 8.60/10    | 8.3 | 8.9
#2   | Meryl Streep    | 2     | 8.45/10    | 8.2 | 8.7
#3   | Leonardo DiCaprio| 4    | 8.35/10    | 7.9 | 8.8
```

---

## Benefits of This Architecture

✅ **Simplified** - Single focus: actor performance
✅ **Faster** - No sentiment analysis overhead
✅ **Cleaner** - Removed unnecessary dimensional tables
✅ **Scalable** - Easy to add more film sources
✅ **Actionable** - Direct actor performance insights

---

## Next Steps

You can further enhance by:
- Adding actor metadata (age, genre preferences, etc.)
- Tracking actor career trends over time
- Comparing actor ratings across genres
- Identifying rising/falling stars
- Generating recommendations based on actor ratings
