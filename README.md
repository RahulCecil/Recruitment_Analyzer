# Recruitment Analyzer

This repository contains a Streamlit dashboard for evaluating how an LLM-based recruitment scoring tool compares with a deterministic rule-based tool.

## Architecture

- Database layer: PostgreSQL tables seeded from the provided CSVs
- Python backend layer: SQLAlchemy models and evaluation logic for summary and performance analysis
- Frontend layer: Streamlit dashboard that reads directly from PostgreSQL

## Project structure

- `Tables/` - source CSV datasets
- `db/` - PostgreSQL initialization scripts
- `backend/` - Python business logic and SQLAlchemy access layer
- `frontend/` - Streamlit dashboard

## Quick start

1. Start the database and dashboard:
   docker compose up --build
2. Open the dashboard in the browser:
   http://localhost:8501

## Data flow

- CSV files are loaded into PostgreSQL during database initialization.
- The Python service layer reads from those tables using SQLAlchemy.
- The Streamlit app uses the same SQLAlchemy layer to render recruitment effectiveness metrics and model comparisons.

## Notes

This keeps the stack focused on Python + PostgreSQL + Streamlit while maintaining clear separation between database access, evaluation logic, and the dashboard presentation layer.