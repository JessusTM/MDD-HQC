from pathlib import Path
from typing import Dict, List, Optional
from app.models.feature import Feature


class UVL:
    FILE_NAME = Path("app/data/model.uvl")

    def __init__(self):
        self.namespace          : str           = "MDD-HQC"
        self.features           : List[Feature] = []
        self.constraints        : List[str]     = [] 
        self.allowed_categories : List[str]     = [
            "@Functionality",
            "@Algorithm",
            "@Programming",
            "@Integration_model",
            "@Quantum_HW_constraint",
        ]

    def clear(self):
        self.features    = []
        self.constraints = []

    def add_feature(
        self,
        name        : str,
        category    : str,
        kind        : Optional[str]             = None,
        attributes  : Optional[Dict[str, str]]  = None,
        comments    : Optional[List[str]]       = None,
    ) -> Feature:
        if category not in self.allowed_categories : category = "@Functionality"

        feature = Feature(
            name        = name,
            category    = category,
            kind        = kind,
            attributes  = attributes or {},
            comments    = comments or [],
        )
        self.features.append(feature)
        return feature

    def add_comment_to_feature(self, feature_name: str, category: str, comment: str):
        for feat in self.features:
            if feat.name == feature_name and feat.category == category:
                feat.comments.append(comment)
                return

    def add_attribute_to_feature(
        self,
        feature_name    : str,
        category        : str,
        attr_name       : str,
        attr_value      : str,
    ):
        for feat in self.features:
            if feat.name == feature_name and feat.category == category:
                feat.attributes[attr_name] = attr_value
                return

    def add_constraint(self, expr: str) -> None:
        expr = expr.strip()
        if expr:
            self.constraints.append(expr)

    # ====== CREATE FILE ======
    def create_file(self) -> None:
        self.FILE_NAME.parent.mkdir(parents=True, exist_ok=True)
        with self.FILE_NAME.open("w", encoding="utf-8") as file:
            self._write_namespace_header(file)
            self._write_categories(file)
            self._write_constraints(file)
            file.write("}\n")

    def _write_namespace_header(self, file) -> None:
        file.write(f"namespace {self.namespace} {{\n\n")

    def _write_categories(self, file) -> None:
        for category in self.allowed_categories:
            category_features = [f for f in self.features if f.category == category]
            if not category_features:
                continue

            file.write(f"  {category} {{\n")
            for feat in category_features:
                self._write_feature(file, feat)
            file.write("  }\n\n")

    def _write_feature(self, file, feat: Feature) -> None:
        for comment in feat.comments:
            file.write(f"    // {comment}\n")

        if not feat.kind and not feat.attributes:
            file.write(f"    {feat.name}\n")
            return

        file.write(f"    {feat.name} {{\n")
        if feat.kind:
            file.write(f'      kind "{feat.kind}"\n')
        for attr_name, attr_value in feat.attributes.items():
            file.write(f'      {attr_name} "{attr_value}"\n')
        file.write("    }\n")

    def _write_constraints(self, file) -> None:
        if not self.constraints:
            return

        file.write("  constraints {\n")
        for c in self.constraints:
            file.write(f"    {c}\n")
        file.write("  }\n")
