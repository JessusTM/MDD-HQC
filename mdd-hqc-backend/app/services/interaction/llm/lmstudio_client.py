"""LM Studio client used to infer missing HQC evidence from iStar elements."""

import requests
from typing import Dict, List

from app.models.llm_contract import CimNode
from app.services.interaction.llm.base import LLMInterface
import json
import re

LMSTUDIO_URL = "http://localhost:1234/v1/completions"
LMSTUDIO_MODEL = "Meta-Llama-3-8B-Instruct"


class LMStudioClient(LLMInterface):
    """Calls LM Studio to analyze iStar elements for the interaction workflow.

    This client adapts the backend interaction contract to the LM Studio completion API
    so missing HQC blocks can be inferred from the source CIM labels.
    """

    def __init__(
        self, model_name=LMSTUDIO_MODEL, temperature: float = 0.0, max_tokens: int = 512
    ):
        """Initializes the LM Studio client with the configured generation settings.

        These settings control how the backend queries LM Studio during one interaction
        analysis pass.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        """Analyzes the provided iStar elements and returns the HQC evidence signals.

        This method is used by the interaction engine when LM Studio is the selected
        provider for detecting missing HQC blocks.
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

    def _build_prompt(self, elements: List[CimNode]) -> str:
        """Builds the prompt sent to LM Studio for one interaction request.

        This helper prepares the textual context that tells the model how to classify the
        current iStar evidence into HQC categories.
        """
        text_elements = "\n".join(
            [f"{element.type}: {element.label_raw}" for element in elements]
        )
        return (
            "Analiza los siguientes elementos iStar y determina si hay evidencia "
            "para los bloques HQC_SPL (Functionality, Algorithm, Programming, "
            "Integration_model, Quantum_HW_constraint).\n\n"
            f"{text_elements}\n\n"
            "Devuelve un JSON con las claves mencionadas y una lista 'missing'."
        )

    def _safe_parse_json(self, raw: str) -> Dict:
        """Extracts the expected JSON object from the LM Studio raw response.

        This helper keeps the interaction flow resilient when the provider returns extra
        text around the JSON payload expected by the backend.
        """
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
        result["missing"] = parsed.get(
            "missing", [k for k, v in result.items() if not v]
        )
        return result
