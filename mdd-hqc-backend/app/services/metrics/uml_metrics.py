"""Services that compute structural metrics from generated UML models."""

import logging
from typing import Any, Dict
from app.models.uml import UmlModel, UmlClass, UmlDependency

logger = logging.getLogger(__name__)


class UmlMetricsService:
    """Calculates aggregate metrics from one generated UML model.

    This service is used by transformation flows to summarize the size and structure of
    the UML output before it is returned or rendered as PlantUML.
    """

    def __init__(self, uml_model: UmlModel):
        """Initializes the metrics service with one in-memory UML model.

        This keeps the metric calculations aligned with the exact UML model produced by
        the transformation pipeline.
        """
        self.uml_model = uml_model

    def calculate(self) -> Dict[str, Any]:
        """Calculates the main structural metrics of the current UML model.

        This method summarizes classes, members, stereotypes, and dependencies so the
        PSM flow can report a compact overview of the generated diagram.
        """
        metrics: Dict[str, Any] = {}

        classes: Dict[str, UmlClass] = self.uml_model.classes
        dependencies: list[UmlDependency] = self.uml_model.dependencies

        total_classes = len(classes)
        metrics["total_classes"] = total_classes
        metrics["total_dependencies"] = len(dependencies)

        total_attributes = 0
        total_methods = 0
        algorithm_classes = 0
        quantum_driver_classes = 0
        other_stereotyped_classes = 0
        for uml_class in classes.values():
            attributes_size = len(uml_class.attributes)
            methods_size = len(uml_class.methods)

            total_attributes += attributes_size
            total_methods += methods_size

            stereotypes_set = set(uml_class.stereotypes)
            if "Algorithm" in stereotypes_set:
                algorithm_classes += 1
            if "QuantumDriver" in stereotypes_set:
                quantum_driver_classes += 1
            if len(stereotypes_set) > 0 and not stereotypes_set.issubset(
                {"Algorithm", "QuantumDriver"}
            ):
                other_stereotyped_classes += 1

        metrics["attributes"] = total_attributes
        metrics["methods"] = total_methods

        metrics["stereotypes"] = {
            "algorithm_classes": algorithm_classes,
            "quantum_driver_classes": quantum_driver_classes,
            "other_stereotyped_classes": other_stereotyped_classes,
        }

        if total_classes > 0:
            metrics["density"] = {
                "average_attributes_per_class": total_attributes / float(total_classes),
                "average_methods_per_class": total_methods / float(total_classes),
            }
        else:
            metrics["density"] = {
                "average_attributes_per_class": 0.0,
                "average_methods_per_class": 0.0,
            }

        metrics["requires_dependencies"] = sum(
            1
            for dep in dependencies
            if (dep.stereotype or "").strip().lower() == "requires"
        )

        logger.debug(
            "PlantUML metrics calculated: total_classes=%s, total_dependencies=%s",
            total_classes,
            len(dependencies),
        )
        return metrics
