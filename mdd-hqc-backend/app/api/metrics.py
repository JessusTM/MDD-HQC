import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas.requests import PathRequest
from app.services.artifacts.xml_service import XmlService
from app.services.metrics.istar_metrics import IstarMetricsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/cim")
async def get_cim_metrics(request: PathRequest):
    logger.info("CIM metrics requested: input_path=%s", request.path)
    try:
        xml_service = XmlService(request.path)
        istar_metrics = IstarMetricsService(xml_service).calculate()
        logger.info(
            "CIM metrics calculated successfully: input_path=%s, total_nodes=%s, total_links=%s",
            request.path, istar_metrics.get("total_nodes"), istar_metrics.get("total_links"),
        )
        return {
            "detail": "Métricas CIM calculadas",
            "input_xml": request.path,
            "metrics": {"cim": istar_metrics},
        }
    except Exception as exc:
        logger.error("CIM metrics calculation failed: input_path=%s, error=%s", request.path, exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
