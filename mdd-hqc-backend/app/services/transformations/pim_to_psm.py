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
    """Applies the PIM->PSM rules from UVL into the HQC UML model.

    This transformer reads the generated UVL structure and maps it into the UML classes,
    methods, attributes, and annotations needed by the final PSM representation.
    """

    def __init__(self, uvl: UVL):
        """Initializes the transformer with the source UVL model.

        The transformer keeps both the source UVL data and the target UML model in
        memory so each rule can progressively enrich the generated diagram.
        """
        self.uvl = uvl
        self.uml = UmlModel(name="MDD-HQC")
        self.element_locations: Dict[str, UmlElementLocation] = {}

    # ====== Private Helpers ======
    # Internal methods below inspect the UVL model and prepare the generated UML elements.

    # ------------ UVL Navigation ------------
    # Methods below inspect the UVL hierarchy and locate the parents needed by R2.

    def _get_existing_feature(self, feature_name: str) -> Optional[Feature]:
        """Returns one UVL feature already loaded in memory by name.

        This helper supports rule R2 when task placement needs to inspect existing
        parent or ancestor features in the source UVL hierarchy.
        """
        return self.uvl.get_feature(feature_name)

    def _get_parent_feature_name(self, feature_name: str) -> Optional[str]:
        """Returns the direct parent name of one UVL feature.

        This helper supports rule R2 by exposing the stored hierarchy relation without
        forcing the rule methods to inspect the raw parent index directly.
        """
        return self.uvl.parent_by_child.get(feature_name)

    def _get_parent_feature(self, feature_name: str) -> Optional[Feature]:
        """Returns the direct parent feature of one UVL feature.

        This helper supports rule R2 when task placement depends on the actual parent
        feature data instead of only the stored parent name.
        """
        parent_name = self._get_parent_feature_name(feature_name)
        if not parent_name:
            return None
        return self._get_existing_feature(parent_name)

    def _is_task_child_of_goal(self, feature: Feature) -> bool:
        """Checks whether one task is directly nested under a goal feature.

        This helper supports rule R2 when deciding whether a task becomes a method on a
        goal-derived class or part of a helper-task branch.
        """
        if feature.kind != "task":
            return False

        parent_feature = self._get_parent_feature(feature.name)
        if parent_feature is None:
            return False
        return parent_feature.kind == "goal"

    def _get_nearest_goal_feature(self, feature_name: str) -> Optional[Feature]:
        """Returns the closest ancestor goal used to place a task as a method.

        This helper supports rule R2 by finding the goal class that should own a task
        when the task belongs to a goal-oriented branch in the UVL hierarchy.
        """
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
        """Returns the root task that must become the helper class of one branch.

        This helper supports rule R2 when a task-only branch needs a synthetic class
        anchor before its nested tasks can be mapped as UML methods.
        """
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

    # ------------ UML Creation and Lookup ------------
    # Methods below create UML elements and store where each UVL feature ended up.

    def _get_existing_element_location(
        self, feature_name: str
    ) -> Optional[UmlElementLocation]:
        """Returns the UML location already created for one UVL feature.

        This helper lets several rules share the same feature-to-UML mapping after the
        target class or method was first created.
        """
        return self.element_locations.get(feature_name)

    def _get_or_create_uml_class(self, class_name: str) -> UmlClass:
        """Returns one UML class, creating it when needed.

        This helper supports rules R2, R3, and R4 by centralizing class creation in the
        target UML model before stereotypes, attributes, or methods are attached.
        """
        return self.uml.get_or_create_class(class_name)

    def _get_or_create_method(self, class_name: str, method_name: str) -> UmlMethod:
        """Returns one UML method inside a class, creating it when needed.

        This helper supports rule R2 when task features must become UML operations while
        still reusing methods that were already created for the same class.
        """
        existing_method = self.uml.get_method_from_class(class_name, method_name)
        if existing_method is not None:
            return existing_method
        return self.uml.add_method_to_class(class_name, method_name)

    def _store_class_location(self, feature_name: str, class_name: str) -> None:
        """Stores the UML class created for one UVL feature.

        This helper keeps the feature-to-class mapping available so later rules can keep
        enriching the same UML element without recomputing its placement.
        """
        self.element_locations[feature_name] = UmlElementLocation(class_name=class_name)

    def _store_method_location(
        self,
        feature_name: str,
        class_name: str,
        method_name: str,
    ) -> None:
        """Stores the UML method created for one UVL feature.

        This helper keeps the feature-to-method mapping available so later rules can add
        annotations or attributes to the method context created by rule R2.
        """
        self.element_locations[feature_name] = UmlElementLocation(
            class_name=class_name,
            method_name=method_name,
        )

    def _get_or_create_goal_class_for_task(
        self, task_feature: Feature
    ) -> Optional[UmlClass]:
        """Returns the UML class derived from the nearest goal of one task.

        This helper supports rule R2 when a task should become a method on the class
        associated with the closest goal ancestor in the UVL hierarchy.
        """
        goal_feature = self._get_nearest_goal_feature(task_feature.name)
        if goal_feature is None:
            return None
        return self._get_or_create_uml_class(goal_feature.name)

    def _get_or_create_helper_class_for_task(self, task_feature: Feature) -> UmlClass:
        """Returns the helper class used for the root task of one task-only branch.

        This helper supports rule R2 when a task branch has no goal parent and still
        needs a UML class that can own the generated branch methods.
        """
        helper_root = self._get_helper_root_task_feature(task_feature)
        return self._get_or_create_uml_class(helper_root.name)

    # ------------ UML Annotations and Attributes ------------
    # Methods below copy metadata, resources, attributes, and annotations into UML.

    def _add_feature_annotations(self, feature: Feature) -> None:
        """Adds actor and contribution annotations to the mapped UML element.

        This helper supports rule R1 by copying the relevant UVL metadata onto the UML
        class or method that was previously created for the same feature.
        """
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
        """Adds UVL feature attributes to the UML class associated with one feature.

        This helper supports rule R7 by transferring stored feature attributes into the
        generated UML class representation after locations are already known.
        """
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
        """Adds direct resource children of one helper task as UML attributes.

        This helper supports rule R2 by turning resource children into class attributes
        when a task-only branch is represented through a helper class.
        """
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
        """Adds one UML annotation for a mandatory or `or` group.

        This helper supports rule R8 by preserving UVL grouping semantics as notes on
        the UML class or method that represents the same feature.
        """
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
        """Adds one hardware-constraint annotation to quantum classes and drivers.

        This helper supports rule R5 by attaching quantum hardware constraints to the
        UML elements that represent quantum algorithms or integration drivers.
        """
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

    # ------------ UML Dependencies ------------
    # Methods below translate UVL requires constraints into UML dependencies.

    def _add_requires_dependency(self, source_name: str, target_name: str) -> None:
        """Adds one UML dependency with stereotype `requires`.

        This helper supports rule R6 by translating one stored UVL constraint into the
        dependency relation used by the generated UML model.
        """
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

    # ====== Public API ======
    # Methods below expose the ordered PIM-to-PSM rules and the final transformation entry point.

    # ------------ Transformation Rules ------------
    # Methods below apply the explicit PIM-to-PSM rules over the source UVL model.

    def apply_r1(self) -> None:
        """Applies rule R1 by transferring actor and contribution metadata into UML.

        This rule copies the relevant UVL annotations after the target UML elements are
        already available in the generated model.
        """
        for feature in self.uvl.get_features():
            self._add_feature_annotations(feature)

        logger.debug("PIM-to-PSM R1 applied: metadata annotations copied to UML")

    def apply_r2(self) -> None:
        """Applies rule R2 to transform goal, task, and resource features into UML.

        This rule creates the main class and method structure that the later PSM rules
        will enrich with stereotypes, dependencies, and annotations.
        """
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
        """Applies rule R3 to transform algorithm features into UML classes.

        This rule ensures algorithm features appear as classes in the target model and
        marks the quantum ones with the expected stereotype.
        """
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
        """Applies rule R4 to transform integration-model features into drivers.

        This rule creates the UML classes that represent integration concerns and marks
        them with the `QuantumDriver` stereotype in the target model.
        """
        for feature in self.uvl.get_features_by_category("@Integration_model"):
            uml_class = self._get_or_create_uml_class(feature.name)
            if "QuantumDriver" not in uml_class.stereotypes:
                uml_class.stereotypes.append("QuantumDriver")
            self._store_class_location(feature.name, uml_class.name)

        logger.debug(
            "PIM-to-PSM R4 applied: integration features converted to QuantumDriver classes"
        )

    def apply_r5(self) -> None:
        """Applies rule R5 to transform quantum hardware constraints into UML notes.

        This rule preserves hardware-related constraints by attaching them to the UML
        elements that represent quantum algorithms or integration drivers.
        """
        for feature in self.uvl.get_features_by_category("@Quantum_HW_constraint"):
            self._add_quantum_hw_annotation(feature)

        logger.debug(
            "PIM-to-PSM R5 applied: quantum hardware constraints added as annotations"
        )

    def apply_r6(self) -> None:
        """Applies rule R6 to transform UVL requires constraints into dependencies.

        This rule converts the stored UVL cross-feature constraints into UML dependency
        relations so the generated diagram preserves those requirements.
        """
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
        """Applies rule R7 to transform UVL feature attributes into UML attributes.

        This rule copies the feature-level data already present in the UVL model into
        the UML classes that represent the same transformed elements.
        """
        for feature in self.uvl.get_features():
            self._add_feature_attributes_to_class(feature)

        logger.debug("PIM-to-PSM R7 applied: feature attributes copied to UML classes")

    def apply_r8(self) -> None:
        """Applies rule R8 to transform mandatory and `or` groups into UML notes.

        This rule preserves UVL grouping semantics by recording them as annotations on
        the UML class or method mapped from each feature.
        """
        for feature in self.uvl.get_features():
            self._add_group_annotation(feature, "mandatory")
            self._add_group_annotation(feature, "or")

        logger.debug("PIM-to-PSM R8 applied: feature groups copied as UML annotations")

    def transform(self) -> UmlModel:
        """Runs the full PIM-to-PSM rule pipeline and returns the generated UML model.

        This method applies the rules in the required order so the final UML model is
        complete before rendering or metric calculations use it.
        """
        self.apply_r2()
        self.apply_r3()
        self.apply_r4()
        self.apply_r6()
        self.apply_r7()
        self.apply_r8()
        self.apply_r1()
        self.apply_r5()
        return self.uml
