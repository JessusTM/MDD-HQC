"""Services that compute structural metrics from generated UVL models."""

import logging
from typing import Any, Dict, List
from app.models.uvl import Feature, UVL

logger = logging.getLogger(__name__)


class UvlMetricsService:
    """Calculates aggregate metrics from one in-memory UVL model.

    This service is used by the transformation endpoints to summarize the size and basic
    density of the generated PIM before the result is returned.
    """

    def __init__(self, uvl_model: UVL):
        """Initializes the metrics service with one in-memory UVL model.

        This keeps the metric calculations attached to the exact UVL state produced by
        the CIM-to-PIM flow.
        """
        self.uvl_model = uvl_model

    def calculate(self) -> Dict[str, Any]:
        """Calculates the main structural metrics of the current UVL model.

        This method summarizes feature counts, categories, constraints, and density so
        the PIM flow can return a compact overview of the generated model.
        """
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
