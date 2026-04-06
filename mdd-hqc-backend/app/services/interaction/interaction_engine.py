"""Interaction engine contracts used by clarification workflows."""

from typing import Protocol
from app.models.llm_contract import InteractionInput, InteractionReport


class InteractionEngine(Protocol):
    """Defines the contract for interaction engines used by the clarification flow.

    This protocol keeps LLM-based and rule-based engines interchangeable as long as they
    expose the same `run` entry point.
    """

    def run(self, payload: InteractionInput) -> InteractionReport:
        """Runs one interaction pass and returns the resulting report.

        This method is the common entry point used by the interaction service when it
        needs questions or proposals for the current CIM and UVL input.
        """
        ...
