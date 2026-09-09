from app.adapters.job_sources.base import JobSourceAdapter
from app.schemas.job_search_schema import (
    JobSearchRequest,
    JobSearchResult,
)


class MockJobSourceAdapter(JobSourceAdapter):

    def search_jobs(
        self,
        criteria: JobSearchRequest,
    ) -> list[JobSearchResult]:

        return [
            JobSearchResult(
                title="Senior Backend Developer",
                company="Test Company",
                location=criteria.location,
                description=(
                    "Python FastAPI PostgreSQL Docker "
                    "backend development"
                ),
                source="mock",
                source_url="https://example.com/jobs/1",
                min_experience_years=3,
                max_experience_years=5,
            ),
            JobSearchResult(
                title="Python Developer",
                company="Another Test Company",
                location=criteria.location,
                description=(
                    "Python Django PostgreSQL REST API"
                ),
                source="mock",
                source_url="https://example.com/jobs/2",
                min_experience_years=1,
                max_experience_years=3,
            ),
        ]