from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.api.schemas.requests import PathRequest
from app.models.llm_contract import InteractionInput, InteractionReport
from app.services.artifacts.uvl_service import UvlService
from app.models.uvl import UVL
from app.services.interaction.service import run_interaction
from app.models.llm_contract import UvlModel

router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post("/interaction/report", response_model=InteractionReport)
async def analyze_uvl(request: PathRequest):
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
