from fastapi import APIRouter, HTTPException, UploadFile
from app.services.upload_service import UploadService

router = APIRouter(prefix="/files", tags=["files"])
upload_service = UploadService()


@router.post("/upload")
async def upload_file(file: UploadFile):
    try:
        saved_path = await upload_service.upload_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "detail": "Archivo subido correctamente",
        "filename": file.filename,
        "path": str(saved_path),
    }
