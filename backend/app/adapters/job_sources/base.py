from abc import ABC, abstractmethod

from app.schemas.job_search_schema import (
    JobSearchRequest,
    JobSearchResult,
)


class JobSourceAdapter(ABC):

    @abstractmethod
    def search_jobs(
        self,
        criteria: JobSearchRequest,
    ) -> list[JobSearchResult]:
        """Search jobs from this source."""
        raise NotImplementedError