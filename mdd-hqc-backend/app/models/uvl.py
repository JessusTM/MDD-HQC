"""UVL in-memory model and file writer."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


EXTENDED_FEATURE_MODEL_HQC: List[str] = [
    "@Functionality",
    "@Algorithm",
    "@Programming",
    "@Integration_model",
    "@Quantum_HW_constraint",
]

CATEGORY_LABELS: Dict[str, str] = {
    "@Functionality": "Functionality",
    "@Algorithm": "Algorithm",
    "@Programming": "Programming",
    "@Integration_model": "Integration_model",
    "@Quantum_HW_constraint": "Quantum_HW_constraint",
}


class Feature(BaseModel):
    category: str
    metadata: List[str] = Field(default_factory=list)
    name: str
    kind: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    mandatory_children: List[str] = Field(default_factory=list)
    or_children: List[str] = Field(default_factory=list)
    subgroup: Optional[str] = None


class UVL:
    FILE_NAME = Path("data/model.uvl")

    def __init__(self):
        self.namespace: str = "MDD-HQC"
        self.features: List[Feature] = []
        self.constraints: List[str] = []
        self.contributions: List[str] = []
        self.global_comments: List[str] = []
        self.parent_by_child: Dict[str, str] = {}

    def create_file(self) -> None:
        self.FILE_NAME.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Writing UVL file: path=%s, features=%s, constraints=%s",
            self.FILE_NAME,
            len(self.features),
            len(self.constraints),
        )

        with self.FILE_NAME.open("w", encoding="utf-8") as file:
            self._write_features(file)
            self._write_constraints(file)

    def _write_features(self, file) -> None:
        file.write("features\n")

        for category in EXTENDED_FEATURE_MODEL_HQC:
            if category == "@Algorithm":
                self._write_algorithm_category(file)
                continue

            features = self._get_root_features(category=category)
            if not features:
                continue

            file.write(f"    {CATEGORY_LABELS[category]}\n")
            self._write_group_block(file, features, indent=8, group_name="mandatory")

    def _write_algorithm_category(self, file) -> None:
        base_features = self._get_root_features(category="@Algorithm")
        classical_features = self._get_root_features(
            category="@Algorithm",
            subgroup="Classical",
        )
        quantum_features = self._get_root_features(
            category="@Algorithm",
            subgroup="Quantum",
        )

        if not base_features and not classical_features and not quantum_features:
            return

        file.write("    Algorithm\n")

        if base_features:
            self._write_group_block(
                file,
                base_features,
                indent=8,
                group_name="mandatory",
            )

        if classical_features:
            file.write("        Classical\n")
            self._write_group_block(
                file,
                classical_features,
                indent=12,
                group_name="mandatory",
            )

        if quantum_features:
            file.write("        Quantum\n")
            self._write_group_block(
                file,
                quantum_features,
                indent=12,
                group_name="mandatory",
            )

    def _write_group_block(
        self,
        file,
        features: List[Feature],
        indent: int,
        group_name: str,
    ) -> None:
        indentation = " " * indent
        file.write(f"{indentation}{group_name}\n")

        for feature in features:
            self._write_feature(file, feature, indent=indent + 4)

    def _write_feature(self, file, feature: Feature, indent: int) -> None:
        indentation = " " * indent

        for line in feature.metadata:
            file.write(f"{indentation}# {line}\n")

        file.write(f"{indentation}{feature.name}\n")

        if feature.kind or feature.attributes:
            file.write(f"{indentation}{{\n")

            if feature.kind:
                file.write(f'{indentation}    kind "{feature.kind}"\n')

            for attribute_name, attribute_value in feature.attributes.items():
                file.write(f'{indentation}    {attribute_name} "{attribute_value}"\n')

            file.write(f"{indentation}}}\n")

        if feature.mandatory_children:
            child_features = self._get_child_features(feature.mandatory_children)
            self._write_group_block(
                file,
                child_features,
                indent=indent + 4,
                group_name="mandatory",
            )

        if feature.or_children:
            child_features = self._get_child_features(feature.or_children)
            self._write_group_block(
                file,
                child_features,
                indent=indent + 4,
                group_name="or",
            )

    def _write_constraints(self, file) -> None:
        if not self.constraints:
            return

        file.write("\nconstraints\n")
        for constraint in self.constraints:
            file.write(f"    {constraint}\n")

    def _get_root_features(
        self,
        category: str,
        subgroup: Optional[str] = None,
    ) -> List[Feature]:
        result: List[Feature] = []

        for feature in self.features:
            if feature.category != category:
                continue
            if subgroup is not None and feature.subgroup != subgroup:
                continue
            if subgroup is None and feature.subgroup is not None:
                continue
            if feature.name in self.parent_by_child:
                continue
            result.append(feature)

        return result

    def _get_child_features(self, child_names: List[str]) -> List[Feature]:
        result: List[Feature] = []

        for child_name in child_names:
            child_feature = self.get_feature(child_name)
            if child_feature is None:
                continue
            result.append(child_feature)

        return result

    def add_feature(
        self,
        category: str,
        metadata: Optional[List[str]],
        name: str,
        kind: Optional[str],
        attributes: Optional[Dict[str, str]] = None,
        subgroup: Optional[str] = None,
    ) -> Feature:
        category = (category or "").strip()
        if category not in EXTENDED_FEATURE_MODEL_HQC:
            category = "@Functionality"

        existing_feature = self.get_feature(name=name, category=category)
        if existing_feature is not None:
            if metadata:
                for comment in metadata:
                    if comment not in existing_feature.metadata:
                        existing_feature.metadata.append(comment)
            if kind and not existing_feature.kind:
                existing_feature.kind = kind
            if attributes:
                existing_feature.attributes.update(attributes)
            if subgroup and not existing_feature.subgroup:
                existing_feature.subgroup = subgroup
            return existing_feature

        feature = Feature(
            category=category,
            metadata=metadata or [],
            name=name,
            kind=kind,
            attributes=attributes or {},
            subgroup=subgroup,
        )
        self.features.append(feature)
        return feature

    def add_comment_to_feature(
        self, feature_name: str, category: str, comment: str
    ) -> None:
        feature = self.get_feature(name=feature_name, category=category)
        if feature is None:
            return
        if comment and comment not in feature.metadata:
            feature.metadata.append(comment)

    def add_global_comment(self, comment: str) -> None:
        comment = comment.strip()
        if not comment:
            return
        if comment in self.global_comments:
            return
        self.global_comments.append(comment)

    def add_attribute_to_feature(
        self,
        feature_name: str,
        category: str,
        attribute_name: str,
        attribute_value: str,
    ) -> None:
        feature = self.get_feature(name=feature_name, category=category)
        if feature is None:
            return
        feature.attributes[attribute_name] = attribute_value

    def add_constraint(self, expr: str) -> None:
        expr = expr.strip()
        if not expr:
            return
        if expr in self.constraints:
            return
        self.constraints.append(expr)

    def add_contribution(self, comment: str) -> None:
        comment = comment.strip()
        if not comment:
            return
        if comment in self.contributions:
            return
        self.contributions.append(comment)

    def add_mandatory_child(self, parent_name: str, child_name: str) -> None:
        parent_feature = self.get_feature(parent_name)
        child_feature = self.get_feature(child_name)

        if parent_feature is None or child_feature is None:
            return

        previous_parent = self.parent_by_child.get(child_name)
        if previous_parent and previous_parent != parent_name:
            return

        if child_name in parent_feature.or_children:
            parent_feature.or_children.remove(child_name)
        if child_name not in parent_feature.mandatory_children:
            parent_feature.mandatory_children.append(child_name)
        self.parent_by_child[child_name] = parent_name

    def add_or_child(self, parent_name: str, child_name: str) -> None:
        parent_feature = self.get_feature(parent_name)
        child_feature = self.get_feature(child_name)

        if parent_feature is None or child_feature is None:
            return

        previous_parent = self.parent_by_child.get(child_name)
        if previous_parent and previous_parent != parent_name:
            return

        if child_name in parent_feature.mandatory_children:
            parent_feature.mandatory_children.remove(child_name)
        if child_name not in parent_feature.or_children:
            parent_feature.or_children.append(child_name)
        self.parent_by_child[child_name] = parent_name

    def get_features(self) -> List[Feature]:
        return self.features

    def get_features_by_category(self, category: str) -> List[Feature]:
        result: List[Feature] = []
        for feature in self.features:
            if feature.category == category:
                result.append(feature)
        return result

    def get_feature(
        self, name: str, category: Optional[str] = None
    ) -> Optional[Feature]:
        name = (name or "").strip()
        normalized_category = None
        if category is not None:
            normalized_category = (category or "").strip()

        if not name:
            return None

        for feature in self.features:
            if feature.name != name:
                continue
            if (
                normalized_category is not None
                and feature.category != normalized_category
            ):
                continue
            return feature

        return None

    def get_constraints(self) -> List[str]:
        return self.constraints

    def get_contributions(self) -> List[str]:
        return self.contributions

    def get_global_comments(self) -> List[str]:
        return self.global_comments
