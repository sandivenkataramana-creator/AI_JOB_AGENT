import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    match_level: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    required_skills_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    preferred_skills_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    experience_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    responsibilities_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    matched_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    missing_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    strengths: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skill_gaps: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommendations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
