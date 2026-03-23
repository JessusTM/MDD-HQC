"""CIM->PIM transformation rules from i* models into the HQC UVL model."""

import logging
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.istar import IstarModel
from app.models.uvl import UVL
from app.services.artifacts.uvl_service import UvlService

logger = logging.getLogger(__name__)


class FeatureLocation(BaseModel):
    """Stores the UVL location created for one i* element."""

    name: str
    category: str
    subgroup: Optional[str] = None


class CimToPim:
    """Applies the CIM->PIM rules from i* into the HQC UVL model."""

    def __init__(self, xml_service: IstarModel, uvl_service: UvlService, uvl: UVL):
        """Initializes the transformer with the parsed i* model and UVL services."""
        self.xml_service = xml_service
        self.uvl_service = uvl_service
        self.uvl = uvl
        self.elements_to_actors: Dict[str, str] = {}
        self.feature_locations: Dict[str, FeatureLocation] = {}

    # ======= Private Helpers =======
    # ----- Feature Resolution and Creation -----
    # These helpers classify CIM labels, build UVL locations, and ensure features exist.

    def _build_actor_traceability_comments(self, element_id: str) -> List[str]:
        """Builds traceability comments used by R1 when features are materialized in UVL."""
        actor_label = self.elements_to_actors.get(element_id)
        if not actor_label:
            return []
        return [f"actor: {actor_label}"]

    def _get_feature_location(self, element_id: str) -> Optional[FeatureLocation]:
        """Returns the stored UVL location reused by R2, R3, R4, and R5."""
        return self.feature_locations.get(element_id)

    def _build_feature_location(
        self,
        label: str,
        category: Optional[str] = None,
        subgroup: Optional[str] = None,
    ) -> Optional[FeatureLocation]:
        """Builds the UVL location metadata used mainly by R2 and reused later by R5."""
        feature_name = self.uvl_service.format_feature_name(label)
        if not feature_name:
            return None

        if category is None:
            category, subgroup = self.uvl_service.classify_feature(label)

        return FeatureLocation(
            name=feature_name,
            category=category,
            subgroup=subgroup,
        )

    def _ensure_uvl_feature(
        self,
        element_id: str,
        label: str,
        kind: Optional[str],
        category: Optional[str] = None,
        subgroup: Optional[str] = None,
    ) -> Optional[FeatureLocation]:
        """Creates one UVL feature for R2 and for R5 resource creation when needed."""
        existing_location = self._get_feature_location(element_id)
        if existing_location is not None:
            return existing_location

        location = self._build_feature_location(label, category, subgroup)
        if location is None:
            return None

        self.uvl.add_feature(
            category=location.category,
            name=location.name,
            kind=kind,
            metadata=self._build_actor_traceability_comments(element_id),
            subgroup=location.subgroup,
        )
        self.feature_locations[element_id] = location
        return location

    def _ensure_resource_feature_for_task_branch(
        self,
        resource_id: str,
        task_location: FeatureLocation,
    ) -> Optional[FeatureLocation]:
        """Creates the resource feature required by R4/R6.1 under the task branch."""
        existing_location = self._get_feature_location(resource_id)
        if existing_location is not None:
            return existing_location

        resource_label = self.xml_service.get_label_by_id(resource_id)
        if not resource_label:
            return None

        return self._ensure_uvl_feature(
            element_id=resource_id,
            label=resource_label,
            kind=None,
            category=task_location.category,
            subgroup=task_location.subgroup,
        )

    # ----- Attribute and Hierarchy Mapping -----
    # These helpers map quality, resources, and refinements into UVL attributes and groups.

    def _add_quality_attribute_to_feature(
        self,
        quality_id: str,
        target_location: FeatureLocation,
    ) -> None:
        """Adds the quality attribute required by R3 and by qualification-link handling in R6.2."""
        quality_label = self.xml_service.get_label_by_id(quality_id)
        if not quality_label:
            return

        attribute_name = self.uvl_service.format_attribute_name(quality_label)
        if not attribute_name:
            return

        self.uvl.add_attribute_to_feature(
            feature_name=target_location.name,
            category=target_location.category,
            attribute_name=attribute_name,
            attribute_value="true",
        )

    def _attach_feature_to_parent_group(
        self,
        parent_location: FeatureLocation,
        child_location: FeatureLocation,
        relation: str,
    ) -> None:
        """Attaches child features for R4 and for refinement handling in R6.1/R6.4."""
        if parent_location.name == child_location.name:
            return

        if relation == "mandatory":
            self.uvl.add_mandatory_child(parent_location.name, child_location.name)
            return

        if relation == "or":
            self.uvl.add_or_child(parent_location.name, child_location.name)

    # ----- Link and Dependency Resolution -----
    # These helpers translate i* links into UVL constraints, comments, and feature groups.

    def _resolve_social_dependency_pairs(self) -> List[Dict[str, str]]:
        """Resolves the depender/dependee pairs consumed by R5 social dependency constraints."""
        pairs: List[Dict[str, str]] = []
        resources = self.xml_service.get_intentional_element_by_type("resource")
        outgoing_by_resource: Dict[str, List[str]] = {}
        incoming_by_resource: Dict[str, List[str]] = {}

        for link in self.xml_service.get_social_dependencies().values():
            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            if (
                target_id in resources
                and self._get_feature_location(source_id) is not None
            ):
                outgoing_by_resource.setdefault(target_id, []).append(source_id)
                continue

            if (
                source_id in resources
                and self._get_feature_location(target_id) is not None
            ):
                incoming_by_resource.setdefault(source_id, []).append(target_id)

        for resource_id, source_ids in outgoing_by_resource.items():
            target_ids = incoming_by_resource.get(resource_id, [])
            for source_id in source_ids:
                for target_id in target_ids:
                    if source_id == target_id:
                        continue
                    pairs.append({"source_id": source_id, "target_id": target_id})

        return pairs

    def _transform_needed_by_links_to_resources(self) -> None:
        """Applies R4 and R6.1 by turning needed-by links into mandatory task resources."""
        resources = self.xml_service.get_intentional_element_by_type("resource")
        tasks = self.xml_service.get_intentional_element_by_type("task")

        for link in self.xml_service.get_internal_links().values():
            if link.get("type") != "needed-by":
                continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            resource_id = None
            task_id = None

            if source_id in resources and target_id in tasks:
                resource_id = source_id
                task_id = target_id
            elif target_id in resources and source_id in tasks:
                resource_id = target_id
                task_id = source_id

            if not resource_id or not task_id:
                continue

            task_location = self._get_feature_location(task_id)
            if task_location is None:
                continue

            resource_location = self._ensure_resource_feature_for_task_branch(
                resource_id,
                task_location,
            )
            if resource_location is None:
                continue

            self._attach_feature_to_parent_group(
                task_location,
                resource_location,
                relation="mandatory",
            )

    def _transform_contribution_links_to_comments(self) -> None:
        """Applies R6.3 by copying contribution links into UVL comments as-is."""
        for link in self.xml_service.get_internal_links().values():
            if link.get("type") != "contribution":
                continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            source_location = self._get_feature_location(source_id)
            if source_location is None:
                continue

            contribution_label = (link.get("label") or "").strip().lower()
            if not contribution_label:
                continue

            target_label = self.xml_service.get_label_by_id(target_id)
            if not target_label:
                continue

            target_name = self.uvl_service.format_feature_name(target_label)
            self.uvl.add_comment_to_feature(
                feature_name=source_location.name,
                category=source_location.category,
                comment=f"contribution: {contribution_label} -> {target_name}",
            )

    def _transform_refinements_to_feature_groups(self) -> None:
        """Applies R6.4 by translating refinements into mandatory or or-groups."""
        for refinement in self.xml_service.get_refinements().values():
            parent_id = refinement.get("source")
            child_id = refinement.get("target")
            relation = (refinement.get("value") or "").strip().lower()

            if not parent_id or not child_id:
                continue
            if relation not in {"and", "or"}:
                continue

            parent_location = self._get_feature_location(parent_id)
            child_location = self._get_feature_location(child_id)
            if parent_location is None or child_location is None:
                continue

            if relation == "and":
                self._attach_feature_to_parent_group(
                    parent_location,
                    child_location,
                    relation="mandatory",
                )
                continue

            self._attach_feature_to_parent_group(
                parent_location,
                child_location,
                relation="or",
            )

    # ======= Public Rules =======
    # Public entry points that apply the explicit CIM->PIM transformation rules.

    def apply_r1(self) -> None:
        """Loads actor ownership so later rules can add traceability comments."""
        self.elements_to_actors = self.xml_service.get_element_to_actor_mapping()
        logger.debug(
            "CIM-to-PIM R1 applied: element-to-actor mappings=%s",
            len(self.elements_to_actors),
        )

    def apply_r2(self) -> None:
        """Transforms goals and tasks into UVL features using dictionary-based classification."""
        for goal in self.xml_service.get_intentional_element_by_type("goal").values():
            goal_id = goal.get("id")
            goal_label = goal.get("label")
            if not goal_id or not goal_label:
                continue
            self._ensure_uvl_feature(goal_id, goal_label, kind="goal")

        for task in self.xml_service.get_intentional_element_by_type("task").values():
            task_id = task.get("id")
            task_label = task.get("label")
            if not task_id or not task_label:
                continue
            self._ensure_uvl_feature(task_id, task_label, kind="task")

        logger.debug("CIM-to-PIM R2 applied: goals and tasks converted to features")

    def apply_r3(self) -> None:
        """Transforms qualification links into quality attributes after all target features exist."""
        qualities = self.xml_service.get_intentional_element_by_type("quality")
        if not qualities:
            qualities = self.xml_service.get_intentional_element_by_type("softgoal")

        for link in self.xml_service.get_internal_links().values():
            if link.get("type") != "qualification-link":
                continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id:
                continue

            quality_id = None
            target_element_id = None

            if source_id in qualities:
                quality_id = source_id
                target_element_id = target_id
            elif target_id in qualities:
                quality_id = target_id
                target_element_id = source_id

            if not quality_id or not target_element_id:
                continue

            target_location = self._get_feature_location(target_element_id)
            if target_location is None:
                continue

            self._add_quality_attribute_to_feature(quality_id, target_location)

        logger.debug(
            "CIM-to-PIM R3 applied: qualities converted into feature attributes"
        )

    def apply_r4(self) -> None:
        """Transforms social dependencies into UVL requires constraints."""
        for pair in self._resolve_social_dependency_pairs():
            source_location = self._get_feature_location(pair["source_id"])
            target_location = self._get_feature_location(pair["target_id"])
            if source_location is None or target_location is None:
                continue

            self.uvl.add_constraint(f"{source_location.name} => {target_location.name}")

        logger.debug(
            "CIM-to-PIM R4 applied: social dependencies converted into requires"
        )

    def apply_r5(self) -> None:
        """Applies internal-link and refinement rules over the feature set created before."""
        self._transform_needed_by_links_to_resources()
        self._transform_contribution_links_to_comments()
        self._transform_refinements_to_feature_groups()
        logger.debug("CIM-to-PIM R5 applied: needed-by, contributions, and refinements")
