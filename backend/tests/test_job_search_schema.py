import pytest
from pydantic import ValidationError

from app.schemas.job_search_schema import JobSearchRequest


def test_job_search_request_rejects_min_experience_above_max():

    with pytest.raises(ValidationError):
        JobSearchRequest(
            keywords="Python",
            min_experience_years=5,
            max_experience_years=2,
        )


def test_job_search_request_accepts_valid_experience_range():

    request = JobSearchRequest(
        keywords="Python",
        min_experience_years=2,
        max_experience_years=5,
    )

    assert request.min_experience_years == 2
    assert request.max_experience_years == 5