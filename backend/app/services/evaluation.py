from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Application


def compute_summary(db: Session) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(Application)) or 0

    hired = db.scalar(select(func.count()).where(Application.recruiter_decision == "hired")) or 0
    interviewed = db.scalar(select(func.count()).where(Application.recruiter_decision == "interviewed")) or 0
    rejected = db.scalar(select(func.count()).where(Application.recruiter_decision == "rejected")) or 0

    average_rule = db.scalar(select(func.avg(Application.rule_score))) or 0.0
    average_llm = db.scalar(select(func.avg(Application.llm_score))) or 0.0

    return {
        "total_applications": total,
        "hired": hired,
        "interviewed": interviewed,
        "rejected": rejected,
        "average_rule_score": round(float(average_rule), 3),
        "average_llm_score": round(float(average_llm), 3),
    }


def compare_tool_performance(db: Session) -> list[dict[str, Any]]:
    stmt = (
        select(
            Application.llm_model_version,
            func.avg(Application.llm_score).label("avg_llm_score"),
            func.avg(Application.rule_score).label("avg_rule_score"),
            func.count(Application.application_id).label("count"),
        )
        .group_by(Application.llm_model_version)
        .order_by(Application.llm_model_version)
    )

    rows = db.execute(stmt).mappings().all()
    return [
        {
            "llm_model_version": row["llm_model_version"],
            "avg_llm_score": round(float(row["avg_llm_score"] or 0.0), 3),
            "avg_rule_score": round(float(row["avg_rule_score"] or 0.0), 3),
            "count": row["count"],
        }
        for row in rows
    ]
