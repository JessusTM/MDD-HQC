"""UVL in-memory model and file writer used across parsing and transformation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ------------ Category Metadata ------------
# Constants below define the UVL categories recognized by the backend pipeline.
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
    """Represents one feature stored inside the in-memory UVL model.

    This model keeps the structural and descriptive data of one feature together so the
    rest of the backend can build, inspect, and export the UVL hierarchy consistently.
    """

    category: str
    metadata: List[str] = Field(default_factory=list)
    name: str
    kind: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    mandatory_children: List[str] = Field(default_factory=list)
    or_children: List[str] = Field(default_factory=list)
    subgroup: Optional[str] = None


class UVL:
    """Stores the in-memory UVL model used across parsing, interaction, and export.

    This class centralizes features, hierarchy relations, constraints, and comments so
    services and transformations can work on one consistent representation of the model.
    """

    FILE_NAME = Path("data/model.uvl")

    def __init__(self):
        """Initializes the empty UVL model containers used by the backend flow.

        These collections hold the feature tree, constraints, and comments that later
        parsing, interaction, and export steps will read or update.
        """

        self.namespace: str = "MDD-HQC"
        self.features: List[Feature] = []
        self.constraints: List[str] = []
        self.contributions: List[str] = []
        self.global_comments: List[str] = []
        self.parent_by_child: Dict[str, str] = {}

    # ====== Private Helpers ======
    # Internal methods below resolve UVL structure before the public API writes or queries it.

    # ------------ UVL File Writing ------------
    # Methods below turn the in-memory UVL model into the exported `.uvl` file structure.
    def create_file(self) -> None:
        """Writes the current in-memory UVL model to the default output file.

        This method is used when the backend needs a persisted UVL artifact after the
        model has already been assembled in memory.

        For example, after writing the file, the exported model can contain:
            @Functionality {
                EncryptData
            }
        """
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
        """Writes the feature section of the current UVL model into one file handle.

        This helper is used by file creation so the visible feature hierarchy of the
        model can be exported category by category in the expected UVL layout.
        """
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
        """Writes the algorithm category, including classical and quantum subgroups.

        This helper is used so the exported model can keep the special algorithm layout
        required when features are split across subgroup branches.
        """
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
        """Writes one grouped child block such as `mandatory` or `or` to the UVL file.

        This helper supports the methods that export the visible model structure by
        preserving grouped child relationships in the generated hierarchy.
        """
        indentation = " " * indent
        file.write(f"{indentation}{group_name}\n")

        for feature in features:
            self._write_feature(file, feature, indent=indent + 4)

    def _write_feature(self, file, feature: Feature, indent: int) -> None:
        """Writes one stored feature and its nested content to the UVL file.

        This helper is responsible for exporting the visible shape of one feature,
        including metadata, attributes, and child groups, when the model is serialized.
        """
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
        """Writes the constraint section of the UVL model when constraints exist.

        This helper is used during export so the final file preserves the cross-feature
        rules already stored in memory.
        """
        if not self.constraints:
            return

        file.write("\nconstraints\n")
        for constraint in self.constraints:
            file.write(f"    {constraint}\n")

    # ------------ Hierarchy Resolution ------------
    # Methods below reconstruct parent-child structure from the features stored in memory.
    def _get_root_features(
        self,
        category: str,
        subgroup: Optional[str] = None,
    ) -> List[Feature]:
        """Returns the root features that belong to one category and optional subgroup.

        This helper is used by the writer so the model can start each exported branch
        from the features that do not already have a parent inside the hierarchy.

        For example, it can return the feature behind:
            @Functionality {
                Security
            }
        """
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
        """Returns the child feature objects that match the provided feature names.

        This helper is used by the export routines so public model operations can turn
        stored child references into full feature nodes before writing the hierarchy.
        """
        result: List[Feature] = []

        for child_name in child_names:
            child_feature = self.get_feature(child_name)
            if child_feature is None:
                continue
            result.append(child_feature)

        return result

    # ====== Public API ======
    # Methods below let the rest of the backend read or modify the in-memory UVL model.

    # ------------ Feature Registration ------------
    # Methods below create features and attach comments, attributes, and hierarchy links.
    def add_feature(
        self,
        category: str,
        metadata: Optional[List[str]],
        name: str,
        kind: Optional[str],
        attributes: Optional[Dict[str, str]] = None,
        subgroup: Optional[str] = None,
    ) -> Feature:
        """Adds a feature to the UVL model or reuses the existing stored one.

        This method keeps the model consistent by merging repeated feature definitions
        instead of creating duplicates during parsing or interaction updates.

        For example, after adding a functionality feature, the model can contain:
            @Functionality {
                EncryptData
            }
        """
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
        """Adds one metadata comment to a stored feature when it already exists.

        This method enriches the model with feature-level annotations that later steps
        can inspect or export alongside the visible UVL hierarchy.

        For example, the model can contain:
            @Functionality {
                # actor: Analyst
                EncryptData
            }
        """
        feature = self.get_feature(name=feature_name, category=category)
        if feature is None:
            return
        if comment and comment not in feature.metadata:
            feature.metadata.append(comment)

    def add_global_comment(self, comment: str) -> None:
        """Adds one model-wide comment to the UVL draft when it is not duplicated.

        This method keeps general notes attached to the model so they remain available
        even when they do not belong to a single feature node.
        """
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
        """Adds or updates one attribute on a stored feature.

        This method lets the model capture feature properties that later exports and
        transformations need to read from the UVL structure.

        For example, the model can contain:
            @Programming {
                Python {
                    version "3.12"
                }
            }
        """
        feature = self.get_feature(name=feature_name, category=category)
        if feature is None:
            return
        feature.attributes[attribute_name] = attribute_value

    def add_constraint(self, expr: str) -> None:
        """Adds one cross-feature constraint to the UVL model when it is valid and new.

        This method stores model-wide rules so the exported UVL file can preserve the
        dependencies that exist beyond the tree structure itself.

        For example, the model can contain:
            constraints
                EncryptData => Python
        """
        expr = expr.strip()
        if not expr:
            return
        if expr in self.constraints:
            return
        self.constraints.append(expr)

    def add_contribution(self, comment: str) -> None:
        """Adds one contribution note to the UVL model when it is valid and new.

        This method stores contribution metadata separately so other backend steps can
        reuse these notes while building or transforming the model.
        """
        comment = comment.strip()
        if not comment:
            return
        if comment in self.contributions:
            return
        self.contributions.append(comment)

    def add_mandatory_child(self, parent_name: str, child_name: str) -> None:
        """Registers one mandatory child relation between two stored features.

        This method preserves the main parent-child hierarchy of the model so exports
        and transformations can rely on the same structural relationship.

        For example, after linking both features, the model can contain:
            @Functionality {
                Security {
                    mandatory {
                        EncryptData
                    }
                }
            }
        """
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
        """Registers one `or` child relation between two stored features.

        This method records alternative branches in the UVL hierarchy so the model can
        later export or transform grouped choices correctly.

        For example, after linking both features, the model can contain:
            @Programming {
                Runtime {
                    or {
                        Python
                        QSharp
                    }
                }
            }
        """
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

    # ------------ Model Queries ------------
    # Methods below expose the stored feature sets, constraints, and comments to other layers.
    def get_features(self) -> List[Feature]:
        """Returns the full list of features stored in the UVL model.

        This query lets other backend steps traverse the current feature catalog when
        they need to inspect or transform the model as a whole.
        """
        return self.features

    def get_features_by_category(self, category: str) -> List[Feature]:
        """Returns the features that belong to the requested UVL category.

        This query helps the model expose one logical slice of the feature set so later
        rules can work only with the category they are responsible for.

        For example, it can return the features stored under:
            @Algorithm {
                QuantumSearch
            }
        """
        result: List[Feature] = []
        for feature in self.features:
            if feature.category == category:
                result.append(feature)
        return result

    def get_feature(
        self, name: str, category: Optional[str] = None
    ) -> Optional[Feature]:
        """Returns the stored feature that matches the requested name and category.

        This lookup helps the UVL model reuse existing nodes instead of duplicating them
        when other operations need to update or connect the same feature.

        For example, it can resolve `EncryptData` from:
            @Functionality {
                EncryptData
            }
        """
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
        """Returns the constraints currently stored in the UVL model.

        This query gives later services access to the model-wide rules that complement
        the visible feature hierarchy.
        """
        return self.constraints

    def get_contributions(self) -> List[str]:
        """Returns the contribution notes stored in the UVL model.

        This query exposes contribution metadata so interaction and transformation steps
        can reuse it without scanning the whole feature structure again.
        """
        return self.contributions

    def get_global_comments(self) -> List[str]:
        """Returns the global comments attached to the UVL model.

        This query keeps model-wide notes available to any step that needs contextual
        information beyond individual features or constraints.
        """
        return self.global_comments
