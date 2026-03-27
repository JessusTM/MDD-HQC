from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.schemas.path import PathRequest
from app.models.llm_contract import InteractionInput, InteractionReport
from app.models.llm_contract import UvlModel
from app.services.artifacts.uvl_service import UvlService
from app.services.interaction.service import run_interaction

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/report", response_model=InteractionReport)
async def get_interaction_report(request: PathRequest):
    uvl_path = Path(request.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        uvl_dict = service.parse_uvl_to_dict(uvl_content)
        uvl_model = UvlModel(**uvl_dict)

        payload = InteractionInput(nodes=[], links=[], uvl=uvl_model)
        report = run_interaction(payload, provider="ollama")
        return report

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/functionality-names")
async def get_functionality_names(request: PathRequest):
    uvl_path = Path(request.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        subfunciones = service.extract_functionality_names(uvl_content)
        return {f"subfuncion_{i + 1}": nombre for i, nombre in enumerate(subfunciones)}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
