"""Rule-based interaction engine used when no LLM provider is selected."""

from app.models.llm_contract import (
    InteractionInput,
    InteractionReport,
    InteractionQuestion,
    InteractionProposal,
)
from app.services.interaction.interaction_engine import InteractionEngine


class RuleBasedInteractionEngine(InteractionEngine):
    """Produces clarification questions and proposals from simple deterministic rules.

    This engine provides a fallback interaction strategy for the backend when the flow
    should not depend on an external LLM provider.
    """

    def run(self, payload: InteractionInput) -> InteractionReport:
        """Runs the rule-based interaction pass over the provided payload.

        This method inspects the current CIM evidence and returns the questions or
        proposals that can be inferred through fixed backend rules.
        """
        questions = []
        proposals = []

        for node in payload.nodes:
            if node.type == "goal" and not node.label_raw.strip():
                questions.append(
                    InteractionQuestion(
                        id="q_goal_missing",
                        text="An unnamed goal was detected. What should it be called?",
                        scope="missing_information",
                    )
                )

        for link in payload.links:
            if link.type == "refinement":
                proposals.append(
                    InteractionProposal(
                        id="p_refinement",
                        kind="add_or_group_child",
                        target={"parent": link.source},
                        data={"child": link.target},
                        rationale="A refinement was detected in the CIM",
                    )
                )
        return InteractionReport(questions=questions, proposals=proposals)
