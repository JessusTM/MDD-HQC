"""Calcula métricas útiles derivadas de los distintos procesos de transformación."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from app.models.feature_tree import FeatureNode
from app.models.metrics import (
    ArchitectureMetrics,
    CimToPimMetricsBundle,
    IStarMetrics,
    PimToPsmMetricsBundle,
    UvlMetrics,
)
from app.models.transformation_result import TransformationResult


class TransformationMetricsCalculator:
    """Evalúa los resultados de cada transformación para construir métricas legibles."""

    GOAL_NODE_TYPES = {"goal"}
    SOFTGOAL_NODE_TYPES = {"softgoal"}
    RESOURCE_NODE_TYPES = {"resource"}
    TASK_NODE_TYPES = {"task"}

    PLANTUML_CLASS_PATTERN = re.compile(r"\bclass\s+[^\s{]+", re.IGNORECASE)
    PLANTUML_CLASS_BLOCK_PATTERN = re.compile(r"class\s+[^\{]+\{([\s\S]*?)\}", re.IGNORECASE)

    def build_cim_to_pim_metrics_bundle(
        self,
        model: Dict[str, List[Dict[str, Any]]],
        transformation_result: TransformationResult,
        duration_ms: float,
    ) -> CimToPimMetricsBundle:
        """Genera métricas consolidadas para el flujo CIM → PIM."""

        nodes = model.get("nodes", [])
        goals_count = self.count_nodes_by_type(nodes, self.GOAL_NODE_TYPES)
        softgoals_count = self.count_nodes_by_type(nodes, self.SOFTGOAL_NODE_TYPES)
        resources_count = self.count_nodes_by_type(nodes, self.RESOURCE_NODE_TYPES)
        tasks_count = self.count_nodes_by_type(nodes, self.TASK_NODE_TYPES)

        istar_metrics = IStarMetrics(
            transformation_time_ms=duration_ms,
            goals_count=goals_count,
            softgoals_count=softgoals_count,
            resources_count=resources_count,
            tasks_count=tasks_count,
        )

        features_primary = transformation_result.features.get("primary", [])
        features_quality = transformation_result.features.get("quality", [])
        features_count = len(features_primary) + len(features_quality)
        constraints_count = len(transformation_result.restrictions)

        total_goals = goals_count + softgoals_count
        goals_converted_percent = self.calculate_percentage(features_count, total_goals)

        semantic_loss_percent = self.calculate_semantic_loss(
            features_count=features_count,
            constraints_count=constraints_count,
            goals_count=goals_count,
            softgoals_count=softgoals_count,
            tasks_count=tasks_count,
            resources_count=resources_count,
        )

        uvl_metrics = UvlMetrics(
            transformation_time_ms=duration_ms,
            features_count=features_count,
            constraints_count=constraints_count,
            goals_converted_percent=goals_converted_percent,
            semantic_loss_percent=semantic_loss_percent,
        )

        return CimToPimMetricsBundle(istar=istar_metrics, uvl=uvl_metrics)

    def build_pim_to_psm_metrics_bundle(
        self,
        diagram: str,
        duration_ms: float,
        feature_nodes: Iterable[FeatureNode],
        context_metrics: Optional[Dict[str, Optional[int]]],
    ) -> PimToPsmMetricsBundle:
        """Calcula las métricas asociadas al diagrama PlantUML resultante."""

        classes_count = self.count_classes_in_plantuml_diagram(diagram)
        attributes_count = self.count_attributes_in_plantuml_diagram(diagram)
        methods_count = self.count_methods_in_plantuml_diagram(diagram)

        features_count = self.count_feature_nodes(feature_nodes)

        context_features = self.extract_context_value(context_metrics, "features_count")
        if context_features is None:
            context_features = features_count
        features_to_classes_percent = self.calculate_percentage(classes_count, context_features)
        tasks_to_methods_percent = self.calculate_percentage(
            methods_count, self.extract_context_value(context_metrics, "tasks_count")
        )
        resources_to_attributes_percent = self.calculate_percentage(
            attributes_count, self.extract_context_value(context_metrics, "resources_count")
        )

        semantic_loss_percent = self.calculate_architecture_semantic_loss(
            features_to_classes_percent,
            tasks_to_methods_percent,
            resources_to_attributes_percent,
        )

        architecture_metrics = ArchitectureMetrics(
            transformation_time_ms=duration_ms,
            classes_count=classes_count,
            attributes_count=attributes_count,
            methods_count=methods_count,
            features_to_classes_percent=features_to_classes_percent,
            tasks_to_methods_percent=tasks_to_methods_percent,
            resources_to_attributes_percent=resources_to_attributes_percent,
            semantic_loss_percent=semantic_loss_percent,
        )

        return PimToPsmMetricsBundle(architecture=architecture_metrics)

    def count_nodes_by_type(self, nodes: Iterable[Dict[str, Any]], valid_types: Iterable[str]) -> int:
        """Cuenta los nodos cuyo tipo coincide con alguno de los proporcionados."""

        valid_type_set = {str(node_type).lower() for node_type in valid_types}
        total = 0
        for node in nodes:
            node_type = str(node.get("type", "")).lower()
            if node_type in valid_type_set:
                total += 1
        return total

    def calculate_percentage(self, numerator: Optional[int], denominator: Optional[int]) -> Optional[float]:
        """Devuelve el porcentaje entre dos valores si el denominador es positivo."""

        if numerator is None or denominator is None:
            return None
        if denominator <= 0:
            return None
        return min(100.0, (numerator / denominator) * 100.0)

    def calculate_semantic_loss(
        self,
        *,
        features_count: int,
        constraints_count: int,
        goals_count: int,
        softgoals_count: int,
        tasks_count: int,
        resources_count: int,
    ) -> Optional[float]:
        """Determina la pérdida semántica tomando como base el total de elementos del CIM."""

        denominator = goals_count + softgoals_count + tasks_count + resources_count
        if denominator <= 0:
            return None
        coverage = ((features_count + constraints_count) / denominator) * 100.0
        coverage = min(100.0, coverage)
        return max(0.0, 100.0 - coverage)

    def calculate_architecture_semantic_loss(
        self,
        features_to_classes_percent: Optional[float],
        tasks_to_methods_percent: Optional[float],
        resources_to_attributes_percent: Optional[float],
    ) -> Optional[float]:
        """Calcula la pérdida semántica promedio para la arquitectura resultante."""

        values = [
            value
            for value in (
                features_to_classes_percent,
                tasks_to_methods_percent,
                resources_to_attributes_percent,
            )
            if value is not None
        ]
        if not values:
            return None
        average_coverage = sum(values) / len(values)
        return max(0.0, 100.0 - average_coverage)

    def count_classes_in_plantuml_diagram(self, diagram: str) -> int:
        """Cuenta las definiciones de clase en el diagrama PlantUML entregado."""

        matches = self.PLANTUML_CLASS_PATTERN.findall(diagram)
        return len(matches)

    def count_attributes_in_plantuml_diagram(self, diagram: str) -> int:
        """Cuenta los atributos declarados dentro de las clases PlantUML."""

        attributes = 0
        for match in self.PLANTUML_CLASS_BLOCK_PATTERN.finditer(diagram):
            body = match.group(1)
            lines = [line.strip() for line in body.splitlines() if line.strip()]
            for line in lines:
                if re.match(r"^[-+#~]", line) and "(" not in line:
                    attributes += 1
        return attributes

    def count_methods_in_plantuml_diagram(self, diagram: str) -> int:
        """Cuenta los métodos declarados dentro de las clases PlantUML."""

        methods = 0
        for match in self.PLANTUML_CLASS_BLOCK_PATTERN.finditer(diagram):
            body = match.group(1)
            lines = [line.strip() for line in body.splitlines() if line.strip()]
            for line in lines:
                if re.match(r"^[-+#~].*\(", line):
                    methods += 1
        return methods

    def count_feature_nodes(self, feature_nodes: Iterable[FeatureNode]) -> int:
        """Cuenta recursivamente la cantidad de nodos de características proporcionados."""

        total = 0
        for node in feature_nodes:
            total += 1
            total += self.count_feature_nodes(node.children)
        return total

    def extract_context_value(
        self,
        context_metrics: Optional[Dict[str, Optional[int]]],
        key: str,
    ) -> Optional[int]:
        """Obtiene un valor numérico del contexto opcional enviado por el cliente."""

        if not context_metrics:
            return None
        value = context_metrics.get(key)
        if value is None:
            return None
        return int(value)
