from app.services.skill_extractor import extract_skills_from_text


def test_extract_common_skills():
    text = """
    Python, FastAPI, Docker, PostgreSQL, Redis and AWS.
    """

    skills = extract_skills_from_text(text)

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills
    assert "PostgreSQL" in skills
    assert "Redis" in skills
    assert "AWS" in skills


def test_extract_skills_is_case_insensitive():
    text = """
    PYTHON
    fastapi
    Docker
    POSTGRESQL
    """

    skills = extract_skills_from_text(text)

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills
    assert "PostgreSQL" in skills


def test_duplicate_skills_are_removed():
    text = """
    Python Python PYTHON
    PostgreSQL postgres postgresql
    """

    skills = extract_skills_from_text(text)

    assert skills.count("Python") == 1
    assert skills.count("PostgreSQL") == 1