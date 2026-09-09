from app.adapters.job_sources.base import JobSourceAdapter
from app.adapters.job_sources.mock import MockJobSourceAdapter


class JobSourceRegistry:

    def __init__(self):
        self._adapters: list[JobSourceAdapter] = []

    def register(self, adapter: JobSourceAdapter) -> None:
        self._adapters.append(adapter)

    def get_adapters(self) -> list[JobSourceAdapter]:
        return list(self._adapters)


job_source_registry = JobSourceRegistry()
job_source_registry.register(MockJobSourceAdapter())