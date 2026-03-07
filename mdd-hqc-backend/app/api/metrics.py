import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.requests import PathRequest
from app.models.istar import IstarModel
from app.services.artifacts.xml_service import XmlService
from app.services.metrics.istar_metrics import IstarMetricsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["metrics"])


def get_xml_service(request: PathRequest) -> IstarModel:
    return XmlService(request.path)


def get_istar_metrics_service(
    xml_service: Annotated[IstarModel, Depends(get_xml_service)],
) -> IstarMetricsService:
    return IstarMetricsService(xml_service)


@router.post("/cim")
async def get_cim_metrics(
    request: PathRequest,
    metrics_service: Annotated[IstarMetricsService, Depends(get_istar_metrics_service)],
):
    logger.info("CIM metrics requested: input_path=%s", request.path)
    try:
        istar_metrics = metrics_service.calculate()
        logger.info(
            "CIM metrics calculated successfully: input_path=%s, total_nodes=%s, total_links=%s",
            request.path,
            istar_metrics.get("total_nodes"),
            istar_metrics.get("total_links"),
        )
        return {
            "detail": "Métricas CIM calculadas",
            "input_xml": request.path,
            "metrics": {"cim": istar_metrics},
        }
    except Exception as exc:
        logger.error(
            "CIM metrics calculation failed: input_path=%s, error=%s",
            request.path,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
