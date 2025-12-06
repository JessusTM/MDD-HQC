from fastapi import FastAPI
from app.api import file

app = FastAPI()

app.include_router(file.router, prefix="/files")
