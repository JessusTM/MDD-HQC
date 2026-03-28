from typing import List

from app.services.interaction.llm.base import LLMInterface

from app.models.llm_contract import (
    InteractionInput,
    InteractionQuestion,
    InteractionReport,
)
from app.services.interaction.interaction_engine import InteractionEngine


class LLMInteractionEngine(InteractionEngine):
    def __init__(self, llm_client: LLMInterface):
        self.llm_client = llm_client

    def run(self, payload: InteractionInput) -> InteractionReport:
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
