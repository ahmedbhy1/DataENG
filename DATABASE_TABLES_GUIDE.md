# Movie Recommendation System - Database Tables Guide

## Overview
The `imdb_reddit` database contains 50 tables total:
- **3 Custom Project Tables** (your application data)
- **5 Dimensional/Fact Tables** (data warehouse structure)
- **42 Airflow System Tables** (scheduling, logging, tracking)

---

## 📊 CUSTOM PROJECT TABLES (Your Data)

### 1. **films** (52 rows)
**Purpose**: Stores information about movies being analyzed
**Columns**:
- `imdb_id` (text) - IMDb unique identifier
- `title` (text) - Movie title
- `rating` (double precision) - IMDb rating (0-10)
- `year` (bigint) - Release year

**Example Data**:
```
Zootopie 2 | 7.7 | 2025
Frankenstein | 7.5 | 2025
The Shawshank Redemption | 9.3 | 1994
```

**Used By**: 
- Extract task (stores extracted movies)
- Recommendations table (linked via film_title)
- dim_film table (data warehouse)

---

### 2. **actors** (228 rows)
**Purpose**: Stores actor information
**Columns**:
- `name` (text) - Actor name
- `films_count` (bigint) - Number of films they appeared in

**Example Data**:
```
Tom Hanks | 5
Meryl Streep | 3
Leonardo DiCaprio | 4
```

**Used By**:
- Process task (stores actors from extracted movies)
- dim_actor table (data warehouse)

---

### 3. **recommendations** (52 rows)
**Purpose**: Stores final recommendation scores combining IMDb ratings and Reddit sentiment
**Columns**:
- `film_title` (text) - Name of the film
- `imdb_rating` (double precision) - IMDb rating (0-10)
- `reddit_score` (bigint) - Sentiment score from Reddit comments (0-100)
- `recommendation_score` (bigint) - **Final score** (0-100) calculated as: 0.6 × IMDb + 0.4 × Reddit
- `comments_count` (bigint) - Number of Reddit comments analyzed

**Example Data**:
```
The Shawshank Redemption | 9.3 | 77 | 77 | 50 comments
The Godfather | 9.2 | 76 | 76 | 50 comments
Zootopie 2 | 7.7 | 69 | 69 | 50 comments
```

**Formula**: 
```
recommendation_score = (imdb_rating × 10 × 0.6) + (reddit_score × 0.4)
```

**Used By**:
- Web dashboard (displays top recommendations)
- Analytics queries
- Decision making

---

## 📈 DATA WAREHOUSE TABLES (Dimensional/Fact Model)

### 4. **dim_film** (Dimension Table)
**Purpose**: Complete film information for data warehouse analytics
**Columns**:
- `film_id` (integer, Primary Key)
- `film_title` (varchar(255))
- `release_year` (integer)
- `genre` (varchar(100))
- `duration` (integer) - in minutes
- `director` (varchar(255))
- `language` (varchar(50))
- `country` (varchar(50))
- `imdb_rating` (double precision)
- `box_office` (double precision)

**Used By**: Fact table (fact_filmsentiment)

---

### 5. **dim_actor** (Dimension Table)
**Purpose**: Actor information for data warehouse
**Columns**:
- `actor_id` (integer, Primary Key)
- Actor details

**Used By**: Fact table (fact_filmsentiment)

---

### 6. **dim_date** (Dimension Table)
**Purpose**: Time dimension for tracking analysis dates
**Used By**: Fact table (fact_filmsentiment)

---

### 7. **dim_redditsource** (Dimension Table)
**Purpose**: Reddit source details (subreddit info, etc.)
**Used By**: Analytics queries

---

### 8. **fact_filmsentiment** (Fact Table - Aggregated)
**Purpose**: Central analytics table combining film, actor, and sentiment data
**Columns**:
- `film_id` (FK to dim_film)
- `actor_id` (FK to dim_actor)
- `date_id` (FK to dim_date)
- `avg_sentiment_score` (double precision) - Average sentiment
- `num_comments` (integer) - Comment count
- `actor_film_score` (double precision)
- `film_rating_imdb` (double precision)
- `calculated_actor_rating` (double precision)

**Used By**: Advanced analytics, reporting, dashboards

---

## 🔧 AIRFLOW SYSTEM TABLES (Internal Use)

These 42 tables manage Airflow operations:

### Core Airflow Tables:
- **dag** - Registered DAGs
- **dag_run** - DAG execution history
- **task_instance** - Individual task execution logs
- **log** - Task logs and output
- **xcom** - Cross-communication between tasks
- **job** - Job tracking
- **connection** - Database/API connections

### Metadata Tables:
- **ab_user**, **ab_role**, **ab_permission** - User management
- **serialized_dag** - DAG definitions
- **dag_code** - DAG source code
- **variable** - Airflow variables
- **import_error** - DAG import errors

**Note**: These are automatically managed by Airflow. Do NOT modify directly.

---

## 📌 Data Flow

```
┌──────────────────┐
│   IMDb Website   │  (Web Scraping)
└────────┬─────────┘
         │
         ├─► FILMS table
         │   (movies extracted)
         │
         ├─► ACTORS table
         │   (cast information)
         │
         └─► DIM_FILM table (warehouse)

┌──────────────────────┐
│   Reddit Comments    │  (HTTP API)
└────────┬─────────────┘
         │
         ├─► Sentiment Analysis (TextBlob)
         │
         ├─► reddit_score (0-100)
         │
         └─► RECOMMENDATIONS table

┌──────────────────────────────────────┐
│    RECOMMENDATIONS TABLE (FINAL)     │
│  ┌────────────────────────────────┐  │
│  │ recommendation_score            │  │ ◄─ Displayed on Web Dashboard
│  │ = (60% IMDb) + (40% Reddit)     │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
         │
         └─► FACT_FILMSENTIMENT (DW analytics)
```

---

## 🚀 How to View in PgAdmin

1. **Go to**: http://localhost:5050
2. **Login**: 
   - Email: `admin@admin.com`
   - Password: `admin`
3. **Add Server** (if not already added):
   - Name: `imdb_reddit`
   - Host: `postgres`
   - Port: `5432`
   - User: `postgres`
   - Password: `postgres`
4. **Navigate**: Servers → imdb_reddit → Databases → imdb_reddit → Schemas → public → Tables

---

## 📊 Current Data Summary

| Table | Rows | Purpose |
|-------|------|---------|
| **films** | 52 | Movie catalog |
| **actors** | 228 | Actor information |
| **recommendations** | 52 | Final scores |
| **dim_film** | ? | Warehouse (films) |
| **dim_actor** | ? | Warehouse (actors) |
| **dim_date** | ? | Warehouse (dates) |
| **fact_filmsentiment** | ? | Warehouse (analytics) |
| **Airflow Tables** | 42 | System management |

---

## 💡 Key Insights

- **52 Films**: Analyzed trending movies
- **228 Actors**: From all 52 films
- **52 Recommendations**: One per film with combined scoring
- **Scoring Formula**: `recommendation_score = (imdb_rating×10×0.6) + (reddit_score×0.4)`
- **Data Update**: Daily via Airflow DAG (trending_movies_pipeline)

---

## 🔗 Related Resources

- **Web Dashboard**: http://localhost:5000
- **Airflow UI**: http://localhost:8080
- **PgAdmin**: http://localhost:5050
- **Database**: PostgreSQL on localhost:5432
