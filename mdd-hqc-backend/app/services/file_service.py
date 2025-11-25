from fastapi import UploadFile

class FileService:
    async def upload_file(self, uploaded_file : UploadFile):
        content = await uploaded_file.read()


