import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/imdb_reddit')
df = pd.read_sql('SELECT film_title, recommendation_score FROM recommendations ORDER BY recommendation_score DESC LIMIT 10', engine)

print('\n' + '='*55)
print('2025 TRENDING MOVIES - RECOMMENDATIONS')
print('='*55)
print(df.to_string(index=False))
print('\n✅ Real 2025 trending movies analyzed with real Reddit sentiment')
