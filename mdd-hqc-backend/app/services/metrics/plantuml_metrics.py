from typing import Any, Dict

from app.models.uml import UmlModel, UmlClass, UmlDependency

class PlantumlMetricsService:
    def __init__(self, uml_model: UmlModel):
        self.uml_model = uml_model

    def calculate(self) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}

        classes     : Dict[str, UmlClass] = self.uml_model.classes
        dependencies: list[UmlDependency] = self.uml_model.dependencies

        total_classes                   = len(classes)
        metrics["total_classes"]        = total_classes
        metrics["total_dependencies"]   = len(dependencies)

        total_attributes            = 0
        total_methods               = 0
        algorithm_classes           = 0
        quantum_driver_classes      = 0
        other_stereotyped_classes   = 0
        classes_with_comments       = 0
        total_comments              = 0
        classes_with_tagged_values  = 0
        total_tagged_values         = 0

        for uml_class in classes.values():
            attributes_size = len(uml_class.attributes)
            methods_size    = len(uml_class.methods)

            total_attributes    += attributes_size
            total_methods       += methods_size

            stereotypes_set = set(uml_class.stereotypes)
            if "Algorithm" in stereotypes_set : algorithm_classes += 1
            if "QuantumDriver" in stereotypes_set : quantum_driver_classes += 1
            if len(stereotypes_set) > 0 and not stereotypes_set.issubset(
                {"Algorithm", "QuantumDriver"}
            ):
                other_stereotyped_classes += 1

            comments_size   = len(uml_class.comments)
            total_comments += comments_size
            if comments_size > 0:
                classes_with_comments += 1

            tagged_values_size = len(uml_class.tagged_values)
            total_tagged_values += tagged_values_size
            if tagged_values_size > 0:
                classes_with_tagged_values += 1

        metrics["attributes"]   = total_attributes
        metrics["methods"]      = total_methods

        metrics["stereotypes"] = {
            "algorithm_classes"         : algorithm_classes,
            "quantum_driver_classes"    : quantum_driver_classes,
            "other_stereotyped_classes" : other_stereotyped_classes,
        }

        metrics["semantic_preservation"] = {
            "classes_with_comments"     : classes_with_comments,
            "total_comments"            : total_comments,
            "classes_with_tagged_values": classes_with_tagged_values,
            "total_tagged_values"       : total_tagged_values,
        }

        if total_classes > 0:
            metrics["density"] = {
                "average_attributes_per_class": total_attributes
                / float(total_classes),
                "average_methods_per_class": total_methods / float(total_classes),
            }
        else:
            metrics["density"] = {
                "average_attributes_per_class"  : 0.0,
                "average_methods_per_class"     : 0.0,
            }

        metrics["requires_dependencies"] = sum(
            1
            for dep in dependencies
            if (dep.stereotype or "").strip().lower() == "requires"
        )

        return metrics
