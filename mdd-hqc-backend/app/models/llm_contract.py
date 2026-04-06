"""Shared contracts for CIM data, UVL snapshots, and interaction outputs."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel


# ------------ CIM Models ------------
# Data structures below carry the normalized CIM elements used during interaction.
class CimNode(BaseModel):
    """Represents one CIM node extracted from the source diagram.

    This structure keeps the node id, type, and raw label together so interaction
    services can classify the original diagram content without losing context.
    """

    id: str
    type: str
    label_raw: str


class CimLink(BaseModel):
    """Represents one CIM relationship between two diagram nodes.

    This contract keeps the source-target connection available so interaction and
    transformation steps can reason about links alongside the node catalog.
    """

    type: str
    source: str
    target: str
    value: Optional[str] = None


# ------------ UVL Models ------------
# Data structures below describe the UVL snapshot exchanged with LLM interactions.
class UvlFeature(BaseModel):
    """Represents one feature in the intermediate UVL payload.

    This model keeps the feature data compact so interaction services can propose
    additions or edits before the full backend UVL model is updated.
    """

    name: str
    category: str
    kind: Optional[str] = None
    attributes: Dict[str, str] = {}
    comments: List[str] = []


class UvlModel(BaseModel):
    """Represents the UVL state shared with the interaction layer.

    This contract groups features, constraints, and or-groups into one payload so
    clarification steps can inspect or extend the draft model consistently.
    """

    namespace: str
    features: List[UvlFeature] = []
    constraints: List[str] = []
    or_groups: Dict[str, List[str]] = {}


# ------------ Interaction Models ------------
# Data structures below describe the questions and proposals returned to the user.
class InteractionInput(BaseModel):
    """Bundles the CIM and UVL inputs required by one interaction run.

    This model gives the interaction engine a single request object that includes
    the diagram evidence and the current UVL draft under review.
    """

    nodes: List[CimNode] = []
    links: List[CimLink] = []
    uvl: UvlModel


QuestionScope = Literal[
    "missing_information",
    "classification_disambiguation",
    "consistency_check",
    "other",
]


class InteractionQuestion(BaseModel):
    """Represents one clarification question emitted by the interaction flow.

    This model keeps the user-facing text and answer metadata together so the
    frontend can present pending decisions in a consistent format.
    """

    id: str
    text: str
    scope: QuestionScope = "other"
    options: Optional[List[str]] = None
    answers: Optional[str] = None


ProposalKind = Literal[
    "move_feature_category",
    "add_feature",
    "add_attribute",
    "add_constraint",
    "add_or_group_child",
    "add_comment",
]


class InteractionProposal(BaseModel):
    """Represents one suggested change to the UVL draft.

    This model packages the proposed action, target, and rationale so the user can
    review structured updates before they are applied to the backend model.
    """

    id: str
    kind: ProposalKind
    target: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    rationale: str


class InteractionReport(BaseModel):
    """Collects the questions and proposals produced by one interaction pass.

    This model is the final payload returned by the interaction layer so callers can
    inspect both missing information and suggested UVL adjustments together.
    """

    questions: List[InteractionQuestion] = []
    proposals: List[InteractionProposal] = []
