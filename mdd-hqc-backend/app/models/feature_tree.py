"""Modelos de datos que describen jerarquías de características extraídas de UVL."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FeatureNode:
    """Representa una característica UVL dentro de la estructura jerárquica."""

    name: str
    section: Optional[str] = None
    children: List["FeatureNode"] = field(default_factory=list)


Constraint = Dict[str, str]
