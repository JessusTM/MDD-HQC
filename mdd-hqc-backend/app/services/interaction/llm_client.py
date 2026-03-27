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
                        text="¿Qué tipo de algoritmo se utilizará?",
                        scope="missing_information",
                        options=[
                            "Greedy",
                            "Dynamic Programming",
                            "Quantum Search",
                            "Otro",
                        ],
                    )
                )
            elif missing == "Programming":
                questions.append(
                    InteractionQuestion(
                        id="q_programming",
                        text="¿Qué framework/lenguaje se usará para programar?",
                        scope="missing_information",
                        options=["Python", "Rust", "Q#", "Otro"],
                    )
                )
            elif missing == "Integration_model":
                questions.append(
                    InteractionQuestion(
                        id="q_integration",
                        text="¿Qué modelo de integración se usará? (SOA, middleware, etc.)",
                        scope="missing_information",
                        options=["Middleware/API", "Microservices", "Quantum-SOA"],
                    )
                )
            elif missing == "Quantum_HW_constraint":
                questions.append(
                    InteractionQuestion(
                        id="q_hw",
                        text="¿Qué restriccion HW es más relevante?",
                        scope="missing_information",
                        options=[
                            "Qubits",
                            "Shots",
                            "Circuit depth",
                            "Error rate",
                            "Conectividad",
                            "Otro",
                        ],
                    )
                )
            elif missing == "Functionality":
                questions.append(
                    InteractionQuestion(
                        id="q_functionality",
                        text="¿Qué funcionalidad principal debe cubrir el sistema?",
                        scope="missing_information",
                    )
                )

        return InteractionReport(questions=questions, proposals=[])
