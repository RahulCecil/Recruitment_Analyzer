from __future__ import annotations

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics import (
    anomaly_metrics,
    disagreements,
    funnel_violations,
    model_versions,
    overview_distributions,
    overview_kpis,
    recruiter_behavior,
    segment_analytics,
)
from app.services.evaluation import compare_tool_performance, compute_summary

app = FastAPI(title="Recruitment Analyzer API", version="1.0.0")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/summary")
def read_summary(db: Session = Depends(get_db)) -> dict:
    return compute_summary(db)


@app.get("/api/tool-performance")
def read_tool_performance(db: Session = Depends(get_db)) -> list[dict]:
    return compare_tool_performance(db)


@app.get("/api/overview/kpis")
def read_overview_kpis(db: Session = Depends(get_db)) -> dict:
    return overview_kpis(db)


@app.get("/api/overview/distributions")
def read_overview_distributions(db: Session = Depends(get_db)) -> list[dict]:
    return overview_distributions(db)


@app.get("/api/overview/model-versions")
def read_model_versions(db: Session = Depends(get_db)) -> list[dict]:
    return model_versions(db)


@app.get("/api/segments/analytics")
def read_segment_analytics(
    job_family: str | None = None,
    country: str | None = None,
    model_version: str | None = None,
    min_profile_completeness: float = Query(0.0, ge=0.0, le=1.0),
    threshold: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
) -> list[dict]:
    return segment_analytics(
        db, job_family, country, model_version, min_profile_completeness, threshold
    )


@app.get("/api/segments/disagreements")
def read_disagreements(
    job_family: str | None = None,
    country: str | None = None,
    model_version: str | None = None,
    min_profile_completeness: float = Query(0.0, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
) -> list[dict]:
    return disagreements(
        db, job_family, country, model_version, min_profile_completeness
    )


@app.get("/api/recruiter/behavior")
def read_recruiter_behavior(db: Session = Depends(get_db)) -> list[dict]:
    return recruiter_behavior(db)


@app.get("/api/anomalies/metrics")
def read_anomaly_metrics(db: Session = Depends(get_db)) -> dict:
    return anomaly_metrics(db)


@app.get("/api/recruiter/funnel-violations")
def read_funnel_violations(db: Session = Depends(get_db)) -> dict[str, int]:
    return funnel_violations(db)
