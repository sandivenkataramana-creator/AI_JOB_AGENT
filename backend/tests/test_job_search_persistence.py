from app.database.database import SessionLocal
from app.models.job import Job
from app.models.user import User
from app.schemas.job_search_schema import JobSearchResult
from app.services.job_search_service import job_search_service


def test_save_results_creates_and_reuses_jobs():
    db = SessionLocal()

    user = User(
        full_name="Job Search Test User",
        email="job-search-test@example.com",
        password_hash="test-password-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        results = [
            JobSearchResult(
                title="Test Python Developer",
                company="Test Search Company",
                location="Hyderabad",
                description="Python PostgreSQL FastAPI",
                source="test",
                source_url="https://example.com/test-job-1",
                min_experience_years=1,
                max_experience_years=3,
            )
        ]

        first_save = job_search_service.save_results(
            db=db,
            user_id=user.id,
            results=results,
        )

        assert len(first_save) == 1
        assert first_save[0].title == "Test Python Developer"

        first_job_id = first_save[0].id

        second_save = job_search_service.save_results(
            db=db,
            user_id=user.id,
            results=results,
        )

        assert len(second_save) == 1
        assert second_save[0].id == first_job_id

        jobs = (
            db.query(Job)
            .filter(Job.user_id == user.id)
            .all()
        )

        assert len(jobs) == 1

    finally:
        db.query(Job).filter(Job.user_id == user.id).delete(
            synchronize_session=False
        )

        db.delete(user)
        db.commit()
        db.close()