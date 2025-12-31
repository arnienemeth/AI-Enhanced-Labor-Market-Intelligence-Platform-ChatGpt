import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "YOUR_PASSWORD"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "job_market"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

df = pd.read_csv("remotive_jobs.csv")


df.to_sql(
    "jobs_raw",
    engine,
    if_exists="append",
    index=False
)

print(f"Loaded {len(df)} rows into jobs_raw")

