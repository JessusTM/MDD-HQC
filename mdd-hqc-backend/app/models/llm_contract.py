from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel


# ------ CIM ------
class CimNode(BaseModel):
    id: str
    type: str
    label_raw: str


class CimLink(BaseModel):
    type: str
    source: str
    target: str
    value: Optional[str] = None


# ------ UVL ------
class UvlFeature(BaseModel):
    name: str
    category: str
    kind: Optional[str] = None
    attributes: Dict[str, str] = {}
    comments: List[str] = []


class UvlModel(BaseModel):
    namespace: str
    features: List[UvlFeature] = []
    constraints: List[str] = []
    or_groups: Dict[str, List[str]] = {}


# ------ Interaction ------
class InteractionInput(BaseModel):
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
    id: str
    text: str
    scope: QuestionScope = "other"


ProposalKind = Literal[
    "move_feature_category",
    "add_feature",
    "add_attribute",
    "add_constraint",
    "add_or_group_child",
    "add_comment",
]


class InteractionProposal(BaseModel):
    id: str
    kind: ProposalKind
    target: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    rationale: str


class InteractionReport(BaseModel):
    questions: List[InteractionQuestion] = []
    proposals: List[InteractionProposal] = []
