from time import perf_counter

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.metrics import CimToPimMetricsBundle, PimToPsmMetricsBundle
from app.services.transformations import CimToPim, PimToPsm
from app.services.transformations.metrics_calculator import (
    TransformationMetricsCalculator,
)
from app.services.xml_service import XmlService


class TransformationRequest(BaseModel):
    xml_content: str


class PimToPsmMetricsContext(BaseModel):
    """Representa el contexto opcional requerido para calcular métricas arquitectónicas."""

    features_count: int | None = None
    tasks_count: int | None = None
    resources_count: int | None = None


class UvlTransformationRequest(BaseModel):
    uvl_content: str
    context_metrics: PimToPsmMetricsContext | None = None


xml_service = XmlService()
transformation_service = CimToPim()
pim_to_psm_transformation_service = PimToPsm()
metrics_calculator = TransformationMetricsCalculator()

router = APIRouter(prefix="/transformations", tags=["Transformations"])


@router.post("/cim-to-pim")
def cim_to_pim(payload: TransformationRequest):
    """Ejecuta las reglas de transformación CIM → PIM sobre el XML entregado."""

    start_time = perf_counter()

    try:
        model = xml_service.transform_frontend_xml_into_graph_structure(
            payload.xml_content
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="El XML recibido no es válido...") from exc

    result = transformation_service.transform_cim_model_to_pim_structure(model)
    duration_ms = (perf_counter() - start_time) * 1000.0
    metrics_bundle: CimToPimMetricsBundle = metrics_calculator.build_cim_to_pim_metrics_bundle(
        model,
        result,
        duration_ms,
    )
    return {
        "model": model,
        "uvl": result.to_dict(),
        "metrics": metrics_bundle.to_dict(),
    }


@router.post("/pim-to-psm")
def pim_to_psm(payload: UvlTransformationRequest):
    """Genera un diagrama Quantum-UML de clases a partir de contenido UVL."""

    content = payload.uvl_content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="El contenido UVL no puede estar vacío...")

    start_time = perf_counter()

    try:
        diagram = pim_to_psm_transformation_service.transform_uvl_content_to_plantuml_diagram(
            content
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="No fue posible interpretar el contenido UVL...") from exc

    duration_ms = (perf_counter() - start_time) * 1000.0
    feature_nodes = pim_to_psm_transformation_service.parse_feature_hierarchy_from_uvl_content(
        content
    )
    context_payload = (
        payload.context_metrics.dict() if payload.context_metrics is not None else None
    )
    metrics_bundle: PimToPsmMetricsBundle = metrics_calculator.build_pim_to_psm_metrics_bundle(
        diagram,
        duration_ms,
        feature_nodes,
        context_payload,
    )
    encoded_diagram = pim_to_psm_transformation_service.encode_diagram_to_plantuml_service_format(diagram)
    diagram_url = pim_to_psm_transformation_service.build_plantuml_diagram_url_with_format(diagram)
    return {
        "diagram": diagram,
        "encoded_diagram": encoded_diagram,
        "diagram_url": diagram_url,
        "metrics": metrics_bundle.to_dict(),
    }
