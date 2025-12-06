from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins       =["http://localhost:3000"],
    allow_credentials   =True,
    allow_methods       =["*"],
    allow_headers       =["*"],
)

app.include_router(file.router, prefix="/files")