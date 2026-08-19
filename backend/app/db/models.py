from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    preferred_job_family: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_completeness: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    job_family: Mapped[str] = mapped_column(String(50), nullable=False)
    seniority: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class Application(Base):
    __tablename__ = "applications"

    application_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(50), ForeignKey("jobs.job_id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("candidates.candidate_id"), nullable=False
    )
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    rule_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    rule_fit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    llm_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    llm_model_version: Mapped[str] = mapped_column(String(20), nullable=False)
    recruiter_decision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    decision_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RecruiterEvent(Base):
    __tablename__ = "recruiter_events"

    event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    application_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("applications.application_id"), nullable=False
    )
    recruiter_id: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
