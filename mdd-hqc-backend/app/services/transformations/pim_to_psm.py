"""PIM->PSM transformation rules from UVL models into the HQC UML model."""

import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.uml import UmlClass, UmlMethod, UmlModel
from app.models.uvl import Feature, UVL

logger = logging.getLogger(__name__)


class UmlElementLocation(BaseModel):
    """Stores the minimal UML reference created for one UVL feature.

    It keeps the target class name and, when the feature became a method,
    the method name inside that class.
    """

    class_name: str
    method_name: Optional[str] = None


class PimToPsm:
    """Applies the PIM->PSM rules from UVL into the HQC UML model."""

    def __init__(self, uvl: UVL):
        """Initializes the transformer with the source UVL model."""
        self.uvl = uvl
        self.uml = UmlModel(name="MDD-HQC")
        self.element_locations: Dict[str, UmlElementLocation] = {}

    # ----- UVL Navigation -----
    # Helpers for R2 that inspect the UVL hierarchy and locate goal/task parents.

    def _get_existing_feature(self, feature_name: str) -> Optional[Feature]:
        """Helper for R2 that returns one UVL feature already loaded in memory by name."""
        return self.uvl.get_feature(feature_name)

    def _get_parent_feature_name(self, feature_name: str) -> Optional[str]:
        """Helper for R2 that returns the direct parent name of one UVL feature."""
        return self.uvl.parent_by_child.get(feature_name)

    def _get_parent_feature(self, feature_name: str) -> Optional[Feature]:
        """Helper for R2 that returns the direct parent feature of one UVL feature."""
        parent_name = self._get_parent_feature_name(feature_name)
        if not parent_name:
            return None
        return self._get_existing_feature(parent_name)

    def _is_task_child_of_goal(self, feature: Feature) -> bool:
        """Helper for R2 that checks whether one task is directly nested under a goal feature."""
        if feature.kind != "task":
            return False

        parent_feature = self._get_parent_feature(feature.name)
        if parent_feature is None:
            return False
        return parent_feature.kind == "goal"

    def _get_nearest_goal_feature(self, feature_name: str) -> Optional[Feature]:
        """Helper for R2 that returns the closest ancestor goal used to place a task as a method."""
        parent_name = self._get_parent_feature_name(feature_name)

        while parent_name:
            parent_feature = self._get_existing_feature(parent_name)
            if parent_feature is None:
                return None
            if parent_feature.kind == "goal":
                return parent_feature
            parent_name = self._get_parent_feature_name(parent_name)

        return None

    def _get_helper_root_task_feature(self, task_feature: Feature) -> Feature:
        """Helper for R2 that returns the root task that must become the helper class of one branch."""
        helper_root = task_feature
        parent_feature = self._get_parent_feature(task_feature.name)

        while parent_feature is not None:
            if parent_feature.kind != "task":
                return helper_root
            if self._is_task_child_of_goal(parent_feature):
                return helper_root

            helper_root = parent_feature
            parent_feature = self._get_parent_feature(parent_feature.name)

        return helper_root

    # ----- UML Creation and Lookup -----
    # Helpers for R2-R4 that create UML elements and store where each UVL feature ended up.

    def _get_existing_element_location(
        self, feature_name: str
    ) -> Optional[UmlElementLocation]:
        """Helper for R1, R2, R7, and R8 that returns the UML location already created for one UVL feature."""
        return self.element_locations.get(feature_name)

    def _get_or_create_uml_class(self, class_name: str) -> UmlClass:
        """Helper for R2, R3, and R4 that returns one UML class, creating it when needed."""
        return self.uml.get_or_create_class(class_name)

    def _get_or_create_method(self, class_name: str, method_name: str) -> UmlMethod:
        """Helper for R2 that returns one UML method inside a class, creating it when needed."""
        existing_method = self.uml.get_method_from_class(class_name, method_name)
        if existing_method is not None:
            return existing_method
        return self.uml.add_method_to_class(class_name, method_name)

    def _store_class_location(self, feature_name: str, class_name: str) -> None:
        """Helper for R2, R3, and R4 that stores the UML class created for one UVL feature."""
        self.element_locations[feature_name] = UmlElementLocation(class_name=class_name)

    def _store_method_location(
        self,
        feature_name: str,
        class_name: str,
        method_name: str,
    ) -> None:
        """Helper for R2 that stores the UML method created for one UVL feature."""
        self.element_locations[feature_name] = UmlElementLocation(
            class_name=class_name,
            method_name=method_name,
        )

    def _get_or_create_goal_class_for_task(
        self, task_feature: Feature
    ) -> Optional[UmlClass]:
        """Helper for R2 that returns the UML class derived from the nearest goal of one task."""
        goal_feature = self._get_nearest_goal_feature(task_feature.name)
        if goal_feature is None:
            return None
        return self._get_or_create_uml_class(goal_feature.name)

    def _get_or_create_helper_class_for_task(self, task_feature: Feature) -> UmlClass:
        """Helper for R2 that returns the helper class used for the root task of one task-only branch."""
        helper_root = self._get_helper_root_task_feature(task_feature)
        return self._get_or_create_uml_class(helper_root.name)

    # ----- UML Annotations and Attributes -----
    # Helpers for R1, R2, R5, R7, and R8 that copy metadata, resources, attributes, and annotations.

    def _add_feature_annotations(self, feature: Feature) -> None:
        """Helper for R1 that adds actor and contribution annotations to the mapped UML element."""
        location = self._get_existing_element_location(feature.name)
        if location is None:
            return

        annotations: List[str] = []
        for metadata in feature.metadata:
            text = (metadata or "").strip()
            if not text:
                continue
            if text.startswith("actor:") or text.startswith("contribution:"):
                annotations.append(text)

        if not annotations:
            return

        if location.method_name:
            method = self.uml.get_method_from_class(
                location.class_name, location.method_name
            )
            if method is None:
                return
            for annotation in annotations:
                method.add_note(annotation)
            return

        uml_class = self.uml.get_class(location.class_name)
        if uml_class is None:
            return
        for annotation in annotations:
            uml_class.add_note(annotation)

    def _add_feature_attributes_to_class(self, feature: Feature) -> None:
        """Helper for R7 that adds UVL feature attributes to the UML class associated with one feature."""
        if not feature.attributes:
            return

        location = self._get_existing_element_location(feature.name)
        if location is None:
            return

        class_name = location.class_name
        for attribute_name, attribute_value in feature.attributes.items():
            attribute = self.uml.add_attribute_to_class(
                class_label=class_name,
                attribute_name=attribute_name,
                default=attribute_value,
            )
            if location.method_name:
                attribute.notes.append(f"source-method: {location.method_name}")

    def _add_helper_resource_attributes(self, helper_feature: Feature) -> None:
        """Helper for R2 that adds direct resource children of one helper task as UML attributes."""
        helper_location = self._get_existing_element_location(helper_feature.name)
        if helper_location is None:
            return

        for child_name, parent_name in self.uvl.parent_by_child.items():
            if parent_name != helper_feature.name:
                continue

            child_feature = self._get_existing_feature(child_name)
            if child_feature is None:
                continue
            if child_feature.kind != "resource":
                continue

            self.uml.add_attribute_to_class(
                class_label=helper_location.class_name,
                attribute_name=child_feature.name,
            )

    def _add_group_annotation(self, feature: Feature, group_name: str) -> None:
        """Helper for R8 that adds one UML annotation for a mandatory or or-group."""
        child_names: List[str] = []
        if group_name == "mandatory":
            child_names = feature.mandatory_children
        if group_name == "or":
            child_names = feature.or_children
        if not child_names:
            return

        annotation_value = ", ".join(child_names)
        location = self._get_existing_element_location(feature.name)
        if location is None:
            return

        if location.method_name:
            method = self.uml.get_method_from_class(
                location.class_name, location.method_name
            )
            if method is None:
                return
            method.add_note(f"{group_name}: {annotation_value}")
            return

        uml_class = self.uml.get_class(location.class_name)
        if uml_class is None:
            return
        uml_class.add_note(f"{group_name}: {annotation_value}")

    def _add_quantum_hw_annotation(self, feature: Feature) -> None:
        """Helper for R5 that adds one hardware-constraint annotation to quantum classes and drivers."""
        applied = False

        for uml_class in self.uml.classes.values():
            stereotypes = set(uml_class.stereotypes)
            if "Quantum" not in stereotypes and "QuantumDriver" not in stereotypes:
                continue

            uml_class.add_note(f"quantum_hw_constraint: {feature.name}")
            applied = True

        if applied:
            return

        self.uml.add_note(f"quantum_hw_constraint: {feature.name}")

    # ----- UML Dependencies -----
    # Helpers for R6 that translate UVL requires constraints into UML dependencies.

    def _add_requires_dependency(self, source_name: str, target_name: str) -> None:
        """Helper for R6 that adds one UML dependency with stereotype requires."""
        source_location = self._get_existing_element_location(source_name)
        target_location = self._get_existing_element_location(target_name)

        source_label = source_name
        target_label = target_name

        if source_location is not None:
            source_label = source_location.class_name
        if target_location is not None:
            target_label = target_location.class_name

        self.uml.add_dependency_by_label(
            source_label=source_label,
            target_label=target_label,
            stereotype="requires",
        )

    # ======= Rules =======
    # Public entry points that apply the explicit PIM->PSM transformation rules.

    def apply_r1(self) -> None:
        """R1: transfers actor and contribution metadata as UML annotations."""
        for feature in self.uvl.get_features():
            self._add_feature_annotations(feature)

        logger.debug("PIM-to-PSM R1 applied: metadata annotations copied to UML")

    def apply_r2(self) -> None:
        """R2: transforms goal/task/resource features into classes, methods, and helper attributes."""
        for feature in self.uvl.get_features():
            if feature.kind == "goal":
                self._get_or_create_uml_class(feature.name)
                self._store_class_location(feature.name, feature.name)
                continue

            if feature.kind != "task":
                continue

            if self._is_task_child_of_goal(feature):
                goal_class = self._get_or_create_goal_class_for_task(feature)
                if goal_class is None:
                    continue

                self._get_or_create_method(goal_class.name, feature.name)
                self._store_method_location(feature.name, goal_class.name, feature.name)
                continue

            helper_root = self._get_helper_root_task_feature(feature)
            helper_class = self._get_or_create_helper_class_for_task(feature)

            if helper_root.name == feature.name:
                logger.debug(
                    "PIM-to-PSM R2 helper class created: task=%s, class=%s",
                    feature.name,
                    helper_class.name,
                )
                self._store_class_location(feature.name, helper_class.name)
                self._add_helper_resource_attributes(feature)
                continue

            self._get_or_create_method(helper_class.name, feature.name)
            self._store_method_location(feature.name, helper_class.name, feature.name)

        logger.debug(
            "PIM-to-PSM R2 applied: goal/task/resource features converted to classes, methods, and attributes"
        )

    def apply_r3(self) -> None:
        """R3: transforms algorithm features into UML classes and marks quantum ones."""
        for feature in self.uvl.get_features_by_category("@Algorithm"):
            if feature.kind == "resource":
                continue

            location = self._get_existing_element_location(feature.name)
            uml_class = None

            if location is not None:
                uml_class = self.uml.get_class(location.class_name)

            if uml_class is None:
                uml_class = self._get_or_create_uml_class(feature.name)
                self._store_class_location(feature.name, uml_class.name)

            if feature.subgroup == "Quantum" and "Quantum" not in uml_class.stereotypes:
                uml_class.stereotypes.append("Quantum")
                logger.debug(
                    "PIM-to-PSM R3 quantum stereotype applied: feature=%s, class=%s",
                    feature.name,
                    uml_class.name,
                )

        logger.debug(
            "PIM-to-PSM R3 applied: algorithm features converted to UML classes"
        )

    def apply_r4(self) -> None:
        """R4: transforms integration model features into QuantumDriver classes."""
        for feature in self.uvl.get_features_by_category("@Integration_model"):
            uml_class = self._get_or_create_uml_class(feature.name)
            if "QuantumDriver" not in uml_class.stereotypes:
                uml_class.stereotypes.append("QuantumDriver")
            self._store_class_location(feature.name, uml_class.name)

        logger.debug(
            "PIM-to-PSM R4 applied: integration features converted to QuantumDriver classes"
        )

    def apply_r5(self) -> None:
        """R5: transforms quantum hardware constraints into UML annotations."""
        for feature in self.uvl.get_features_by_category("@Quantum_HW_constraint"):
            self._add_quantum_hw_annotation(feature)

        logger.debug(
            "PIM-to-PSM R5 applied: quantum hardware constraints added as annotations"
        )

    def apply_r6(self) -> None:
        """R6: transforms UVL requires constraints into UML dependencies."""
        for constraint in self.uvl.get_constraints():
            if "=>" not in constraint:
                continue

            parts = constraint.split("=>", maxsplit=1)
            source_name = parts[0].strip()
            target_name = parts[1].strip()
            if not source_name or not target_name:
                continue

            self._add_requires_dependency(source_name, target_name)

        logger.debug(
            "PIM-to-PSM R6 applied: requires constraints converted to UML dependencies"
        )

    def apply_r7(self) -> None:
        """R7: transforms UVL feature attributes into UML attributes."""
        for feature in self.uvl.get_features():
            self._add_feature_attributes_to_class(feature)

        logger.debug("PIM-to-PSM R7 applied: feature attributes copied to UML classes")

    def apply_r8(self) -> None:
        """R8: transforms mandatory and or groups into UML annotations."""
        for feature in self.uvl.get_features():
            self._add_group_annotation(feature, "mandatory")
            self._add_group_annotation(feature, "or")

        logger.debug("PIM-to-PSM R8 applied: feature groups copied as UML annotations")

    def transform(self) -> UmlModel:
        """Runs the PIM->PSM rule pipeline and returns the generated UML model."""
        self.apply_r2()
        self.apply_r3()
        self.apply_r4()
        self.apply_r6()
        self.apply_r7()
        self.apply_r8()
        self.apply_r1()
        self.apply_r5()
        return self.uml
