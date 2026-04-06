"""LLM-backed interaction engine used to ask for missing HQC information."""

from typing import List

from app.services.interaction.llm.base import LLMInterface

from app.models.llm_contract import (
    InteractionInput,
    InteractionQuestion,
    InteractionReport,
)
from app.services.interaction.interaction_engine import InteractionEngine


class LLMInteractionEngine(InteractionEngine):
    """Builds interaction questions from the evidence returned by an LLM client.

    This engine turns provider analysis results into the structured questions consumed by
    the rest of the backend interaction flow.
    """

    def __init__(self, llm_client: LLMInterface):
        """Initializes the engine with the selected LLM client implementation.

        This keeps provider-specific analysis behind a shared interface before the engine
        turns the result into interaction questions.
        """
        self.llm_client = llm_client

    def run(self, payload: InteractionInput) -> InteractionReport:
        """Runs the LLM-backed interaction pass over the provided payload.

        This method asks the configured LLM client for missing HQC evidence and converts
        the result into the clarification questions returned by the API.
        """
        llm_analysis = self.llm_client.analyze_istar_elements(payload.nodes)

        questions: List[InteractionQuestion] = []
        for missing in llm_analysis.get("missing", []):
            if missing == "Algorithm":
                questions.append(
                    InteractionQuestion(
                        id="q_algorithm",
                        text="What type of algorithm will be used?",
                        scope="missing_information",
                        options=[
                            "Greedy",
                            "Dynamic Programming",
                            "Quantum Search",
                            "Other",
                        ],
                    )
                )
            elif missing == "Programming":
                questions.append(
                    InteractionQuestion(
                        id="q_programming",
                        text="Which framework/language will be used for development?",
                        scope="missing_information",
                        options=["Python", "Rust", "Q#", "Other"],
                    )
                )
            elif missing == "Integration_model":
                questions.append(
                    InteractionQuestion(
                        id="q_integration",
                        text="Which integration model will be used? (SOA, middleware, etc.)",
                        scope="missing_information",
                        options=["Middleware/API", "Microservices", "Quantum-SOA"],
                    )
                )
            elif missing == "Quantum_HW_constraint":
                questions.append(
                    InteractionQuestion(
                        id="q_hw",
                        text="Which hardware constraint is the most relevant?",
                        scope="missing_information",
                        options=[
                            "Qubits",
                            "Shots",
                            "Circuit depth",
                            "Error rate",
                            "Connectivity",
                            "Other",
                        ],
                    )
                )
            elif missing == "Functionality":
                questions.append(
                    InteractionQuestion(
                        id="q_functionality",
                        text="What main functionality should the system cover?",
                        scope="missing_information",
                    )
                )

        return InteractionReport(questions=questions, proposals=[])
