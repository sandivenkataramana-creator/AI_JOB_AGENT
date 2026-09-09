from sqlalchemy.orm import Session

from app.models.resume_profile import ResumeProfile


class ResumeProfileRepository:

    def get_by_resume_id(
        self,
        db: Session,
        resume_id: str,
    ) -> ResumeProfile | None:

        return (
            db.query(ResumeProfile)
            .filter(
                ResumeProfile.resume_id == resume_id
            )
            .first()
        )

    def create(
        self,
        db: Session,
        profile: ResumeProfile,
    ) -> ResumeProfile:

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    def update(
        self,
        db: Session,
        profile: ResumeProfile,
    ) -> ResumeProfile:

        db.commit()
        db.refresh(profile)

        return profile

    def delete(
        self,
        db: Session,
        profile: ResumeProfile,
    ) -> None:

        db.delete(profile)
        db.commit()


resume_profile_repository = ResumeProfileRepository()