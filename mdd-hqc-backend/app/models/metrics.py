"""Modelos de métricas generadas durante las transformaciones entre niveles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class IStarMetrics:
    """Agrupa las métricas principales derivadas del modelo i* limpiado."""

    transformation_time_ms: float
    goals_count: int
    softgoals_count: int
    resources_count: int
    tasks_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transformationTimeMs": self.transformation_time_ms,
            "goalsCount": self.goals_count,
            "softgoalsCount": self.softgoals_count,
            "resourcesCount": self.resources_count,
            "tasksCount": self.tasks_count,
        }


@dataclass
class UvlMetrics:
    """Incluye los indicadores del modelo UVL construido desde el CIM."""

    transformation_time_ms: float
    features_count: int
    constraints_count: int
    goals_converted_percent: Optional[float]
    semantic_loss_percent: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transformationTimeMs": self.transformation_time_ms,
            "featuresCount": self.features_count,
            "constraintsCount": self.constraints_count,
            "goalsConvertedPercent": self.goals_converted_percent,
            "semanticLossPercent": self.semantic_loss_percent,
        }


@dataclass
class ArchitectureMetrics:
    """Representa las métricas resultantes del diagrama Quantum-UML generado."""

    transformation_time_ms: float
    classes_count: int
    attributes_count: int
    methods_count: int
    features_to_classes_percent: Optional[float]
    tasks_to_methods_percent: Optional[float]
    resources_to_attributes_percent: Optional[float]
    semantic_loss_percent: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transformationTimeMs": self.transformation_time_ms,
            "classesCount": self.classes_count,
            "attributesCount": self.attributes_count,
            "methodsCount": self.methods_count,
            "featuresToClassesPercent": self.features_to_classes_percent,
            "tasksToMethodsPercent": self.tasks_to_methods_percent,
            "resourcesToAttributesPercent": self.resources_to_attributes_percent,
            "semanticLossPercent": self.semantic_loss_percent,
        }


@dataclass
class CimToPimMetricsBundle:
    """Agrupa las métricas generadas durante la transformación CIM → PIM."""

    istar: IStarMetrics
    uvl: UvlMetrics

    def to_dict(self) -> Dict[str, Any]:
        return {
            "istar": self.istar.to_dict(),
            "uvl": self.uvl.to_dict(),
        }


@dataclass
class PimToPsmMetricsBundle:
    """Agrupa las métricas producidas durante la transformación PIM → PSM."""

    architecture: ArchitectureMetrics

    def to_dict(self) -> Dict[str, Any]:
        return {"architecture": self.architecture.to_dict()}
