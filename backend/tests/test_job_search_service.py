from app.adapters.job_sources.base import JobSourceAdapter
from app.adapters.job_sources.mock import MockJobSourceAdapter
from app.schemas.job_search_schema import (
    JobSearchRequest,
    JobSearchResult,
)
from app.services.job_search_service import JobSearchService


class DuplicateJobAdapter(JobSourceAdapter):

    def search_jobs(
        self,
        criteria: JobSearchRequest,
    ) -> list[JobSearchResult]:

        return [
            JobSearchResult(
                title="Senior Backend Developer",
                company="Test Company",
                location="Hyderabad",
                description="Python FastAPI PostgreSQL Docker",
                source="another_source",
                source_url="https://example.com/jobs/1",
                min_experience_years=3,
                max_experience_years=5,
            ),
        ]


def test_job_search_service_combines_adapter_results():

    service = JobSearchService()

    criteria = JobSearchRequest(
        keywords="Python FastAPI",
        location="Hyderabad",
        min_experience_years=0,
        max_experience_years=5,
        limit=20,
    )

    adapter = MockJobSourceAdapter()

    results = service.search(
        criteria=criteria,
        adapters=[adapter],
    )

    assert len(results) == 2
    assert results[0].title == "Senior Backend Developer"
    assert results[1].title == "Python Developer"


def test_job_search_service_removes_duplicate_urls():

    service = JobSearchService()

    criteria = JobSearchRequest(
        keywords="Python",
        location="Hyderabad",
    )

    results = service.search(
        criteria=criteria,
        adapters=[
            MockJobSourceAdapter(),
            DuplicateJobAdapter(),
        ],
    )

    assert len(results) == 2

    urls = [job.source_url for job in results]

    assert urls.count("https://example.com/jobs/1") == 1


def test_duplicate_without_url_uses_title_company_location():

    service = JobSearchService()

    job1 = JobSearchResult(
        title="Python Developer",
        company="Test Company",
        location="Hyderabad",
        description="First description",
        source="source_a",
    )

    job2 = JobSearchResult(
        title=" python developer ",
        company=" test company ",
        location=" HYDERABAD ",
        description="Different description",
        source="source_b",
    )

    key1 = service._build_duplicate_key(job1)
    key2 = service._build_duplicate_key(job2)

    assert key1 == key2