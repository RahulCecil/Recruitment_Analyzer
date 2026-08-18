from __future__ import annotations

from sqlalchemy import Boolean, Float, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    years_experience: Mapped[int | None] = mapped_column(nullable=True)
    preferred_job_family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_completeness: Mapped[float | None] = mapped_column(Float, nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    job_family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Application(Base):
    __tablename__ = "applications"

    application_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    job_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    candidate_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rule_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rule_fit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    llm_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    llm_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recruiter_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    decision_at: Mapped[str | None] = mapped_column(String(50), nullable=True)


class RecruiterEvent(Base):
    __tablename__ = "recruiter_events"

    event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    application_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recruiter_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    event_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
