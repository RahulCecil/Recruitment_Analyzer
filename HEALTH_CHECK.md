# Repository Health Check

**Date:** 2026-08-20
**Status:** Ready for submission with documented analytical limitations

## Checks Passed

- Docker Compose configuration validated successfully.
- PostgreSQL and backend containers are healthy.
- Streamlit frontend is reachable on `http://localhost:8501`.
- Backend health endpoint is reachable on `http://localhost:8000/health`.
- All dashboard API endpoints returned HTTP 200.
- Filtered segment analytics requests returned HTTP 200.
- Python sources compiled successfully with `compileall`.
- Independent CSV validation passed.
- Source dataset contains 6,000 applications, including 5,496 evaluated and 504 pending applications.
- No fresh database or backend errors appeared after the smoke tests.
- No orphaned dashboard routes or unexpected placeholder code were found.
- Working-tree whitespace validation passed.

## Database Consistency

The existing PostgreSQL volume was migrated so `applications.rule_score` now uses `NUMERIC(5,4)`, matching `db/init.sql` and the SQLAlchemy model. The migration procedure is documented in `README.md` for older database volumes.

## Known Analytical Findings

These are intentional findings in the source data, not runtime health failures:

- The rule scorer produces a Healthcare scoring collapse with zero positive predictions.
- Synthetic data contains a seniority/experience inversion.
- Job-family preference mismatches are unusually high.
- LLM scores have a negative correlation with profile completeness.

These limitations are documented in `analysis.md` and surfaced in the dashboard's anomaly view.

## Runtime URLs

- Dashboard: `http://localhost:8501`
- Backend health: `http://localhost:8000/health`
