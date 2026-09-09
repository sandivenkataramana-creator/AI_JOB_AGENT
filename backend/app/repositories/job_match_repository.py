from sqlalchemy.orm import Session

from app.models.job_match import JobMatch


class JobMatchRepository:

    def create(
        self,
        db: Session,
        job_match: JobMatch,
    ) -> JobMatch:

        db.add(job_match)
        db.commit()
        db.refresh(job_match)

        return job_match

    def get_by_id(
        self,
        db: Session,
        match_id: str,
    ) -> JobMatch | None:

        return (
            db.query(JobMatch)
            .filter(JobMatch.id == match_id)
            .first()
        )

    def get_by_job_and_resume(
        self,
        db: Session,
        job_id: str,
        resume_id: str,
    ) -> JobMatch | None:

        return (
            db.query(JobMatch)
            .filter(
                JobMatch.job_id == job_id,
                JobMatch.resume_id == resume_id,
            )
            .first()
        )

    def get_all_by_job(
        self,
        db: Session,
        job_id: str,
    ) -> list[JobMatch]:

        return (
            db.query(JobMatch)
            .filter(JobMatch.job_id == job_id)
            .order_by(JobMatch.match_score.desc())
            .all()
        )

    def get_all_by_resume(
        self,
        db: Session,
        resume_id: str,
    ) -> list[JobMatch]:

        return (
            db.query(JobMatch)
            .filter(JobMatch.resume_id == resume_id)
            .order_by(JobMatch.match_score.desc())
            .all()
        )

    def delete(
        self,
        db: Session,
        job_match: JobMatch,
    ) -> None:

        db.delete(job_match)
        db.commit()


job_match_repository = JobMatchRepository()
