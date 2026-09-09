import logging
from sqlalchemy.orm import Session

from app.adapters.job_sources.base import JobSourceAdapter
from app.models.job import Job
from app.repositories.job_repository import job_repository
from app.schemas.job_search_schema import (
    JobSearchRequest,
    JobSearchResult,
)

logger = logging.getLogger(__name__)

class JobSearchService:

    def search(
        self,
        criteria: JobSearchRequest,
        adapters: list[JobSourceAdapter],
    ) -> list[JobSearchResult]:

        results: list[JobSearchResult] = []
        seen: set[str] = set()

        for adapter in adapters:
            try:
                adapter_results = adapter.search_jobs(criteria)

            except Exception:
                logger.exception(
                    "Job source adapter failed: %s",
                    adapter.__class__.__name__,
                )
                continue

            for job in adapter_results:
                key = self._build_duplicate_key(job)

                if key in seen:
                    continue

                seen.add(key)
                results.append(job)

        return results

    def save_results(
        self,
        db: Session,
        user_id: str,
        results: list[JobSearchResult],
    ) -> list[Job]:

        saved_jobs: list[Job] = []

        for result in results:
            existing_job = None

            if result.source_url:
                existing_job = job_repository.get_by_source_url(
                    db=db,
                    user_id=user_id,
                    source_url=result.source_url,
                )

            if existing_job is None:
                existing_job = job_repository.get_by_identity(
                    db=db,
                    user_id=user_id,
                    title=result.title,
                    company=result.company,
                    location=result.location,
                )

            if existing_job:
                saved_jobs.append(existing_job)
                continue

            job = Job(
                user_id=user_id,
                title=result.title,
                company=result.company,
                location=result.location,
                description=result.description,
                source=result.source,
                source_url=result.source_url,
                min_experience_years=result.min_experience_years,
                max_experience_years=result.max_experience_years,
            )

            saved_job = job_repository.create(
                db=db,
                job=job,
            )

            saved_jobs.append(saved_job)

        return saved_jobs

    @staticmethod
    def _build_duplicate_key(
        job: JobSearchResult,
    ) -> str:

        if job.source_url:
            return f"url:{job.source_url.strip().lower()}"

        title = (job.title or "").strip().lower()
        company = (job.company or "").strip().lower()
        location = (job.location or "").strip().lower()

        return f"job:{title}|{company}|{location}"


job_search_service = JobSearchService()