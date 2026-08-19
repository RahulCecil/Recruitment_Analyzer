import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgrespassword@db:5432/recruitment_db",
)
