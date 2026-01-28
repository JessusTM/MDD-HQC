import logging

from app.models.uvl import UVL
from app.services.artifacts.xml_service import XmlService
from app.services.artifacts.uvl_service import UvlService

logger = logging.getLogger(__name__)


class CimToPim:
    def __init__(self, xml_service: XmlService, uvl_service: UvlService, uvl: UVL):
        self.xml_service = xml_service
        self.uvl_service = uvl_service
        self.uvl = uvl
        self.elements_to_actors = {}

    # R1: Actors / Resources -> Metadata
    def apply_r1(self) -> None:
        self.elements_to_actors = self.xml_service.get_element_to_actor_mapping()
        logger.debug("CIM-to-PIM R1 applied: element-to-actor mappings=%s", len(self.elements_to_actors))

    def _convert_intentional_element_in_feature(self, kind):
        elements = self.xml_service.get_intentional_element_by_type(kind)
        for element in elements.values():
            id = element.get("id")
            label = element.get("label")

            if not id or not label:
                continue

            feature_category = self.uvl_service.assign_category(label)
            feature_name = self.uvl_service.format_feature_name(label)
            actor_label = self.elements_to_actors.get(id)

            metadata = []
            if actor_label:
                metadata.append(f"actor: {actor_label}")

            self.uvl.add_feature(
                category=feature_category,
                name=feature_name,
                kind=f"{kind}",
                metadata=metadata,
            )

    # R2: Goals / Tasks -> Features
    def apply_r2(self) -> None:
        self._convert_intentional_element_in_feature("goal")
        self._convert_intentional_element_in_feature("task")
        logger.debug("CIM-to-PIM R2 applied: goals and tasks converted to features")

    # R3: Softgoals -> Atributos (via qualification-link)
    def apply_r3(self) -> None:
        softgoals = self.xml_service.get_intentional_element_by_type("softgoal")
        goals = self.xml_service.get_intentional_element_by_type("goal")
        tasks = self.xml_service.get_intentional_element_by_type("task")
        links = self.xml_service.get_internal_links()

        feature_elements = {}
        feature_elements.update(goals)
        feature_elements.update(tasks)

        for link in links.values():
            if link.get("type") != "qualification-link":
                continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            if source_id in softgoals and target_id in feature_elements:
                softgoal_id = source_id
                feature_id = target_id
            elif target_id in softgoals and source_id in feature_elements:
                softgoal_id = target_id
                feature_id = source_id
            else:
                continue

            softgoal_label = self.xml_service.get_label_by_id(softgoal_id)
            feature_label = self.xml_service.get_label_by_id(feature_id)
            if not softgoal_label or not feature_label:
                continue

            feature_name = self.uvl_service.format_feature_name(feature_label)
            category = self.uvl_service.assign_category(feature_label)
            attribute_name = self.uvl_service.format_feature_name(softgoal_label)

            self.uvl.add_attribute_to_feature(
                feature_name=feature_name,
                category=category,
                attribute_name=attribute_name,
                attribute_value="true",
            )
        logger.debug("CIM-to-PIM R3 applied: softgoals -> attributes via qualification-link")

    # R4: Dependencias sociales -> requires
    def apply_r4(self) -> None:
        goals = self.xml_service.get_intentional_element_by_type("goal")
        tasks = self.xml_service.get_intentional_element_by_type("task")
        social_dependencies = self.xml_service.get_social_dependencies()

        feature_elements = {}
        feature_elements.update(goals)
        feature_elements.update(tasks)

        for dep in social_dependencies.values():
            source_id = dep.get("source")
            target_id = dep.get("target")
            if not source_id or not target_id:
                continue

            if source_id not in feature_elements or target_id not in feature_elements:
                continue

            source_label = self.xml_service.get_label_by_id(source_id)
            target_label = self.xml_service.get_label_by_id(target_id)
            if not source_label or not target_label:
                continue

            source_feature = self.uvl_service.format_feature_name(source_label)
            target_feature = self.uvl_service.format_feature_name(target_label)
            if (
                not source_feature
                or not target_feature
                or source_feature == target_feature
            ):
                continue

            self.uvl.add_constraint(f"{source_feature} -> {target_feature}")
        logger.debug("CIM-to-PIM R4 applied: social dependencies -> requires constraints")

    # R5: needed-by / qualification-link / contribution / refinement
    def apply_r5(self) -> None:
        """
        R5: needed-by / contribution / refinement -> UVL constraints, contributions, and OR-groups.

        This rule consumes:
        - Internal links (needed-by, contribution). Note: qualification-link is handled by R3.
        - Refinements (AND/OR) to derive constraints or OR-groups.

        Labels are resolved by id via XmlService, since links store only endpoint ids.
        """
        goals = self.xml_service.get_intentional_element_by_type("goal")
        tasks = self.xml_service.get_intentional_element_by_type("task")
        links = self.xml_service.get_internal_links()
        refinements = self.xml_service.get_refinements()

        feature_elements = {}
        feature_elements.update(goals)
        feature_elements.update(tasks)

        self._apply_r5_needed_by(links, feature_elements)
        self._apply_r5_contributions(links)
        self._apply_r5_refinements(refinements, feature_elements)
        logger.debug("CIM-to-PIM R5 applied: needed-by, contributions, refinements")

    def _apply_r5_needed_by(self, links, feature_elements) -> None:
        """
        R5.1: needed-by -> requires-like constraints.

        Mapping: target -> source (keeps the same direction used in the legacy implementation).
        """
        for link in links.values():
            if link.get("type") != "needed-by":
                continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            if source_id not in feature_elements or target_id not in feature_elements:
                continue

            source_label = self.xml_service.get_label_by_id(source_id)
            target_label = self.xml_service.get_label_by_id(target_id)
            if not source_label or not target_label:
                continue

            source_name = self.uvl_service.format_feature_name(source_label)
            target_name = self.uvl_service.format_feature_name(target_label)
            if not source_name or not target_name or source_name == target_name:
                continue

            self.uvl.add_constraint(f"{target_name} -> {source_name}")

    def _apply_r5_contributions(self, links) -> None:
        """
        R5.2: contribution -> contributions (stored as comments in the UVL output).

        The contribution kind is taken from the edge label (e.g., helps/makes/hurts/breaks),
        and endpoints are resolved by id.
        """
        for link in links.values():
            if link.get("type") != "contribution":
                continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            contribution_kind = (link.get("label") or "").strip().lower()
            if not contribution_kind:
                continue

            source_label = self.xml_service.get_label_by_id(source_id)
            target_label = self.xml_service.get_label_by_id(target_id)
            if not source_label or not target_label:
                continue

            source_name = self.uvl_service.format_feature_name(source_label)
            target_name = self.uvl_service.format_feature_name(target_label)
            if not source_name or not target_name or source_name == target_name:
                continue

            self.uvl.add_contribution(
                f"{source_name} {contribution_kind} {target_name}"
            )

    def _apply_r5_refinements(self, refinements, feature_elements) -> None:
        """
        R5.3: refinement AND/OR -> constraints / OR-groups.

        - AND: child -> parent constraint
        - OR : record OR-group parent -> child
        """
        for ref in refinements.values():
            parent_id = ref.get("source")
            child_id = ref.get("target")
            kind = (ref.get("value") or "").strip().lower()

            if not parent_id or not child_id or kind not in {"and", "or"}:
                continue

            if parent_id not in feature_elements or child_id not in feature_elements:
                continue

            parent_label = self.xml_service.get_label_by_id(parent_id)
            child_label = self.xml_service.get_label_by_id(child_id)
            if not parent_label or not child_label:
                continue

            parent_name = self.uvl_service.format_feature_name(parent_label)
            child_name = self.uvl_service.format_feature_name(child_label)
            if not parent_name or not child_name or parent_name == child_name:
                continue

            if kind == "and":
                self.uvl.add_constraint(f"{child_name} -> {parent_name}")
            else:
                self.uvl.add_or_group(parent_name, child_name)
