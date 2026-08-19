from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Application
from app.services.analytics import _classification_metrics, application_evaluations


def compute_summary(db: Session) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(Application)) or 0
    evaluated = db.scalar(
        select(func.count()).where(Application.recruiter_decision.is_not(None))
    ) or 0

    hired = db.scalar(select(func.count()).where(Application.recruiter_decision == "hired")) or 0
    interviewed = db.scalar(select(func.count()).where(Application.recruiter_decision == "interviewed")) or 0
    rejected = db.scalar(select(func.count()).where(Application.recruiter_decision == "rejected")) or 0

    labeled_filter = application_evaluations.c.recruiter_decision.is_not(None)
    average_rule = db.scalar(
        select(func.avg(application_evaluations.c.rule_score)).where(labeled_filter)
    ) or 0.0
    average_llm = db.scalar(
        select(func.avg(application_evaluations.c.llm_score_norm)).where(labeled_filter)
    ) or 0.0

    return {
        "total_applications": total,
        "evaluated_applications": evaluated,
        "pending_applications": total - evaluated,
        "hired": hired,
        "interviewed": interviewed,
        "rejected": rejected,
        "average_rule_score": round(float(average_rule), 3),
        "average_llm_score": round(float(average_llm), 3),
    }


def compare_tool_performance(db: Session) -> list[dict[str, Any]]:
    stmt = (
        select(
            application_evaluations.c.llm_model_version,
            func.avg(application_evaluations.c.llm_score_norm).label("avg_llm_score"),
            func.avg(application_evaluations.c.rule_score).label("avg_rule_score"),
            func.count(application_evaluations.c.application_id).label("count"),
        )
        .where(application_evaluations.c.recruiter_decision.is_not(None))
        .group_by(application_evaluations.c.llm_model_version)
        .order_by(application_evaluations.c.llm_model_version)
    )

    rows = db.execute(stmt).mappings().all()
    results = []
    for row in rows:
        filters = (
            application_evaluations.c.llm_model_version
            == row["llm_model_version"],
        )
        results.append(
            {
                "llm_model_version": row["llm_model_version"],
                "avg_llm_score": round(float(row["avg_llm_score"] or 0.0), 3),
                "avg_rule_score": round(float(row["avg_rule_score"] or 0.0), 3),
                "rule_accuracy": _classification_metrics(
                    db, application_evaluations.c.rule_score, filters
                )["accuracy"],
                "llm_accuracy": _classification_metrics(
                    db, application_evaluations.c.llm_score_norm, filters
                )["accuracy"],
                "count": row["count"],
            }
        )
    return results
