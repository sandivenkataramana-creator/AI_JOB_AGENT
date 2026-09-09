from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobMatchResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    job_id: str
    resume_id: str

    match_score: float
    match_level: str

    required_skills_score: float | None
    preferred_skills_score: float | None
    experience_score: float | None
    responsibilities_score: float | None

    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    skill_gaps: list[str]
    recommendations: list[str]

    created_at: datetime
    updated_at: datetime


class JobMatchListResponse(BaseModel):
    matches: list[JobMatchResponse]
    total: int


class JobMatchAllResult(BaseModel):
    match_id: str
    resume_id: str
    filename: str
    match_score: float
    match_level: str
    match: dict


class JobMatchSkippedResult(BaseModel):
    resume_id: str
    filename: str
    reason: str


class JobMatchAllResponse(BaseModel):
    job_id: str
    total_resumes: int
    matched_resumes: int
    skipped_resumes: int
    results: list[JobMatchAllResult]
    skipped: list[JobMatchSkippedResult]