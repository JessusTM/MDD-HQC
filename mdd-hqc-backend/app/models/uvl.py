from pathlib import Path
from typing import Dict, List, Optional

from app.models.feature import Feature


EXTENDED_FEATURE_MODEL_HQC: List[str] = [
    "@Functionality",
    "@Algorithm",
    "@Programming",
    "@Integration_model",
    "@Quantum_HW_constraint",
]


class UVL:
    """
    In-memory representation of a UVL model (HQC extended feature model dialect).

    Conventions used in this prototype:
    - category      : UVL category tag (e.g., @Functionality).
    - features      : collection of Feature objects already classified by category.
    - constraints   : UVL expressions written under `constraints { ... }`.
    - contributions : informational lines written as comments (for now).
    - or_groups     : OR-group relationships stored as parent -> [children] (written as comments for now).
    """

    FILE_NAME = Path("app/data/model.uvl")

    def __init__(self):
        """Creates an empty UVL model ready to receive features, constraints, etc."""
        self.namespace: str = "MDD-HQC"
        self.features: List[Feature] = []
        self.constraints: List[str] = []
        self.contributions: List[str] = []
        self.or_groups: Dict[str, List[str]] = {}

    # ====== CREATE FILE ======
    def create_file(self) -> None:
        """
        Writes the final UVL file to `FILE_NAME`.

        High-level flow:
        1) Namespace header
        2) Categories and their features
        3) Constraints block
        4) Contributions (comments)
        5) OR-groups (comments)
        6) Namespace closing brace
        """
        # Ensure output directory exists
        self.FILE_NAME.parent.mkdir(parents=True, exist_ok=True)

        # Write UVL deterministically
        with self.FILE_NAME.open("w", encoding="utf-8") as file:
            self._write_namespace_header(file)
            self._write_categories(file)
            self._write_constraints(file)
            self._write_contributions(file)
            self._write_or_groups(file)
            file.write("}\n")

    # ====== PRIVATE: WRITERS ======
    def _write_namespace_header(self, file) -> None:
        """Writes `namespace X {` header."""
        file.write(f"namespace {self.namespace} {{\n\n")

    def _write_categories(self, file) -> None:
        """
        Writes HQC extended categories and their associated features.

        Iterates over the allowed category set, then collects features belonging
        to each category and writes them inside the category block.
        """
        for category in EXTENDED_FEATURE_MODEL_HQC:
            # Collect features for this category (expanded for readability)
            category_features: List[Feature] = []
            for feature in self.features:
                if feature.category == category:
                    category_features.append(feature)

            # Skip empty categories
            if not category_features:
                continue

            # Category block
            file.write(f"  {category} {{\n")
            for feature in category_features:
                self._write_feature(file, feature)
            file.write("  }\n\n")

    def _write_feature(self, file, feature: Feature) -> None:
        """
        Writes a single UVL feature.

        Cases:
        - No `kind` and no `attributes`: prints a single-line feature.
        - Has `kind` and/or `attributes`: prints a feature block `{ ... }`.
        """
        # Feature comments (metadata): traceability, actor, resources, etc.
        for line in feature.metadata:
            file.write(f"    # {line}\n")

        has_kind = bool(feature.kind)
        has_attributes = bool(feature.attributes)

        # Simple feature line (no block)
        if not has_kind and not has_attributes:
            file.write(f"    {feature.name}\n")
            return

        # Block feature (kind + attributes)
        file.write(f"    {feature.name} {{\n")

        if feature.kind:
            file.write(f'      kind "{feature.kind}"\n')

        # Write feature attributes
        for attribute_name, attribute_value in feature.attributes.items():
            file.write(f'      {attribute_name} "{attribute_value}"\n')

        file.write("    }\n")

    def _write_constraints(self, file) -> None:
        """
        Writes the `constraints { ... }` block if any constraints exist.

        Each string in `self.constraints` is written as a UVL line.
        """
        if not self.constraints:
            return

        file.write("  constraints {\n")
        for constraint in self.constraints:
            file.write(f"    {constraint}\n")
        file.write("  }\n\n")

    def _write_contributions(self, file) -> None:
        """
        Writes contributions as comments (not executable UVL syntax).

        This keeps the file readable without enforcing an additional grammar
        while the prototype evolves.
        """
        if not self.contributions:
            return

        file.write("  # Contributions\n")
        for contribution in self.contributions:
            file.write(f"  # {contribution}\n")
        file.write("\n")

    def _write_or_groups(self, file) -> None:
        """
        Writes OR-groups as comments (parent -> children).

        Note: if you later define a concrete UVL syntax for OR-groups,
        this is the natural place to change the output format.
        """
        if not self.or_groups:
            return

        file.write("  # OR-groups\n")
        for parent_name, children_names in self.or_groups.items():
            if not children_names:
                continue
            file.write(f"  # {parent_name} -> {', '.join(children_names)}\n")
        file.write("\n")

    # ====== PUBLIC API (used by other modules) ======
    def add_feature(
        self,
        category: str,
        metadata: Optional[List[str]],
        name: str,
        kind: Optional[str],
        attributes: Optional[Dict[str, str]],
    ) -> Feature:
        """
        Adds a feature to the model.

        Behavior:
        - Normalizes `category` (strip) and falls back to @Functionality if invalid.
        - Enforces invariants: `metadata` is always List[str], `attributes` always Dict[str, str].
        """
        # Normalize to avoid common issues (spaces, None, etc.)
        category = (category or "").strip()

        # Fallback if category is not part of the HQC extended feature model
        if category not in EXTENDED_FEATURE_MODEL_HQC:
            category = "@Functionality"

        # Invariants: never store None
        feature = Feature(
            category=category,
            metadata=metadata or [],
            name=name,
            kind=kind,
            attributes=attributes or {},
        )
        self.features.append(feature)
        return feature

    def add_comment_to_feature(
        self, feature_name: str, category: str, comment: str
    ) -> None:
        """Adds one comment line (metadata) to an existing feature."""
        category = (category or "").strip()

        for feature in self.features:
            if feature.name == feature_name and feature.category == category:
                if comment:
                    feature.metadata.append(comment)
                return

    def add_attribute_to_feature(
        self,
        feature_name: str,
        category: str,
        attribute_name: str,
        attribute_value: str,
    ) -> None:
        """Adds (or overwrites) one attribute inside the feature's attribute block."""
        category = (category or "").strip()

        for feature in self.features:
            if feature.name == feature_name and feature.category == category:
                feature.attributes[attribute_name] = attribute_value
                return

    def add_constraint(self, expr: str) -> None:
        """
        Adds a UVL constraint line to the `constraints` block.

        The expression is stored as-is after stripping whitespace.
        """
        expr = expr.strip()
        if expr:
            self.constraints.append(expr)

    def add_contribution(self, comment: str) -> None:
        """Adds a contribution line that will be written as a comment."""
        comment = comment.strip()
        if comment:
            self.contributions.append(comment)

    def add_or_group(self, parent_name: str, child_name: str) -> None:
        """
        Adds an OR-group relationship in memory: parent -> child.

        It is currently written as a comment for traceability/debugging.
        """
        if parent_name not in self.or_groups:
            self.or_groups[parent_name] = []

        if child_name not in self.or_groups[parent_name]:
            self.or_groups[parent_name].append(child_name)
