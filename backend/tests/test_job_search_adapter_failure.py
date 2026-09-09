from app.adapters.job_sources.base import JobSourceAdapter
from app.adapters.job_sources.mock import MockJobSourceAdapter
from app.schemas.job_search_schema import JobSearchRequest, JobSearchResult
from app.services.job_search_service import job_search_service


class FailingJobSourceAdapter(JobSourceAdapter):

    def search_jobs(
        self,
        criteria: JobSearchRequest,
    ) -> list[JobSearchResult]:
        raise RuntimeError("Job source temporarily unavailable")


def test_search_continues_when_one_adapter_fails():

    criteria = JobSearchRequest(
        keywords="Python",
        location="Hyderabad",
        limit=20,
    )

    adapters = [
        FailingJobSourceAdapter(),
        MockJobSourceAdapter(),
    ]

    results = job_search_service.search(
        criteria=criteria,
        adapters=adapters,
    )

    assert len(results) == 2

    titles = {job.title for job in results}

    assert "Senior Backend Developer" in titles
    assert "Python Developer" in titles


def test_search_continues_when_adapter_after_successful_adapter_fails():

    criteria = JobSearchRequest(
        keywords="Python",
        location="Hyderabad",
        limit=20,
    )

    adapters = [
        MockJobSourceAdapter(),
        FailingJobSourceAdapter(),
    ]

    results = job_search_service.search(
        criteria=criteria,
        adapters=adapters,
    )

    assert len(results) == 2

    titles = {job.title for job in results}

    assert "Senior Backend Developer" in titles
    assert "Python Developer" in titles