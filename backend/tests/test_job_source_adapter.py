import pytest

from app.adapters.job_sources.base import JobSourceAdapter
from app.schemas.job_search_schema import JobSearchRequest


class TestAdapter(JobSourceAdapter):

    def search_jobs(
        self,
        criteria: JobSearchRequest,
    ):
        return []


def test_job_source_adapter_can_be_implemented():
    adapter = TestAdapter()

    criteria = JobSearchRequest(
        keywords="Python",
        location="Hyderabad",
    )

    result = adapter.search_jobs(criteria)

    assert result == []