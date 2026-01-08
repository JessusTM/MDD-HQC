from typing import Protocol
from app.models.llm_contract import InteractionInput, InteractionReport


class InteractionEngine(Protocol):
    """
    Contrato para motores de interacción (LLM o rule-based).
    NOTA: Protocol permite validar el contrato por «forma»: no requiere herencia, solo implementar run().
    """

    def run(self, payload: InteractionInput) -> InteractionReport: ...
