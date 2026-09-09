from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories.job_repository import job_repository
from app.schemas.job_schema import JobCreate, JobUpdate


class JobService:

    def create_job(
        self,
        db: Session,
        user_id: str,
        data: JobCreate,
    ) -> Job:

        self._validate_experience_range(
            data.min_experience_years,
            data.max_experience_years,
        )

        job = Job(
            user_id=user_id,
            title=data.title,
            company=data.company,
            location=data.location,
            description=data.description,
            source=data.source,
            source_url=data.source_url,
            min_experience_years=data.min_experience_years,
            max_experience_years=data.max_experience_years,
        )

        return job_repository.create(
            db,
            job,
        )

    def get_job(
        self,
        db: Session,
        user_id: str,
        job_id: str,
    ) -> Job:

        job = job_repository.get_by_id_and_user(
            db,
            job_id,
            user_id,
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        return job

    def get_jobs(
        self,
        db: Session,
        user_id: str,
    ) -> list[Job]:

        return job_repository.get_all_by_user(
            db,
            user_id,
        )

    def update_job(
        self,
        db: Session,
        user_id: str,
        job_id: str,
        data: JobUpdate,
    ) -> Job:

        job = self.get_job(
            db,
            user_id,
            job_id,
        )

        self._validate_experience_range(
            data.min_experience_years,
            data.max_experience_years,
            current_min=job.min_experience_years,
            current_max=job.max_experience_years,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(job, field, value)

        return job_repository.update(
            db,
            job,
        )

    def delete_job(
        self,
        db: Session,
        user_id: str,
        job_id: str,
    ) -> None:

        job = self.get_job(
            db,
            user_id,
            job_id,
        )

        job_repository.delete(
            db,
            job,
        )

    @staticmethod
    def _validate_experience_range(
        min_years: int | None,
        max_years: int | None,
        current_min: int | None = None,
        current_max: int | None = None,
    ) -> None:

        if min_years is None:
            min_years = current_min

        if max_years is None:
            max_years = current_max

        if (
            min_years is not None
            and max_years is not None
            and min_years > max_years
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Minimum experience years cannot be "
                    "greater than maximum experience years."
                ),
            )


job_service = JobService()
