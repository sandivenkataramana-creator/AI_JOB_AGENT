from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    file_size: int
    created_at: datetime
    extracted_text: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ResumeTextResponse(BaseModel):
    resume_id: str
    filename: str
    extracted_text: str