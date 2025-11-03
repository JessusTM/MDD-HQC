from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import transformations, xml


app = FastAPI(title="HQC-MDD")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(xml.router)
app.include_router(transformations.router)
