import os
import uuid

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.resume_profile import ResumeProfile

from app.repositories.resume_repository import resume_repository
from app.repositories.resume_profile_repository import (
    resume_profile_repository,
)

from app.services.resume_parser import extract_resume_text
from app.services.resume_section_parser import parse_resume_text
from app.services.skill_extractor import extract_skills_from_text


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


class ResumeService:

    async def upload_resume(
        self,
        db: Session,
        user_id: str,
        file: UploadFile,
    ) -> Resume:

        # -----------------------------------------
        # 1. Validate filename
        # -----------------------------------------

        original_filename = file.filename or ""

        if not original_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # -----------------------------------------
        # 2. Validate extension
        # -----------------------------------------

        extension = os.path.splitext(
            original_filename
        )[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are allowed",
            )

        # -----------------------------------------
        # 3. Validate content type
        # -----------------------------------------

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type",
            )

        # -----------------------------------------
        # 4. Read uploaded file
        # -----------------------------------------

        file_data = await file.read()

        file_size = len(file_data)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 5 MB",
            )

        # -----------------------------------------
        # 5. Create storage directory
        # -----------------------------------------

        storage_directory = os.path.join(
            "app",
            "storage",
            "resumes",
        )

        os.makedirs(
            storage_directory,
            exist_ok=True,
        )

        # -----------------------------------------
        # 6. Generate stored filename
        # -----------------------------------------

        stored_filename = (
            f"{uuid.uuid4()}{extension}"
        )

        file_path = os.path.join(
            storage_directory,
            stored_filename,
        )

        # -----------------------------------------
        # 7. Save physical file
        # -----------------------------------------

        with open(file_path, "wb") as output_file:
            output_file.write(file_data)

        # -----------------------------------------
        # 8. Extract resume text
        # -----------------------------------------

        try:

            extracted_text = extract_resume_text(
                file_path=file_path,
                content_type=file.content_type,
            )

        except Exception:

            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from resume",
            )

        # -----------------------------------------
        # 9. Create Resume database record
        # -----------------------------------------

        resume = Resume(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size=file_size,
            extracted_text=extracted_text,
        )

        resume = resume_repository.create(
            db,
            resume,
        )

        # -----------------------------------------
        # 10. Parse extracted resume text
        # -----------------------------------------

        try:

            parsed_data = parse_resume_text(
                extracted_text
            )
            extracted_skills = extract_skills_from_text(
                extracted_text
        )

        except Exception:

            # Remove physical file
            if os.path.exists(file_path):
                os.remove(file_path)

            # Remove resume database record
            resume_repository.delete(
                db,
                resume,
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse resume",
            )

        # -----------------------------------------
        # 11. Create ResumeProfile
        # -----------------------------------------

        profile = ResumeProfile(
            resume_id=resume.id,
            full_name=parsed_data.get("full_name"),
            email=parsed_data.get("email"),
            phone=parsed_data.get("phone"),
            location=parsed_data.get("location"),
            summary=parsed_data.get("summary"),
            skills=", ".join(extracted_skills),
            experience=parsed_data.get("experience"),
            education=parsed_data.get("education"),
            projects=parsed_data.get("projects"),
            certifications=parsed_data.get("certifications"),
        )

        resume_profile_repository.create(
            db,
            profile,
        )

        # -----------------------------------------
        # 12. Return Resume
        # -----------------------------------------

        return resume

    def get_user_resumes(
        self,
        db: Session,
        user_id: str,
    ) -> list[Resume]:

        return resume_repository.get_by_user(
            db,
            user_id,
        )

    def get_user_resume(
        self,
        db: Session,
        user_id: str,
        resume_id: str,
    ) -> Resume:

        resume = resume_repository.get_by_id_and_user(
            db,
            resume_id,
            user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        return resume

    def get_resume_text(
        self,
        db: Session,
        user_id: str,
        resume_id: str,
    ) -> Resume:

        resume = resume_repository.get_by_id_and_user(
            db,
            resume_id,
            user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        if not resume.extracted_text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume text not available",
            )

        return resume

    def download_resume(
        self,
        db: Session,
        user_id: str,
        resume_id: str,
    ):
        resume = resume_repository.get_by_id_and_user(
            db,
            resume_id,
            user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        if not os.path.exists(resume.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume file not found",
            )

        return FileResponse(
            path=resume.file_path,
            media_type=resume.content_type,
            filename=resume.original_filename,
        )

    def delete_resume(
        self,
        db: Session,
        user_id: str,
        resume_id: str,
    ) -> None:

        resume = resume_repository.get_by_id_and_user(
            db,
            resume_id,
            user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        # Delete physical file
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)

        # ResumeProfile is deleted automatically because
        # resume_profiles.resume_id has ON DELETE CASCADE.
        resume_repository.delete(
            db,
            resume,
        )


resume_service = ResumeService()