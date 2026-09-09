from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:

    def create(
        self,
        db: Session,
        resume: Resume
    ) -> Resume:

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume

    def get_by_id(
        self,
        db: Session,
        resume_id: str
    ) -> Resume | None:

        return (
            db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    def get_by_user(
        self,
        db: Session,
        user_id: str
    ) -> list[Resume]:

        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .all()
        )

    def get_by_id_and_user(
        self,
        db: Session,
        resume_id: str,
        user_id: str
    ) -> Resume | None:

        return (
            db.query(Resume)
            .filter(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
            .first()
        )

    def delete(
        self,
        db: Session,
        resume: Resume
    ) -> None:

        db.delete(resume)
        db.commit()


resume_repository = ResumeRepository()