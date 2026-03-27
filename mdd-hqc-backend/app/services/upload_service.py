import logging
import shutil
from pathlib import Path
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class UploadService:
    """Stores uploaded XML models on disk so they can be processed later."""

    BASE_DIR = Path("data")

    async def upload_file(self, uploaded_file: UploadFile) -> Path:
        """Validates one uploaded XML file and writes it into the local data directory."""
        self.validate_extension(uploaded_file.filename)
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)

        filename = uploaded_file.filename or "model.xml"
        dest_path = self.BASE_DIR / filename
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
        logger.info("File saved to disk: path=%s", dest_path)
        return dest_path

    def validate_extension(self, uploaded_file):
        """Rejects uploaded files whose extension is different from `.xml`."""
        extension = Path(uploaded_file).suffix.lower()
        if extension != ".xml":
            logger.warning(
                "Upload rejected: only .xml files allowed, got extension=%s", extension
            )
            raise ValueError("Solo se permiten archivos .xml")
