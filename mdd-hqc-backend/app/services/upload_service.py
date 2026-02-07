import logging
import shutil
from pathlib import Path

from fastapi import UploadFile

logger = logging.getLogger(__name__)


class UploadService:
    BASE_DIR = Path("app/data")

    async def upload_file(self, uploaded_file: UploadFile) -> Path:
        self.validate_extension(uploaded_file.filename)
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)

        filename = uploaded_file.filename or "model.xml"
        dest_path = self.BASE_DIR / filename
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
        logger.info("File saved to disk: path=%s", dest_path)
        return dest_path

    def validate_extension(self, uploaded_file):
        extension = Path(uploaded_file).suffix.lower()
        if extension != ".xml":
            logger.warning("Upload rejected: only .xml files allowed, got extension=%s", extension)
            raise ValueError("Solo se permiten archivos .xml")
