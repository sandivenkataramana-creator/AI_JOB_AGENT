from pydantic import BaseModel, Field, model_validator


class JobSearchRequest(BaseModel):
    keywords: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    min_experience_years: int | None = Field(
        default=None,
        ge=0,
    )

    max_experience_years: int | None = Field(
        default=None,
        ge=0,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    @model_validator(mode="after")
    def validate_experience_range(self):
        if (
            self.min_experience_years is not None
            and self.max_experience_years is not None
            and self.min_experience_years > self.max_experience_years
        ):
            raise ValueError(
                "min_experience_years cannot be greater than max_experience_years"
            )

        return self

class JobSearchResult(BaseModel):
    title: str
    company: str | None = None
    location: str | None = None
    description: str
    source: str
    source_url: str | None = None
    min_experience_years: int | None = None
    max_experience_years: int | None = None

class JobSearchResponse(BaseModel):
    jobs: list[JobSearchResult]
    saved_jobs: int
    total: int