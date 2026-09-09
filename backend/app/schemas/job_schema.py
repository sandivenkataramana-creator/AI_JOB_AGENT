from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str | None = Field(
        default=None,
        max_length=255,
    )
    location: str | None = Field(
        default=None,
        max_length=255,
    )
    description: str = Field(..., min_length=1)
    source: str | None = Field(
        default=None,
        max_length=100,
    )
    source_url: str | None = Field(
        default=None,
        max_length=1000,
    )
    min_experience_years: int | None = Field(
        default=None,
        ge=0,
    )
    max_experience_years: int | None = Field(
        default=None,
        ge=0,
    )


class JobUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    company: str | None = Field(
        default=None,
        max_length=255,
    )
    location: str | None = Field(
        default=None,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        min_length=1,
    )
    source: str | None = Field(
        default=None,
        max_length=100,
    )
    source_url: str | None = Field(
        default=None,
        max_length=1000,
    )
    min_experience_years: int | None = Field(
        default=None,
        ge=0,
    )
    max_experience_years: int | None = Field(
        default=None,
        ge=0,
    )


class JobResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    user_id: str
    title: str
    company: str | None
    location: str | None
    description: str
    source: str | None
    source_url: str | None
    min_experience_years: int | None
    max_experience_years: int | None
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
