from app.adapters.job_sources.mock import MockJobSourceAdapter
from app.schemas.job_search_schema import JobSearchRequest


def test_mock_job_source_returns_normalized_jobs():
    adapter = MockJobSourceAdapter()

    criteria = JobSearchRequest(
        keywords="Python FastAPI",
        location="Hyderabad",
        min_experience_years=0,
        max_experience_years=5,
        limit=20,
    )

    results = adapter.search_jobs(criteria)

    assert len(results) == 2

    assert results[0].title == "Senior Backend Developer"
    assert results[0].company == "Test Company"
    assert results[0].source == "mock"
    assert results[0].source_url == "https://example.com/jobs/1"

    assert results[1].title == "Python Developer"
    assert results[1].source == "mock"