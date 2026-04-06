"""Service helpers that select and run the backend interaction engines."""

from typing import Dict
from app.models.llm_contract import InteractionInput, InteractionReport
from app.services.interaction.llm_client import LLMInteractionEngine
from app.services.interaction.rule_based import RuleBasedInteractionEngine
from app.services.interaction.llm.factory import get_llm_client
from app.models.uvl import UVL


# ====== Public API ======
# Functions below select the interaction engine and apply the resulting user decisions.


def get_interaction_engine(provider: str = "ollama") -> object:
    """Returns the interaction engine that matches the requested provider.

    This helper centralizes engine selection so the rest of the interaction flow can use
    one shared entry point for rule-based and LLM-backed execution.
    """

    if provider == "rule_based":
        return RuleBasedInteractionEngine()

    if provider in ["ollama", "lmstudio"]:
        llm_client = get_llm_client(provider)
        return LLMInteractionEngine(llm_client)

    return RuleBasedInteractionEngine()


def run_interaction(
    payload: InteractionInput, provider: str = "ollama"
) -> InteractionReport:
    """Runs the interaction flow with the selected provider and returns its report.

    This helper keeps the orchestration step small by combining engine resolution and
    report generation in one call used by the API layer.
    """

    engine = get_interaction_engine(provider)
    return engine.run(payload)


def apply_user_answers(uvl: UVL, answers: Dict) -> str:
    """Applies the provided answers to the UVL model and returns the saved text.

    This helper is used after clarification so the selected answers can be reflected in
    the UVL draft before the updated file is returned to the caller.
    """

    for block, value in answers.items():
        category = (
            f"@{block}" if f"@{block}" in uvl.allowed_categories else "@Functionality"
        )
        uvl.add_feature(name=value, category=category)

    uvl.create_file()

    if uvl.FILE_NAME.exists():
        return uvl.FILE_NAME.read_text(encoding="utf-8")
    return ""
