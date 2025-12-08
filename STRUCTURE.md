# Project Structure - Cleaned & Organized

## Directory Layout

```
DataENG/
├── docker/                 # Docker configuration
│   ├── docker-compose.yml  # Container orchestration
│   ├── init.sql            # Database initialization
│   ├── requirements.txt     # Python dependencies
│   ├── dags/               # Working DAGs folder (for development)
│   │   ├── config.py
│   │   ├── run_pipeline.py
│   │   ├── web_app.py
│   │   ├── show_results.py
│   │   ├── test_project.py
│   │   ├── etl/
│   │   │   ├── extract.py
│   │   │   ├── reddit_extract.py
│   │   │   ├── sentiment.py
│   │   │   ├── load.py
│   │   │   └── __init__.py
│   │   └── templates/
│   │       └── index.html
│   └── etl/                # Docker ETL modules
│
├── dags/                   # Airflow DAGs (mounted in Airflow container)
│   ├── config.py
│   ├── trending_movies_dag.py
│   ├── run_pipeline.py
│   ├── web_app.py
│   ├── show_results.py
│   ├── test_project.py
│   ├── etl/               # Copy of ETL modules
│   └── templates/
│
├── .git/
├── .github/
├── images/
├── pdfs/
├── LICENSE
├── README.md
└── config.py (removed - duplicate)
```

## Why We Have `/docker/dags/` and `/dags/`

- **`/docker/dags/`** - Main development folder with all code
  - Used by: Python scripts, Flask web app
  - Runs: `python run_pipeline.py`

- **`/dags/`** - Copy for Airflow container
  - Used by: Apache Airflow scheduler
  - Docker mounts this to `/opt/airflow/dags`
  - Allows Airflow to see and run the DAG

## What Was Removed

✓ Duplicate `config.py` at root level
✓ Empty `etl/` folder at root level
✓ Old `dags/` folder with incomplete copies

## How to Use

### Run Pipeline Directly
```bash
cd docker/dags
python run_pipeline.py
```

### View Results Dashboard
```bash
cd docker/dags
python web_app.py
# Visit http://localhost:5000
```

### Run via Airflow
1. Go to http://localhost:8080
2. Find "trending_movies_pipeline" DAG
3. Click "Trigger DAG"

## Services

- **PostgreSQL** - http://localhost:5432
- **PgAdmin** - http://localhost:5050 (admin@admin.com / admin)
- **Airflow** - http://localhost:8080 (admin / admin)
- **Web Dashboard** - http://localhost:5000
