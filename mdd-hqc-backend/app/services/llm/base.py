from abc import ABC, abstractmethod
from typing import List, Dict

class LLMInterface(ABC):
    @abstractmethod
    def analyze_istar_elements(self, elements: List[Dict]) -> Dict:
        """
        Analiza elementos iStar y devuelve señales de evidencia para HQC_SPL.

        Entrada:
            elements: Lista de diccionarios con {"type": str, "text": str}
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