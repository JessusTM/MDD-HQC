"""Base contracts for LLM clients used by the interaction layer."""

from abc import ABC, abstractmethod
from typing import Dict, List

from app.models.llm_contract import CimNode


class LLMInterface(ABC):
    """Defines the contract implemented by LLM clients used in interactions.

    This abstraction lets the interaction engine call different providers through the
    same analysis method.
    """

    @abstractmethod
    def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        """Analyzes iStar elements and returns the HQC evidence signals.

        This method is called by the LLM interaction engine when it needs a provider to
        infer which HQC blocks are still missing from the current input.
        """
        pass
