"""Transformaciones desde UVL hacia diagramas PlantUML para el nivel PSM."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

from app.models.feature_tree import Constraint, FeatureNode
from .plant_uml_diagram_service import PlantUMLDiagramService


class PimToPsm:
    """Interpreta contenido UVL y produce diagramas de clases PlantUML."""

    SECTION_KEYS = {"primary", "quality"}

    def __init__(self) -> None:
        self.plantuml_service = PlantUMLDiagramService()

    def transform_uvl_content_to_plantuml_diagram(self, uvl_content: str) -> str:
        """Genera un diagrama PlantUML representando el contenido UVL dado."""

        if not uvl_content or not uvl_content.strip():
            raise ValueError("El contenido UVL no puede estar vacío...")

        feature_tree = self.parse_feature_hierarchy_from_uvl_content(uvl_content)
        constraints = self.parse_constraints_from_uvl_content(uvl_content)
        diagram_text = self.build_plantuml_diagram_from_feature_hierarchy_and_constraints(
            feature_tree, constraints
        )
        return diagram_text

    def parse_feature_hierarchy_from_uvl_content(self, uvl_content: str) -> List[FeatureNode]:
        """Extrae nodos de características desde un documento UVL."""

        stripped_lines: List[str] = []
        for original_line in uvl_content.splitlines():
            uncommented_line = self.remove_line_comments_from_uvl_text(original_line)
            stripped_line = uncommented_line.strip()
            stripped_lines.append(stripped_line)

        non_empty_lines: List[str] = []
        for stripped_line in stripped_lines:
            if stripped_line:
                non_empty_lines.append(stripped_line)

        features: List[FeatureNode] = []
        context_stack: List[Dict[str, FeatureNode | str]] = []
        inside_features_block = False

        for raw_line in non_empty_lines:
            current_line = raw_line

            if not inside_features_block and current_line.lower().startswith("features"):
                inside_features_block = True
                context_stack.append({"type": "block", "name": "features"})
                continue

            if current_line.lower().startswith("constraints"):
                break

            if not inside_features_block:
                continue

            if current_line == "}":
                if context_stack:
                    context_stack.pop()
                if not context_stack:
                    inside_features_block = False
                continue

            if current_line.endswith("{"):
                feature_name = current_line[:-1].strip()
                lowered_name = feature_name.lower()
                if lowered_name in self.SECTION_KEYS:
                    context_stack.append({"type": "section", "name": lowered_name})
                    continue

                node = FeatureNode(
                    name=feature_name,
                    section=self.determine_current_section_from_parsing_context_stack(context_stack),
                )
                parent = self.determine_current_feature_from_parsing_context_stack(context_stack)
                if parent is not None:
                    parent.children.append(node)
                else:
                    features.append(node)
                context_stack.append({"type": "feature", "node": node})
                continue

            lowered_line = current_line.lower()
            if lowered_line in self.SECTION_KEYS:
                context_stack.append({"type": "section", "name": lowered_line})
                continue

            node = FeatureNode(
                name=current_line,
                section=self.determine_current_section_from_parsing_context_stack(context_stack),
            )
            parent = self.determine_current_feature_from_parsing_context_stack(context_stack)
            if parent is not None:
                parent.children.append(node)
            else:
                features.append(node)

        return features

    def parse_constraints_from_uvl_content(self, uvl_content: str) -> List[Constraint]:
        """Extrae relaciones de tipo requiere y excluye desde un documento UVL."""

        constraints: List[Constraint] = []
        inside_constraints_block = False

        for raw_line in uvl_content.splitlines():
            uncommented_line = self.remove_line_comments_from_uvl_text(raw_line)
            stripped_line = uncommented_line.strip()
            if not stripped_line:
                continue

            if not inside_constraints_block and stripped_line.lower().startswith("constraints"):
                inside_constraints_block = True
                continue

            if inside_constraints_block:
                if stripped_line == "}":
                    break

                parts = stripped_line.split()
                if len(parts) >= 3:
                    relation = parts[1].lower()
                    if relation in {"requires", "excludes"}:
                        constraint: Constraint = {
                            "source": parts[0],
                            "type": relation,
                            "target": parts[2],
                        }
                        constraints.append(constraint)

        return constraints

    def remove_line_comments_from_uvl_text(self, line: str) -> str:
        """Elimina comentarios en línea presentes en una línea UVL."""

        comment_index = line.find("//")
        if comment_index == -1:
            return line
        uncommented_line = line[:comment_index]
        return uncommented_line

    def determine_current_section_from_parsing_context_stack(
        self, context_stack: Iterable[Dict[str, FeatureNode | str]]
    ) -> Optional[str]:
        """Obtiene la sección activa dentro del contexto de análisis."""

        reversed_stack = list(context_stack)[::-1]
        for context in reversed_stack:
            context_type = context.get("type")
            if context_type == "section":
                name_value = context.get("name")
                if name_value is None:
                    continue
                return str(name_value)
        return None

    def determine_current_feature_from_parsing_context_stack(
        self, context_stack: Iterable[Dict[str, FeatureNode | str]]
    ) -> Optional[FeatureNode]:
        """Recupera el nodo de característica activo desde el contexto."""

        reversed_stack = list(context_stack)[::-1]
        for context in reversed_stack:
            context_type = context.get("type")
            if context_type == "feature":
                node = context.get("node")
                if isinstance(node, FeatureNode):
                    return node
        return None

    def build_plantuml_diagram_from_feature_hierarchy_and_constraints(
        self, features: List[FeatureNode], constraints: List[Constraint]
    ) -> str:
        """Crea el texto del diagrama PlantUML para la estructura proporcionada."""

        class_lines: List[str] = []
        relation_lines: List[str] = []

        used_aliases: Dict[str, int] = {}
        alias_lookup: Dict[str, str] = {}

        for feature in features:
            self.add_feature_node_to_diagram_with_alias_management(
                feature,
                None,
                class_lines,
                relation_lines,
                used_aliases,
                alias_lookup,
            )

        for constraint in constraints:
            self.add_constraint_relation_to_diagram_lines(
                constraint,
                relation_lines,
                alias_lookup,
            )

        diagram_lines = [
            "@startuml",
            "!pragma layout smetana",
            "skinparam backgroundColor #FFFFFF",
            "skinparam classBackgroundColor #FFFFFF",
            "skinparam classBorderColor #4B6CC1",
            "skinparam classAttributeIconSize 0",
            "title Arquitectura Quantum-UML",
        ]

        for class_line in class_lines:
            diagram_lines.append(class_line)

        if relation_lines:
            diagram_lines.append("")
            for relation_line in relation_lines:
                diagram_lines.append(relation_line)

        diagram_lines.append("@enduml")
        diagram_text = "\n".join(diagram_lines)
        return diagram_text

    def add_feature_node_to_diagram_with_alias_management(
        self,
        node: FeatureNode,
        parent_alias: Optional[str],
        class_lines: List[str],
        relation_lines: List[str],
        used_aliases: Dict[str, int],
        alias_lookup: Dict[str, str],
    ) -> None:
        alias = self.generate_alias_for_feature_name(node.name, used_aliases)
        key = self.normalise_feature_name_to_key(node.name)
        if key not in alias_lookup:
            alias_lookup[key] = alias

        stereotype = "<<Feature>>"
        section_value = node.section or ""
        if section_value.lower() == "quality":
            stereotype = "<<QualityAttribute>>"

        class_line = f'class "{node.name}" as {alias} {stereotype}'
        class_lines.append(class_line)

        if parent_alias is not None:
            relation_line = f"{parent_alias} *-- {alias}"
            relation_lines.append(relation_line)

        for child in node.children:
            self.add_feature_node_to_diagram_with_alias_management(
                child,
                alias,
                class_lines,
                relation_lines,
                used_aliases,
                alias_lookup,
            )

    def add_constraint_relation_to_diagram_lines(
        self,
        constraint: Constraint,
        relation_lines: List[str],
        alias_lookup: Dict[str, str],
    ) -> None:
        source_alias = alias_lookup.get(self.normalise_feature_name_to_key(constraint["source"]))
        target_alias = alias_lookup.get(self.normalise_feature_name_to_key(constraint["target"]))
        if source_alias is None or target_alias is None:
            return
        label = constraint["type"].capitalize()
        relation_line = f"{source_alias} ..> {target_alias} : {label}"
        relation_lines.append(relation_line)

    def normalise_feature_name_to_key(self, value: str) -> str:
        cleaned_value = re.sub(r"[^0-9a-zA-Z]+", "", value)
        lowered_value = cleaned_value.lower()
        return lowered_value

    def generate_alias_for_feature_name(self, name: str, used_aliases: Dict[str, int]) -> str:
        base_value = re.sub(r"[^0-9a-zA-Z]+", " ", name)
        base_value = base_value.title().replace(" ", "")
        if not base_value:
            base_value = "Feature"
        current_counter = used_aliases.get(base_value, 0)
        if current_counter:
            alias_value = f"{base_value}{current_counter + 1}"
        else:
            alias_value = base_value
        used_aliases[base_value] = current_counter + 1
        return alias_value

    def build_plantuml_diagram_url_with_format(self, diagram: str, output_format: str = "svg") -> str:
        """Expone la construcción de URLs de PlantUML desde el servicio dedicado."""

        plantuml_url = self.plantuml_service.build_plantuml_server_url(diagram, output_format)
        return plantuml_url

    def encode_diagram_to_plantuml_service_format(self, diagram: str) -> str:
        """Expone la codificación de diagramas para el servidor PlantUML."""

        encoded_diagram = self.plantuml_service.encode_diagram_to_plantuml_server_format(diagram)
        return encoded_diagram
