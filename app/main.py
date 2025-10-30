from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="HQC-MDD")

app.mount("/", StaticFiles(directory="app/web/static/", html=True), name="static")

# app.include_router(xml.router, prefix="/xml")
