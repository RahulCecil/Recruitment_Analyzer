from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Recruitment Analyzer API"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgrespassword@db:5432/recruitment_db"
    BACKEND_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
