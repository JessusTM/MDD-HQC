from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.models.uvl import UVL
from app.services.upload_service import UploadService
from app.services.xml_service import XmlService
from app.services.transformations.cim_to_pim import CimToPim
from app.services.transformations.pim_to_psm import PimToPsm
from app.services.plantuml_service import PlantumlService
from app.services.metrics.istar_metrics import IstarMetricsService
from app.services.metrics.uvl_metrics import UvlMetricsService
from app.services.metrics.plantuml_metrics import PlantumlMetricsService

router = APIRouter()
upload_service = UploadService()


class PathRequest(BaseModel):
    path: str


@router.post("/upload")
async def upload_file(file: UploadFile):
    try:
        saved_path = await upload_service.upload_file(file)
    except ValueError as exc:
        raise HTTPException(
            status_code = 400,
            detail      = str(exc),
        )

    response = {
        "detail"    : "Archivo subido correctamente",
        "filename"  : file.filename,
        "path"      : str(saved_path),
    }
    return response


@router.post("/metrics-cim")
async def get_cim_metrics(request: PathRequest):
    try:
        xml_service             = XmlService(str(request.path))
        elements                = xml_service.get_elements()
        istar_metrics_service   = IstarMetricsService(xml_service, elements)
        istar_metrics           = istar_metrics_service.calculate()

        response = {
            "detail"    : "Métricas CIM calculadas",
            "input_xml" : request.path,
            "metrics"   : {
                "cim": istar_metrics,
            },
        }
        return response
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/transform-cim-pim")
async def transform_cim_pim(request: PathRequest):
    xml_service = XmlService(str(request.path))
    uvl         = UVL()
    elements    = xml_service.get_elements()
    cim_to_pim  = CimToPim(xml_service, uvl, elements)

    istar_metrics_service   = IstarMetricsService(xml_service, elements)
    istar_metrics           = istar_metrics_service.calculate()

    uvl.clear()
    cim_to_pim.apply_r1()
    cim_to_pim.apply_r2()
    cim_to_pim.apply_r3()
    cim_to_pim.apply_r4()
    cim_to_pim.apply_r5()
    uvl.create_file()

    uvl_metrics_service = UvlMetricsService(uvl)
    uvl_metrics         = uvl_metrics_service.calculate()

    uvl_content = ""
    if uvl.FILE_NAME.exists():
        uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")

    response = {
        "detail"        : "Transformación CIM -> PIM completada",
        "input_xml"     : str(request.path),
        "output_uvl"    : str(uvl.FILE_NAME),
        "uvl_content"   : uvl_content,
        "metrics"       : {
            "cim"   : istar_metrics,
            "pim"   : uvl_metrics,
        },
    }
    return response


@router.post("/transform-pim-psm")
async def transform_pim_psm(request: PathRequest):
    xml_service = XmlService(str(request.path))
    uvl         = UVL()
    elements    = xml_service.get_elements()
    cim_to_pim  = CimToPim(xml_service, uvl, elements)

    istar_metrics_service   = IstarMetricsService(xml_service, elements)
    istar_metrics           = istar_metrics_service.calculate()

    uvl.clear()
    cim_to_pim.apply_r1()
    cim_to_pim.apply_r2()
    cim_to_pim.apply_r3()
    cim_to_pim.apply_r4()
    cim_to_pim.apply_r5()
    uvl.create_file()

    uvl_metrics_service = UvlMetricsService(uvl)
    uvl_metrics         = uvl_metrics_service.calculate()

    pim_to_psm          = PimToPsm(uvl)
    uml_model           = pim_to_psm.transform()

    plantuml_metrics_service    = PlantumlMetricsService(uml_model)
    plantuml_metrics            = plantuml_metrics_service.calculate()

    puml_output         = Path("app/data/model.puml")
    plantuml_service    = PlantumlService()
    puml_path           = plantuml_service.render(uml_model, puml_output)

    uvl_content         = ""
    if uvl.FILE_NAME.exists():
        uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")
    
    puml_content = ""
    if puml_path.exists():
        puml_content = puml_path.read_text(encoding="utf-8")

    response = {
        "detail"        : "Transformación PIM -> PSM completada",
        "input_xml"     : str(request.path),
        "output_uvl"    : str(uvl.FILE_NAME),
        "output_puml"   : str(puml_path),
        "uvl_content"   : uvl_content,
        "puml_content"  : puml_content,
        "metrics": {
            "cim": istar_metrics,
            "pim": uvl_metrics,
            "psm": plantuml_metrics,
        },
    }
    return response