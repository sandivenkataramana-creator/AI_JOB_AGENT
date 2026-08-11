import os
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.repositories.resume_repository import resume_repository


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

        original_filename = file.filename or ""

        if not original_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        extension = os.path.splitext(
            original_filename
        )[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are allowed",
            )

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type",
            )

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

        storage_directory = os.path.join(
            "app",
            "storage",
            "resumes",
        )

        os.makedirs(
            storage_directory,
            exist_ok=True,
        )

        stored_filename = (
            f"{uuid.uuid4()}{extension}"
        )

        file_path = os.path.join(
            storage_directory,
            stored_filename,
        )

        with open(file_path, "wb") as output_file:
            output_file.write(file_data)

        resume = Resume(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size=file_size,
        )

        return resume_repository.create(
            db,
            resume,
        )


resume_service = ResumeService()