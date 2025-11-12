from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime

engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/imdb_reddit')

def load_dim_film(film_data):
    df = pd.DataFrame([film_data])
    df.to_sql('dim_film', engine, if_exists='append', index=False)

def load_dim_actor(actor_data):
    df = pd.DataFrame([actor_data])
    df.to_sql('dim_actor', engine, if_exists='append', index=False)

def load_fact(fact_data):
    df = pd.DataFrame([fact_data])
    df.to_sql('fact_filmsentiment', engine, if_exists='append', index=False)
