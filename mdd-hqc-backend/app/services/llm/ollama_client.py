import requests
from typing import List, Dict
from app.services.llm.base import LLMInterface
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "devstral-small-2"

SYSTEM_INSTRUCTIONS = ( 
    "Eres un clasificador. Dado texto de elementos iStar (type, text), " 
    "indica si hay evidencia suficiente para poblar los bloques HQC_SPL: " 
    "Functionality, Algorithm, Programming, Integration_model, Quantum_HW_constraint. " 
    "Responde SOLO en JSON con claves booleanas y 'missing' como lista." 
)

def build_prompt(elements: List[Dict]) -> str:
    lines = [f"- {el.get('type', 'unknown')}: {el.get('text','')}" for el in elements]
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        "Elementos iStar:\n" + "\n".join(lines) + "\n\n"
        "Formato de salida:\n"
        "{\n"
        '   "Functionality": true|false,\n'
        '   "Algorithm": true|false,\n'
        '   "Programming": true|false,\n'
        '   "Integration_model": true|false,\n'
        '   "Quantum_HW_constraint": true|false,\n'
        '   "missing": ["..."]\n'
        "}\n"
        "No inventes decisiones: si no hay evidencia, marca false y agrega a missing."
    )

class OllamaClient(LLMInterface):
    def __init__(self, model_name = OLLAMA_MODEL, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
    
    def analyze_istar_elements(self, elements: List[Dict]) -> Dict:
        prompt = build_prompt(elements)
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "options": {"temperature": self.temperature},
                "stream": False
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("response", "").strip()
        return self._safe_parse_json(raw)
    
    def _safe_parse_json(self, raw: str) -> Dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return self._fallback_empty()
        try:
            parsed = json.loads(match.group(0))
        except Exception:
            return self._fallback_empty()
        
        keys = [
            "Functionality", "Algorithm", "Programming",
            "Integration_model", "Quantum_HW_constraint"
        ]
        result = {k: bool(parsed.get(k, False)) for k in keys}
        missing = [k for k, v in result.items() if not v]
        result["missing"] = parsed.get("missing", missing)
        return result
    
    def _fallback_empty(self) -> Dict:
        return {
            "Functionality": False,
            "Algorithm": False,
            "Programming": False,
            "Integration_model": False,
            "Quantum_HW_constraint": False,
            "missing": [
                "Functionality", "Algorithm", "Programming",
                "Integration_model", "Quantum_HW_constraint"
            ]
        }

