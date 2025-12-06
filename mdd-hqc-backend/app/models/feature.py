from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Feature:
    name        : str
    category    : str
    kind        : Optional[str]     = None            
    attributes  : Dict[str, str]    = field(default_factory=dict)
    comments    : List[str]         = field(default_factory=list)
