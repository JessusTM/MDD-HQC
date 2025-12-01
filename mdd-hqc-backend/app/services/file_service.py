from pathlib import Path
from fastapi import UploadFile
import shutil

class FileService:
    BASE_DIR = Path("app/data")

    async def upload_file(self, uploaded_file : UploadFile) -> Path:
        self.validate_extension(uploaded_file.filename)
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)

        filename    = uploaded_file.filename or "model.xml"
        dest_path   = self.BASE_DIR / filename
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
        return dest_path

    def validate_extension(self, uploaded_file):
        extension = Path(uploaded_file).suffix.lower()
        if extension != ".xml":
            raise ValueError("Solo se permiten archivos .xml")
