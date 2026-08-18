from __future__ import annotations

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.db.session import get_db
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
