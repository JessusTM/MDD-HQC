from app.models.llm_contract import (
    InteractionInput,
    InteractionReport,
    InteractionQuestion,
    InteractionProposal,
)
from app.services.interaction.interaction_engine import InteractionEngine


class RuleBasedInteractionEngine(InteractionEngine):
    def run(self, payload: InteractionInput) -> InteractionReport:
        questions = []
        proposals = []

        for node in payload.nodes:
            if node.type == "goal" and not node.label_raw.strip():
                questions.append(
                    InteractionQuestion(
                        id="q_goal_missing",
                        text="Se detectó un goal sin nombre, ¿cómo debería llamarse?",
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
                        rationale="Se detectó un refinamiento en el CIM",
                    )
                )
        return InteractionReport(questions=questions, proposals=proposals)
