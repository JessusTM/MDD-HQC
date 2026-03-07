import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.uvl import UVL

from app.services.artifacts.xml_service import XmlService
from app.services.artifacts.uvl_service import UvlService
from app.services.artifacts.plantuml_service import PlantumlService

from app.services.transformations.cim_to_pim import CimToPim
from app.services.transformations.pim_to_psm import PimToPsm

from app.services.metrics.istar_metrics import IstarMetricsService
from app.services.metrics.uvl_metrics import UvlMetricsService
from app.services.metrics.uml_metrics import UmlMetricsService


class PathRequest(BaseModel):
    path: str


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transformations", tags=["transformations"])


@router.post("/cim-to-pim")
async def transform_cim_pim(request: PathRequest):
    logger.info("CIM-to-PIM transformation requested: input_path=%s", request.path)
    try:
        xml_service = XmlService(request.path)
        uvl_service = UvlService()
        uvl = UVL()

        istar_metrics = IstarMetricsService(xml_service).calculate()

        cim_to_pim = CimToPim(xml_service=xml_service, uvl_service=uvl_service, uvl=uvl)
        cim_to_pim.apply_r1()
        cim_to_pim.apply_r2()
        cim_to_pim.apply_r3()
        cim_to_pim.apply_r4()
        cim_to_pim.apply_r5()
        uvl.create_file()

        uvl_metrics = UvlMetricsService(uvl).calculate()

        uvl_content = ""
        if uvl.FILE_NAME.exists():
            uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")

        logger.info(
            "CIM-to-PIM transformation completed: input_path=%s, output_uvl=%s, features=%s",
            request.path,
            uvl.FILE_NAME,
            uvl_metrics.get("total_features"),
        )
        return {
            "detail": "Transformación CIM -> PIM completada",
            "input_xml": request.path,
            "output_uvl": str(uvl.FILE_NAME),
            "uvl_content": uvl_content,
            "metrics": {"cim": istar_metrics, "pim": uvl_metrics},
        }
    except Exception as exc:
        logger.error(
            "CIM-to-PIM transformation failed: input_path=%s, error=%s",
            request.path,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pim-to-psm")
async def transform_pim_psm(request: PathRequest):
    logger.info("PIM-to-PSM transformation requested: input_path=%s", request.path)
    try:
        xml_service = XmlService(request.path)
        uvl_service = UvlService()
        uvl = UVL()

        istar_metrics = IstarMetricsService(xml_service).calculate()

        cim_to_pim = CimToPim(xml_service=xml_service, uvl_service=uvl_service, uvl=uvl)
        cim_to_pim.apply_r1()
        cim_to_pim.apply_r2()
        cim_to_pim.apply_r3()
        cim_to_pim.apply_r4()
        cim_to_pim.apply_r5()
        uvl.create_file()

        uvl_metrics = UvlMetricsService(uvl).calculate()

        pim_to_psm = PimToPsm(uvl)
        uml_model = pim_to_psm.transform()

        uml_metrics = UmlMetricsService(uml_model).calculate()

        uml_output = Path("data/model.puml")
        plantuml_service = PlantumlService()
        uml_path = plantuml_service.write(uml_model, uml_output)

        uvl_content = ""
        if uvl.FILE_NAME.exists():
            uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")

        uml_content = ""
        if uml_path.exists():
            uml_content = uml_path.read_text(encoding="utf-8")

        logger.info(
            "PIM-to-PSM transformation completed: input_path=%s, output_uvl=%s, output_puml=%s, classes=%s",
            request.path,
            uvl.FILE_NAME,
            uml_path,
            uml_metrics.get("total_classes"),
        )
        return {
            "detail": "Transformación PIM -> PSM completada",
            "input_xml": request.path,
            "output_uvl": str(uvl.FILE_NAME),
            "output_puml": str(uml_path),
            "uvl_content": uvl_content,
            "puml_content": uml_content,
            "metrics": {
                "cim": istar_metrics,
                "pim": uvl_metrics,
                "psm": uml_metrics,
            },
        }
    except Exception as exc:
        logger.error(
            "PIM-to-PSM transformation failed: input_path=%s, error=%s",
            request.path,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
