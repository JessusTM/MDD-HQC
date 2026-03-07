import logging

from app.models.uml import UmlModel
from app.models.uvl import UVL
from app.services.artifacts.plantuml_service import PlantumlService
from app.services.artifacts.uvl_service import UvlService

logger = logging.getLogger(__name__)


class PimToPsm:
    def __init__(
        self,
        uvl: UVL,
        uml: UmlModel,
        uvl_service: UvlService,
        plantuml_service: PlantumlService,
    ):
        self.uvl = uvl
        self.uml = uml
        self.uvl_service = uvl_service
        self.plantuml_service = plantuml_service

    # Metadata Agents + Contributions -> Comments UML
    def apply_q1(self):
        pass

    def apply_q2(self):
        features = self.uvl.get_features()
        for feature in features:
            category = feature.category
            kind = feature.kind

            if category != "@Functionality":
                continue

            if kind == "goal":
                self.uml.get_or_create_class(feature.name)

            if kind == "task":
                parent_class = self.uml.get_or_create_class(feature.name)
                self.uml.add_method_to_class(
                    class_name=parent_class.name, method_name=feature.name
                )

    def apply_q3(self):
        for feature in self.uvl.features:
            if feature.category != "@Algorithm":
                continue
