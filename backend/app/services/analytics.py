from __future__ import annotations

from decimal import Decimal
from math import sqrt
from typing import Any

from sqlalchemy import Column, Float, Integer, Numeric, String, Table, case, cast, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Application, RecruiterEvent


application_evaluations = Table(
    "view_application_evaluations",
    Base.metadata,
    Column("application_id", String(50)),
    Column("job_id", String(50)),
    Column("candidate_id", String(50)),
    Column("job_family", String(100)),
    Column("job_country", String(10)),
    Column("candidate_country", String(10)),
    Column("years_experience", Integer),
    Column("profile_completeness", Float),
    Column("llm_model_version", String(50)),
    Column("rule_score", Float),
    Column("llm_score_norm", Float),
    Column("score_delta", Float),
    Column("recruiter_decision", String(50)),
    Column("is_positive_outcome", Integer),
)


def _rounded_average(column: Any) -> Any:
    return func.round(cast(func.avg(column), Numeric(10, 3)), 3)


def _row_dict(row: Any) -> dict[str, Any]:
    values = dict(getattr(row, "_mapping", row))
    return {
        key: float(value) if isinstance(value, (Decimal, float)) else value
        for key, value in values.items()
    }


def _wilson_interval(successes: int, total: int) -> tuple[float, float]:
    if not total:
        return 0.0, 0.0
    proportion = successes / total
    z = 1.96
    denominator = 1 + z**2 / total
    centre = (proportion + z**2 / (2 * total)) / denominator
    margin = (
        z
        * sqrt(
            proportion * (1 - proportion) / total
            + z**2 / (4 * total**2)
        )
        / denominator
    )
    return max(0.0, centre - margin), min(1.0, centre + margin)


def _classification_metrics(
    db: Session, score_column: Any, extra_filters: tuple[Any, ...] = ()
) -> dict[str, Any]:
    view = application_evaluations
    statement = select(
        func.sum(
            case(((score_column >= 0.5) & (view.c.is_positive_outcome == 1), 1)),
            else_=0,
        ).label("tp"),
        func.sum(
            case(((score_column < 0.5) & (view.c.is_positive_outcome == 0), 1)),
            else_=0,
        ).label("tn"),
        func.sum(
            case(((score_column >= 0.5) & (view.c.is_positive_outcome == 0), 1)),
            else_=0,
        ).label("fp"),
        func.sum(
            case(((score_column < 0.5) & (view.c.is_positive_outcome == 1), 1)),
            else_=0,
        ).label("fn"),
    ).where(view.c.recruiter_decision.is_not(None), *extra_filters)
    row = db.execute(statement).mappings().one()
    tp = int(row["tp"] or 0)
    tn = int(row["tn"] or 0)
    fp = int(row["fp"] or 0)
    fn = int(row["fn"] or 0)
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    balanced_accuracy = (recall + specificity) / 2
    denominator = sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denominator if denominator else 0.0
    ci_low, ci_high = _wilson_interval(tp + tn, total)
    return {
        "total_applications": total,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "correct": tp + tn,
        "incorrect": fp + fn,
        "accuracy": round(accuracy, 3),
        "accuracy_ci_low": round(ci_low, 3),
        "accuracy_ci_high": round(ci_high, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "specificity": round(specificity, 3),
        "balanced_accuracy": round(balanced_accuracy, 3),
        "mcc": round(mcc, 3),
    }


def overview_kpis(db: Session) -> dict[str, Any]:
    view = application_evaluations
    rule_metrics = _classification_metrics(db, view.c.rule_score)
    llm_metrics = _classification_metrics(db, view.c.llm_score_norm)
    statement = select(
        func.count().label("total_applications"),
        _rounded_average(view.c.is_positive_outcome).label("positive_outcome_rate"),
        _rounded_average(case((view.c.score_delta > 0.4, 1), else_=0)).label(
            "large_score_gap_rate"
        ),
        _rounded_average(
            case(
                (
                    (view.c.rule_score >= 0.5)
                    != (view.c.llm_score_norm >= 0.5),
                    1,
                ),
                else_=0,
            )
        ).label("classification_disagreement_rate"),
        _rounded_average(view.c.rule_score).label("avg_rule_score"),
        _rounded_average(view.c.llm_score_norm).label("avg_llm_score"),
    ).where(view.c.recruiter_decision.is_not(None))
    result = _row_dict(db.execute(statement).mappings().one())
    result["rule_accuracy"] = rule_metrics["accuracy"]
    result["llm_accuracy"] = llm_metrics["accuracy"]
    result["rule_metrics"] = rule_metrics
    result["llm_metrics"] = llm_metrics
    return result


def overview_distributions(db: Session) -> list[dict[str, Any]]:
    view = application_evaluations
    statement = (
        select(
            view.c.recruiter_decision,
            _rounded_average(view.c.rule_score).label("avg_rule_score"),
            _rounded_average(view.c.llm_score_norm).label("avg_llm_score_norm"),
            func.count().label("application_count"),
        )
        .where(view.c.recruiter_decision.is_not(None))
        .group_by(view.c.recruiter_decision)
    )
    return [_row_dict(row) for row in db.execute(statement).mappings().all()]


def model_versions(db: Session) -> list[dict[str, Any]]:
    view = application_evaluations
    statement = (
        select(
            view.c.llm_model_version,
            func.count().label("total_apps"),
            _rounded_average(view.c.llm_score_norm).label("avg_llm_score"),
            _rounded_average(view.c.rule_score).label("avg_rule_score"),
            _rounded_average(view.c.is_positive_outcome).label("positive_outcome_rate"),
        )
        .where(view.c.recruiter_decision.is_not(None))
        .group_by(view.c.llm_model_version)
        .order_by(view.c.llm_model_version)
    )
    results = []
    for row in db.execute(statement).mappings().all():
        result = _row_dict(row)
        filters = (view.c.llm_model_version == row["llm_model_version"],)
        result["rule_accuracy"] = _classification_metrics(
            db, view.c.rule_score, filters
        )["accuracy"]
        result["llm_accuracy"] = _classification_metrics(
            db, view.c.llm_score_norm, filters
        )["accuracy"]
        results.append(result)
    return results


def _segment_filters(
    statement: Any,
    job_family: str | None,
    country: str | None,
    model_version: str | None,
    min_profile_completeness: float,
) -> Any:
    view = application_evaluations
    if job_family:
        statement = statement.where(view.c.job_family == job_family)
    if country:
        statement = statement.where(view.c.job_country == country)
    if model_version:
        normalized_version = {
            "v1": "scorer-v1",
            "v2": "scorer-v2",
        }.get(model_version, model_version)
        statement = statement.where(view.c.llm_model_version == normalized_version)
    return statement.where(
        view.c.profile_completeness >= min_profile_completeness,
        view.c.recruiter_decision.is_not(None),
    )


def segment_analytics(
    db: Session,
    job_family: str | None,
    country: str | None,
    model_version: str | None,
    min_profile_completeness: float,
) -> list[dict[str, Any]]:
    view = application_evaluations
    statement = select(
        view.c.job_family,
        func.count().label("total_apps"),
        _rounded_average(view.c.rule_score).label("avg_rule_score"),
        _rounded_average(view.c.llm_score_norm).label("avg_llm_score"),
        _rounded_average(view.c.score_delta).label("avg_disagreement_delta"),
        _rounded_average(view.c.is_positive_outcome).label("positive_outcome_rate"),
        _rounded_average(
            case((view.c.rule_score >= 0.5, 1), else_=0)
        ).label("rule_positive_rate"),
        _rounded_average(
            case((view.c.llm_score_norm >= 0.5, 1), else_=0)
        ).label("llm_positive_rate"),
        _rounded_average(
            case(
                (
                    (
                        ((view.c.rule_score >= 0.5) & (view.c.is_positive_outcome == 1))
                        | ((view.c.rule_score < 0.5) & (view.c.is_positive_outcome == 0))
                    ),
                    1,
                ),
                else_=0,
            )
        ).label("rule_accuracy"),
        _rounded_average(
            case(
                (
                    (
                        ((view.c.llm_score_norm >= 0.5) & (view.c.is_positive_outcome == 1))
                        | ((view.c.llm_score_norm < 0.5) & (view.c.is_positive_outcome == 0))
                    ),
                    1,
                ),
                else_=0,
            )
        ).label("llm_accuracy"),
    )
    statement = _segment_filters(
        statement, job_family, country, model_version, min_profile_completeness
    ).group_by(view.c.job_family).order_by(view.c.job_family)
    return [_row_dict(row) for row in db.execute(statement).mappings().all()]


def disagreements(
    db: Session,
    job_family: str | None,
    country: str | None,
    model_version: str | None,
    min_profile_completeness: float,
) -> list[dict[str, Any]]:
    view = application_evaluations
    statement = select(
        view.c.application_id,
        view.c.job_family,
        view.c.rule_score,
        view.c.llm_score_norm,
        view.c.score_delta,
        view.c.profile_completeness,
        view.c.years_experience,
        view.c.recruiter_decision,
    ).where(view.c.score_delta > 0.4)
    statement = _segment_filters(
        statement,
        job_family,
        country,
        model_version,
        min_profile_completeness,
    )
    statement = statement.order_by(view.c.score_delta.desc()).limit(50)
    return [_row_dict(row) for row in db.execute(statement).mappings().all()]


def recruiter_behavior(db: Session) -> list[dict[str, Any]]:
    statement = (
        select(
            RecruiterEvent.event_type,
            func.count(RecruiterEvent.event_id).label("total_events"),
            func.count(func.distinct(RecruiterEvent.application_id)).label(
                "unique_applications_affected"
            ),
        )
        .group_by(RecruiterEvent.event_type)
    )
    rows = db.execute(statement).mappings().all()
    total_apps = db.scalar(select(func.count()).select_from(Application)) or 0
    return [
        {
            **_row_dict(row),
            "pct_of_total_apps": round(
                row["unique_applications_affected"] / total_apps, 3
            )
            if total_apps
            else 0.0,
        }
        for row in rows
    ]