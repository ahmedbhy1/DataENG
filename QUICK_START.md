# Quick Start Guide

## Project Overview
Actor Rating Pipeline - A data engineering system that extracts films from IMDb, rates them, and calculates average actor ratings based on their filmography.

---

## Running the Project

### Start All Services
```powershell
cd "c:\Users\msi\Desktop\projet data\DataENG"
docker-compose -f docker/docker-compose.yml up -d
```

### Stop All Services
```powershell
docker-compose -f docker/docker-compose.yml down
```

### Restart Services
```powershell
docker-compose -f docker/docker-compose.yml restart
```

---

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Actor Rating Dashboard** | http://localhost:5000/ | Public |
| **Airflow UI** | http://localhost:8080/ | admin/admin |
| **PgAdmin** | http://localhost:5050/ | admin@admin.com/admin |
| **PostgreSQL** | localhost:5432 | postgres/postgres |

---

## Web Dashboard (http://localhost:5000/)

### Features
- ⭐ **Statistics Panel** - Shows total films, actors, rated actors, and average rating
- 🏆 **Top Rated Actors Table** - Displays top 20 actors with rankings
- 🚀 **Run Pipeline Button** - Executes the full pipeline (extract → rate → calculate)
- 🔄 **Refresh Button** - Reloads current data

### Pipeline Execution
1. Click **"Run Pipeline"** button
2. Confirm the dialog
3. Wait for processing (typically 15-20 seconds)
4. View updated actor ratings in the table below

### Data Shown
- **Actor Name:** Name of the actor
- **Films:** Number of films in their filmography
- **Average Rating:** Average rating of all their films (0-10 scale)
- **Min Rating:** Lowest-rated film
- **Max Rating:** Highest-rated film

---

## API Endpoints

### Get Statistics
```bash
GET http://localhost:5000/api/stats
```
Response:
```json
{
    "total_films": 77,
    "total_actors": 308,
    "rated_actors": 62,
    "average_actor_rating": 7.86
}
```

### Get Top 10 Actors
```bash
GET http://localhost:5000/api/top-actors
```

### Get All Actor Ratings
```bash
GET http://localhost:5000/api/actor-ratings
```

### Get All Films
```bash
GET http://localhost:5000/api/films
```

### Get Actor Details
```bash
GET http://localhost:5000/api/actor/<actor_name>
```
Example: `GET http://localhost:5000/api/actor/Al%20Pacino`

### Run Pipeline
```bash
POST http://localhost:5000/api/run-pipeline
Content-Type: application/json
```

---

## Apache Airflow

### Access Airflow UI
Navigate to http://localhost:8080/ with credentials:
- Username: admin
- Password: admin

### View DAGs
1. Click on **"DAGs"** in left sidebar
2. Look for **"actor_rating_pipeline"**
3. Click to view details

### Trigger Pipeline Manually
```bash
docker exec imdb_airflow airflow dags trigger actor_rating_pipeline
```

### Check DAG Status
```bash
docker exec imdb_airflow airflow dags list
```

### View Logs
```bash
docker logs imdb_airflow | tail -n 100
```

---

## Database Management

### Access PostgreSQL via PgAdmin
1. Go to http://localhost:5050/
2. Login: admin@admin.com / admin
3. Add server with:
   - Host: postgres (or imdb_postgres)
   - User: postgres
   - Password: postgres
   - Database: imdb_reddit

### Query Database Directly
```bash
docker exec imdb_postgres psql -U postgres -d imdb_reddit
```

### View Tables
```sql
-- List all tables
\dt

-- Count rows in each table
SELECT COUNT(*) as films FROM films;
SELECT COUNT(*) as actors FROM actors;
SELECT COUNT(*) as rated_actors FROM actor_ratings;

-- View top actors
SELECT * FROM actor_ratings ORDER BY average_rating DESC LIMIT 10;

-- View all actors with ratings
SELECT * FROM actor_ratings;
```

---

## Project Structure

```
c:\Users\msi\Desktop\projet data\DataENG\
├── docker/
│   ├── docker-compose.yml          (Main orchestration)
│   ├── init.sql                    (Database initialization)
│   ├── requirements.txt            (Python dependencies)
│   ├── dags/
│   │   ├── trending_movies_dag.py  (Airflow DAG)
│   │   ├── config.py               (Configuration)
│   │   ├── web_app.py              (Flask application)
│   │   ├── run_pipeline.py         (Manual runner)
│   │   ├── show_results.py         (Results viewer)
│   │   ├── test_project.py         (Testing guide)
│   │   ├── templates/
│   │   │   ├── actor_ratings.html  (Dashboard)
│   │   │   └── index.html          (Legacy)
│   │   └── etl/
│   │       ├── __init__.py
│   │       ├── extract.py          (IMDb scraper)
│   │       ├── load.py             (Database saver)
│   │       ├── calculate_actor_ratings.py
│   │       ├── sentiment.py        (Legacy)
│   │       └── reddit_extract.py   (Legacy)
├── TESTING_RESULTS.md              (Test report)
├── ACTOR_RATING_PIPELINE.md        (Technical docs)
├── DATABASE_TABLES_GUIDE.md        (Schema docs)
├── README.md                        (Project overview)
└── populate_actor_ratings.sql      (Data script)
```

---

## Troubleshooting

### Flask App Not Accessible
1. Verify Flask is running in container:
   ```bash
   docker exec imdb_airflow curl http://localhost:5000/api/stats
   ```
2. Check port mapping in docker-compose.yml (should have `5000:5000`)
3. Restart containers:
   ```bash
   docker-compose -f docker/docker-compose.yml restart
   ```

### Airflow DAG Not Running
1. Check if DAG is paused:
   ```bash
   docker exec imdb_airflow airflow dags list | grep actor
   ```
2. Unpause if needed:
   ```bash
   docker exec imdb_airflow airflow dags unpause actor_rating_pipeline
   ```
3. Check logs:
   ```bash
   docker logs imdb_airflow | tail -n 50
   ```

### Database Connection Issues
1. Verify PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```
2. Test connection:
   ```bash
   docker exec imdb_postgres psql -U postgres -c "SELECT 1"
   ```
3. Check database exists:
   ```bash
   docker exec imdb_postgres psql -U postgres -l
   ```

### Actor Ratings Table Empty
1. Check if table exists:
   ```bash
   docker exec imdb_postgres psql -U postgres -d imdb_reddit -c "\dt actor_ratings"
   ```
2. Run pipeline via web dashboard or Airflow UI
3. Wait 15-20 seconds for completion
4. Refresh the dashboard

---

## Key Commands

### View Container Logs
```bash
docker logs imdb_airflow -f          # Flask + Airflow logs
docker logs imdb_postgres            # Database logs
docker logs imdb_pgadmin             # PgAdmin logs
```

### Monitor Pipeline Execution
```bash
# Watch Airflow scheduler
docker logs imdb_airflow -f

# Check task status
docker exec imdb_airflow airflow tasks list actor_rating_pipeline

# View recent runs
docker exec imdb_airflow airflow dags list-runs --dag-id actor_rating_pipeline
```

### Database Backup
```bash
docker exec imdb_postgres pg_dump -U postgres imdb_reddit > backup.sql
```

### Database Restore
```bash
docker exec -i imdb_postgres psql -U postgres imdb_reddit < backup.sql
```

---

## Monitoring

### Check All Services Health
```bash
docker-compose -f docker/docker-compose.yml ps
```

### View System Resources
```bash
docker stats
```

### Check Container Details
```bash
docker inspect imdb_airflow
docker inspect imdb_postgres
```

---

## Performance Tips

1. **For Large Datasets:**
   - Increase Docker memory allocation
   - Use connection pooling (already configured)
   - Consider batch processing

2. **For Better Dashboard Performance:**
   - Use pagination for actor lists
   - Cache API responses

3. **For Faster Pipeline Execution:**
   - Parallel task execution is already enabled
   - Increase number of parallel rating tasks if needed

---

## Documentation Files

- **TESTING_RESULTS.md** - Complete test report with all verifications
- **ACTOR_RATING_PIPELINE.md** - Technical architecture and pipeline details
- **DATABASE_TABLES_GUIDE.md** - Complete database schema documentation
- **README.md** - Project overview and getting started

---

## Support

For detailed technical documentation, see **ACTOR_RATING_PIPELINE.md**

For database schema information, see **DATABASE_TABLES_GUIDE.md**

For complete test results, see **TESTING_RESULTS.md**

---

**Last Updated:** December 8, 2025
**Status:** All Systems Operational ✅
