from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TransformationResult:
    metadata: List[Dict[str, Any]]
    features: Dict[str, List[Dict[str, Any]]]
    restrictions: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "features": self.features,
            "restrictions": self.restrictions,
            "relations": self.relations,
        }
