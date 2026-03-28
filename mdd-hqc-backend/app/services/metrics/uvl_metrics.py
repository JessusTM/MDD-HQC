import logging
from typing import Any, Dict, List
from app.models.uvl import Feature, UVL

logger = logging.getLogger(__name__)


class UvlMetricsService:
    def __init__(self, uvl_model: UVL):
        self.uvl_model = uvl_model

    def calculate(self) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}

        features: List[Feature] = self.uvl_model.features
        total_features = len(features)
        metrics["total_features"] = total_features

        features_by_category: Dict[str, int] = {}
        for feature in features:
            category_name = feature.category
            if category_name not in features_by_category:
                features_by_category[category_name] = 0
            features_by_category[category_name] += 1
        metrics["features_by_category"] = features_by_category

        constraints_count = len(self.uvl_model.constraints)
        metrics["constraints"] = constraints_count

        total_metadata = 0
        features_with_metadata = 0
        for feature in features:
            metadata_size = len(feature.metadata)
            total_metadata += metadata_size
            if metadata_size > 0:
                features_with_metadata += 1

        total_attributes = 0
        features_with_attributes = 0
        for feature in features:
            attributes_size = len(feature.attributes)
            total_attributes += attributes_size
            if attributes_size > 0:
                features_with_attributes += 1

        if total_features > 0:
            metrics["density"] = {
                "average_metadata_per_feature": total_metadata / float(total_features),
                "average_attributes_per_feature": total_attributes
                / float(total_features),
            }
        else:
            metrics["density"] = {
                "average_metadata_per_feature": 0.0,
                "average_attributes_per_feature": 0.0,
            }

        logger.debug(
            "UVL metrics calculated: total_features=%s, constraints=%s",
            total_features,
            constraints_count,
        )
        return metrics
