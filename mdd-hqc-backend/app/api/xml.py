from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.xml_service import XmlService

class XmlPayload(BaseModel):
    content: str

xml_service = XmlService()

router = APIRouter(prefix="/xml", tags=["XML"])


@router.post("/clean")
def clean_xml(payload: XmlPayload):
    try:
        cleaned = xml_service.transform_frontend_xml_into_graph_structure(
            payload.content
        )
    except ValueError as exc:  
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return cleaned
