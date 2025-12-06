from typing import Dict
from app.models.uvl import UVL
from app.models.uml import (
    UmlModel,
    UmlClass,
    UmlMethod,
    UmlAttribute,
    UmlDependency,
)


class PimToPsm:
    def __init__(self, uvl_model: UVL):
        self.uvl_model = uvl_model
        self.uml_model = UmlModel(name=uvl_model.namespace)
        self.classes_by_name: Dict[str, UmlClass] = {}


    def transform(self) -> UmlModel:
        self.apply_q2()
        self.apply_q3()
        self.apply_q4()
        self.apply_q7()
        self.apply_q1()
        self.apply_q6()
        self.apply_q5()
        return self.uml_model

    def get_or_create_class(self, class_name: str) -> UmlClass:
        existing = self.classes_by_name.get(class_name)
        if existing is not None:
            return existing

        new_class = self.uml_model.get_or_create_class(class_name)
        self.classes_by_name[class_name] = new_class
        return new_class

    def apply_q1(self) -> None:
        for feature in self.uvl_model.features:
            target_class = self.classes_by_name.get(feature.name)
            if target_class is None:
                continue

            for comment_text in feature.comments:
                target_class.add_comment(comment_text)

    def apply_q2(self) -> None:
        for feature in self.uvl_model.features:
            if feature.category != "@Functionality":
                continue

            if feature.kind == "goal":
                self.get_or_create_class(feature.name)

            if feature.kind == "task":
                parent_class = self.get_or_create_class(feature.name)
                method = UmlMethod(name=feature.name)
                parent_class.add_method(method)

    def apply_q3(self) -> None:
        for feature in self.uvl_model.features:
            if feature.category != "@Algorithm":
                continue

            algorithm_class = self.get_or_create_class(feature.name)
            if "Algorithm" not in algorithm_class.stereotypes:
                algorithm_class.stereotypes.append("Algorithm")

    def apply_q4(self) -> None:
        for feature in self.uvl_model.features:
            if feature.category != "@Integration_model":
                continue

            driver_class = self.get_or_create_class(feature.name)
            if "QuantumDriver" not in driver_class.stereotypes:
                driver_class.stereotypes.append("QuantumDriver")

    def apply_q5(self) -> None:
        constraint_values: Dict[str, str] = {}

        for feature in self.uvl_model.features:
            if feature.category != "@Quantum_HW_constraint":
                continue

            has_attributes = False
            for attribute_name, attribute_value in feature.attributes.items():
                constraint_values[attribute_name] = attribute_value
                has_attributes = True

            if not has_attributes:
                constraint_values[feature.name] = "true"

        if not constraint_values:
            return

        for uml_class in self.uml_model.classes.values():
            has_relevant_stereotype = any(
                s in {"Algorithm", "QuantumDriver"} for s in uml_class.stereotypes
            )
            if not has_relevant_stereotype:
                continue

            for key, value in constraint_values.items():
                uml_class.add_tagged_value(key, value)

    def apply_q6(self) -> None:
        for constraint_text in self.uvl_model.constraints:
            text = constraint_text.strip()
            if "=>" not in text:
                continue

            parts = text.split("=>", 1)
            left_part = parts[0].strip()
            right_part = parts[1].strip()

            if left_part == "" or right_part == "":
                continue

            client_class = self.get_or_create_class(left_part)
            supplier_class = self.get_or_create_class(right_part)

            dependency = UmlDependency(
                source=client_class.name,
                target=supplier_class.name,
                stereotype="requires",
            )
            self.uml_model.add_dependency(dependency)

    def apply_q7(self) -> None:
        for feature in self.uvl_model.features:
            target_class = self.classes_by_name.get(feature.name)
            if target_class is None:
                continue

            for attribute_name, attribute_value in feature.attributes.items():
                uml_attribute = UmlAttribute(
                    name=attribute_name,
                    type="String",
                )
                target_class.add_attribute(uml_attribute)
                target_class.add_tagged_value(attribute_name, attribute_value)

