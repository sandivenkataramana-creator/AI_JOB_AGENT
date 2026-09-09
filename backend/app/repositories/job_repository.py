from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:

    def create(
        self,
        db: Session,
        job: Job,
    ) -> Job:

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    def get_by_id(
        self,
        db: Session,
        job_id: str,
    ) -> Job | None:

        return (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    def get_by_id_and_user(
        self,
        db: Session,
        job_id: str,
        user_id: str,
    ) -> Job | None:

        return (
            db.query(Job)
            .filter(
                Job.id == job_id,
                Job.user_id == user_id,
            )
            .first()
        )

    def get_all_by_user(
        self,
        db: Session,
        user_id: str,
    ) -> list[Job]:

        return (
            db.query(Job)
            .filter(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .all()
        )

    def get_by_source_url(
        self,
        db: Session,
        user_id: str,
        source_url: str,
    ) -> Job | None:

        return (
            db.query(Job)
            .filter(
                Job.user_id == user_id,
                Job.source_url == source_url,
            )
            .first()
        )

    def get_by_identity(
        self,
        db: Session,
        user_id: str,
        title: str,
        company: str | None,
        location: str | None,
    ) -> Job | None:

        query = (
            db.query(Job)
            .filter(
                Job.user_id == user_id,
                Job.title == title,
            )
        )

        if company is None:
            query = query.filter(Job.company.is_(None))
        else:
            query = query.filter(Job.company == company)

        if location is None:
            query = query.filter(Job.location.is_(None))
        else:
            query = query.filter(Job.location == location)

        return query.first()

    def update(
        self,
        db: Session,
        job: Job,
    ) -> Job:

        db.commit()
        db.refresh(job)

        return job

    def delete(
        self,
        db: Session,
        job: Job,
    ) -> None:

        db.delete(job)
        db.commit()


job_repository = JobRepository()
