import requests
from typing import List, Dict
from app.services.interaction.llm.base import LLMInterface
import json
import re

LMSTUDIO_URL = "http://localhost:1234/v1/completions" 
LMSTUDIO_MODEL = "Meta-Llama-3-8B-Instruct"

class LMStudioClient(LLMInterface):
    def __init__(self, model_name = LMSTUDIO_MODEL, temperature: float = 0.0, max_tokens: int = 512):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def analyze_istar_elements(self, elements: List[Dict]) -> Dict:
        """
        Recibe elementos iStar (type + text) y devuelve señales HQC_SPL.
        """

        prompt = self._build_prompt(elements)

        resp = requests.post(
            LMSTUDIO_URL,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        raw = ""
        if isinstance(data.get("choices"), list) and data["choices"]:
            raw = (data["choices"][0].get("text") or "").strip()
        
        return self._safe_parse_json(raw)

    def _build_prompt(self, elements: List[Dict]) -> str: 
        text_elements = "\n".join([f"{el['type']}: {el['text']}" for el in elements]) 
        return ( 
            "Analiza los siguientes elementos iStar y determina si hay evidencia " 
            "para los bloques HQC_SPL (Functionality, Algorithm, Programming, " 
            "Integration_model, Quantum_HW_constraint).\n\n" 
            f"{text_elements}\n\n" 
            "Devuelve un JSON con las claves mencionadas y una lista 'missing'." 
        )
    
    def _safe_parse_json(self, raw: str) -> Dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {}
        try:
            parsed = json.loads(match.group(0))
        except Exception:
            return {}
        
        keys = [
            "Functionality",
            "Algorithm",
            "Programming",
            "Integration_model",
            "Quantum_HW_constraint",
        ]
        result = {k: bool(parsed.get(k, False)) for k in keys}
        result["missing"] = parsed.get("missing", [k for k, v in result.items() if not v])
        return result
    
    
    