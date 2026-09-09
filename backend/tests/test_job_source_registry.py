from app.adapters.job_sources.mock import MockJobSourceAdapter
from app.adapters.job_sources.registry import JobSourceRegistry


def test_registry_returns_registered_adapters():
    registry = JobSourceRegistry()

    registry.register(MockJobSourceAdapter())

    adapters = registry.get_adapters()

    assert len(adapters) == 1
    assert isinstance(adapters[0], MockJobSourceAdapter)


def test_registry_starts_empty():
    registry = JobSourceRegistry()

    assert registry.get_adapters() == []