from fastapi import APIRouter, HTTPException, UploadFile
from app.services.file_service import FileService

router          = APIRouter()
file_service    = FileService()

@router.post("/upload")
async def upload_file(file: UploadFile):
    try:
        saved_path = await file_service.upload_file(file)
    except ValueError as exc:
        raise HTTPException(
            status_code = 400, 
            detail      = str(exc)
        )

    response = {
        "detail"    : "Archivo subido correctamente",
        "filename"  : file.filename,
        "path"      : str(saved_path),
    }
    return response 
