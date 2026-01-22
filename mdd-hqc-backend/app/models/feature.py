from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Feature:
    category: str
    metadata: List[str]
    name: str
    kind: Optional[str]
    attributes: Dict[str, str]
