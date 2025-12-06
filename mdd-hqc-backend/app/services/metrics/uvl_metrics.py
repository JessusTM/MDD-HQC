from typing import Any, Dict, List

from app.models.uvl import UVL
from app.models.feature import Feature


class UvlMetricsService:
    def __init__(self, uvl_model: UVL):
        self.uvl_model = uvl_model

    def calculate(self) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}

        features: List[Feature]     = self.uvl_model.features
        total_features              = len(features)
        metrics["total_features"]   = total_features

        features_by_category: Dict[str, int] = {}
        for feature in features:
            category_name = feature.category
            if category_name not in features_by_category:
                features_by_category[category_name] = 0
            features_by_category[category_name] += 1
        metrics["features_by_category"] = features_by_category

        goals_count         = 0
        tasks_count         = 0
        other_kind_count    = 0

        for feature in features:
            kind_value = feature.kind or ""
            if kind_value == "goal":
                goals_count += 1
            elif kind_value == "task":
                tasks_count += 1
            elif kind_value != "":
                other_kind_count += 1

        metrics["features_by_kind"] = {
            "goal"  : goals_count,
            "task"  : tasks_count,
            "other" : other_kind_count,
        }

        constraints_count       = len(self.uvl_model.constraints)
        metrics["constraints"]  = constraints_count

        total_comments          = 0
        features_with_comments  = 0
        for feature in features:
            comments_size = len(feature.comments)
            total_comments += comments_size
            if comments_size > 0:
                features_with_comments += 1

        total_attributes            = 0
        features_with_attributes    = 0
        for feature in features:
            attributes_size = len(feature.attributes)
            total_attributes += attributes_size
            if attributes_size > 0:
                features_with_attributes += 1

        metrics["semantic_preservation"] = {
            "features_with_comments"    : features_with_comments,
            "total_comments"            : total_comments,
            "features_with_attributes"  : features_with_attributes,
            "total_attributes"          : total_attributes,
        }

        if total_features > 0:
            metrics["density"] = {
                "average_comments_per_feature"  : total_comments / float(total_features),
                "average_attributes_per_feature": total_attributes
                / float(total_features),
            }
        else:
            metrics["density"] = {
                "average_comments_per_feature"  : 0.0,
                "average_attributes_per_feature": 0.0,
            }

        return metrics
