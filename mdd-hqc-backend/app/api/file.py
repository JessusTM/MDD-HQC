import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from app.services.upload_service import UploadService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])
upload_service = UploadService()


@router.post("/upload")
async def upload_file(
    file: UploadFile, upload_service: Annotated[UploadService, Depends(UploadService)]
):
    logger.info("File upload requested: filename=%s", file.filename)
    try:
        saved_path = await upload_service.upload_file(file)
    except ValueError as exc:
        logger.warning(
            "File upload rejected: filename=%s, error=%s", file.filename, exc
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info(
        "File uploaded successfully: filename=%s, path=%s", file.filename, saved_path
    )
    return {
        "detail": "Archivo subido correctamente",
        "filename": file.filename,
        "path": str(saved_path),
    }
