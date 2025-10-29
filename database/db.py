# db.py (PostgreSQL version)
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
load_dotenv()  # take environment variables from .env file

# Example: use env vars so it works locally, in Docker, and in prod
PG_USER = os.getenv("PGUSER", "app")
PG_PASS = os.getenv("PGPASSWORD", "app_password")
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = os.getenv("PGPORT", "5432")
PG_DB   = os.getenv("PGDATABASE", "app_db")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,         # helps survive network hiccups
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)  # ok for fresh DBs; use Alembic later
