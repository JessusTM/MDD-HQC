from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.file import router as file_router
from app.api.metrics import router as metrics_router
from app.api.transformations import router as transformations_router
from app.core.logging.logging import setup_logging

setup_logging()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(file_router)
app.include_router(metrics_router)
app.include_router(transformations_router)
