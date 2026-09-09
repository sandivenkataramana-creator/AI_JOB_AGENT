import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    resume_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    projects: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    certifications: Mapped[str | None] = mapped_column(
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