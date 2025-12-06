from fastapi import APIRouter, HTTPException, UploadFile
from app.models.uvl import UVL
from app.services.upload_service import UploadService
from app.services.transformations.cim_to_pim import CimToPim
from app.services.xml_service import XmlService

router          = APIRouter()
upload_service  = UploadService()

@router.post("/upload")
async def upload_file(file: UploadFile):
    try:
        saved_path = await upload_service.upload_file(file)
    except ValueError as exc:
        raise HTTPException(
            status_code = 400, 
            detail      = str(exc)
        )

    response = {
        "detail"    : "Archivo subido correctamente",
        "filename"  : file.filename,
        "path"      : str(saved_path),
    }
    return response 


@router.post("/transform")
async def transform(path: str):
    xml_service = XmlService(str(path))
    uvl         = UVL()
    elements    = xml_service.get_elements()
    cim_to_pim  = CimToPim(xml_service, uvl, elements)

    uvl.clear()
    cim_to_pim.apply_r1()
    cim_to_pim.apply_r2()
    cim_to_pim.apply_r3()
    cim_to_pim.apply_r4()
    cim_to_pim.apply_r5()

    response = {
        "detail"        : "Transformación CIM -> PIM completada",
        "input_xml"     : str(path),
        "output_uvl"    : str(uvl.FILE_NAME),
        "metrics"       : {},
    }
    return response
