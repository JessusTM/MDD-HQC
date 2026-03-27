import os
import requests
from typing import Dict, List

from app.models.llm_contract import CimNode
from app.services.interaction.llm.base import LLMInterface
import json
import re
import logging

logger = logging.getLogger(__name__)


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

SYSTEM_INSTRUCTIONS = (
    "Analiza los elementos UVL/iStar y responde SOLO con un JSON válido con las claves exactas: "
    "Functionality, Algorithm, Programming, Integration_model, Quantum_HW_constraint, missing.\n"
    "No uses otras claves como 'questions' o 'proposals'.\n"
    "No incluyas explicaciones, comentarios ni texto adicional fuera del JSON.\n\n"
    "Reglas de interpretación:\n"
    "- Functionality=true si existe un bloque @Functionality con metas o tareas.\n"
    "- Algorithm=true Si existe un bloque @Algorithm con cualquier tarea, marca Algorithm=true aunque no se mencionen lenguajes o frameworks..\n"
    "- Programming=true SOLO si aparecen referencias explícitas a lenguajes o frameworks (Python, Rust, Q#, etc.).\n"
    "- Integration_model=true SOLO si aparecen términos como SOA, middleware, microservicios o API REST.\n"
    "- Quantum_HW_constraint=true SOLO si aparecen restricciones técnicas explícitas de hardware cuántico (ej. qubits, shots, circuit depth, error rate, conectividad)..\n"
    "- Si no hay evidencia textual, marca false y agrega esa clave a missing.\n"
    "- La clave missing debe contener TODAS las claves que estén en false. \n"
    "- Responde SOLO con el JSON. \n"
    "No incluyas explicaciones, comentarios ni texto adicional fuera del JSON. \n"
)


def build_prompt(elements: List[CimNode]) -> str:
    lines = [f"- {element.type}: {element.label_raw}" for element in elements]
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
        "}\n\n"
        "Ejemplo 1 (UVL con @Functionality y @Algorithm, sin lenguajes ni integración):\n"
        "{\n"
        '   "Functionality": true,\n'
        '   "Algorithm": true,\n'
        '   "Programming": false,\n'
        '   "Integration_model": false,\n'
        '   "Quantum_HW_constraint": true,\n'
        '   "missing": ["Programming","Integration_model"]\n'
        "}\n\n"
        "Ejemplo 2 (UVL con referencias a Python y API REST, sin cómputo cuántico):\n"
        "{\n"
        '   "Functionality": true,\n'
        '   "Algorithm": false,\n'
        '   "Programming": true,\n'
        '   "Integration_model": true,\n'
        '   "Quantum_HW_constraint": false,\n'
        '   "missing": ["Algorithm","Quantum_HW_constraint"]\n'
        "}\n\n"
        "⚠️ Importante: No copies los ejemplos. Analiza los elementos UVL/iStar y decide cada clave en base a ellos. "
        "Responde SOLO con el JSON."
    )


class OllamaClient(LLMInterface):
    def __init__(self, model_name=OLLAMA_MODEL, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature

    def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        prompt = build_prompt(elements)
        logger.debug("Prompt enviado a Ollama:\n%s", prompt)
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "options": {"temperature": self.temperature},
                "stream": False,
            },
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("response", "").strip()
        logger.debug("Respuesta cruda de Ollama:\n%s", raw)

        parsed = self._safe_parse_json(raw)
        logger.debug("Resultado parseado:\n%s", parsed)
        return parsed

    def _safe_parse_json(self, raw: str) -> Dict:
        logger.debug("Respuesta cruda recibida:\n%s", raw)
        parsed = None
        try:
            parsed = json.loads(raw)
            logger.debug("JSON cargado directamente: %s", parsed)
        except Exception:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                logger.warning("No se encontró bloque JSON en la respuesta.")
                return {}
            try:
                parsed = json.loads(match.group(0))
                logger.debug("JSON cargado desde regex: %s", parsed)
            except Exception as e:
                logger.error("Error al parsear JSON desde regex: %s", e)
                return {}

        if not parsed:
            return {}

        keys = [
            "Functionality",
            "Algorithm",
            "Programming",
            "Integration_model",
            "Quantum_HW_constraint",
        ]

        # 👇 Aquí añades tu chequeo
        if not all(k in parsed for k in keys):
            logger.warning(
                "JSON no contiene todas las claves esperadas: %s", parsed.keys()
            )
            return {}

        result = {k: bool(parsed.get(k, False)) for k in keys}
        result["missing"] = parsed.get(
            "missing", [k for k, v in result.items() if not v]
        )
        return result
