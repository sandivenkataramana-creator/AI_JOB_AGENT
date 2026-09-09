from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeProfileResponse(BaseModel):
    id: str
    resume_id: str
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: str | None = None
    experience: str | None = None
    education: str | None = None
    projects: str | None = None
    certifications: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)