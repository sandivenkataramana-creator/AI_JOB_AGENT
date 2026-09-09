from fastapi.testclient import TestClient

from main import app
from app.database.database import SessionLocal
from app.models.job import Job
from app.models.user import User


client = TestClient(app)


def test_job_search_api_authenticated():
    email = "job-search-api-test@example.com"
    password = "TestPassword@123"

    # Clean up any previous test user
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        db.delete(existing_user)
        db.commit()

    db.close()

    # Register user
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Job Search API Test",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    # Login user
    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Call protected job search endpoint
    search_response = client.post(
        "/jobs/search",
        json={
            "keywords": "Python",
            "location": "Hyderabad",
            "limit": 20,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert search_response.status_code == 200

    data = search_response.json()

    assert "jobs" in data
    assert "saved_jobs" in data
    assert "total" in data

    assert data["total"] == 2
    assert data["saved_jobs"] == 2

    assert len(data["jobs"]) == 2

    assert data["jobs"][0]["title"] == "Senior Backend Developer"
    assert data["jobs"][0]["source"] == "mock"

    assert data["jobs"][1]["title"] == "Python Developer"
    assert data["jobs"][1]["source"] == "mock"

    # Verify jobs were actually persisted to PostgreSQL
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()
    assert user is not None

    jobs = db.query(Job).filter(Job.user_id == user.id).all()

    assert len(jobs) == 2

    db.delete(user)
    db.commit()
    db.close()