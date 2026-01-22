from fastapi import APIRouter, HTTPException

from app.api.schemas.requests import PathRequest
from app.services.artifacts.xml_service import XmlService
from app.services.metrics.istar_metrics import IstarMetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/cim")
async def get_cim_metrics(request: PathRequest):
    try:
        xml_service = XmlService(request.path)
        istar_metrics = IstarMetricsService(xml_service).calculate()

        return {
            "detail": "Métricas CIM calculadas",
            "input_xml": request.path,
            "metrics": {"cim": istar_metrics},
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
