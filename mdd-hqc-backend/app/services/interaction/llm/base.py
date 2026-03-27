from abc import ABC, abstractmethod
from typing import Dict, List

from app.models.llm_contract import CimNode


class LLMInterface(ABC):
    @abstractmethod
    def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        """
        Analiza elementos iStar y devuelve señales de evidencia para HQC_SPL.

        Entrada:
            elements: Lista de nodos CIM con `type` y `label_raw`.
        Salida:
            {
                "Functionality": bool,
                "Algorithm": bool,
                "Programming": bool,
                "Integration_model": bool,
                "Quantum_HW_constraint": bool,
                "missing": ["Lista de bloques faltantes"]
            }
        """
        pass
