# Recruitment Analyzer

This repository contains a Streamlit dashboard for evaluating how an LLM-based recruitment scoring tool compares with a deterministic rule-based tool.

## Architecture

- Database layer: PostgreSQL tables seeded from the provided CSVs
- Python backend layer: SQLAlchemy models and evaluation logic for summary and performance analysis
- Frontend layer: Streamlit dashboard that reads from the FastAPI backend

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

For an existing PostgreSQL volume created before the rule-score precision fix, apply
the migration once:

```text
Get-Content -Raw .\db\migrate_rule_score_precision.sql | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U postgres -d recruitment_db
```

## Data flow

- CSV files are loaded into PostgreSQL during database initialization.
- The Python service layer reads from those tables using SQLAlchemy.
- The Streamlit app calls the FastAPI endpoints to render recruitment effectiveness metrics and model comparisons.

## Notes

This keeps the stack focused on Python + PostgreSQL + Streamlit while maintaining clear separation between database access, evaluation logic, and the dashboard presentation layer.

## Validate the analysis

The report's core metrics can be independently recomputed from the source CSVs without installing extra packages:

```text
python scripts/validate_analysis.py
```

The script checks primary-key and foreign-key integrity, excludes pending decisions, and reports confusion matrices, balanced accuracy, MCC, version-level results, and both disagreement definitions.