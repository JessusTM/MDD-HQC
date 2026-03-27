import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class UvlService:
    BASE_PATH = Path(__file__).resolve().parent
    CSV_PATH = BASE_PATH / "uvl_category_keywords.csv"
    CATEGORY_ORDER = [
        "@Algorithm.Classical",
        "@Algorithm.Quantum",
        "@Algorithm",
        "@Programming",
        "@Integration_model",
        "@Quantum_HW_constraint",
        "@Functionality",
    ]

    def __init__(self):
        self.category_keywords: Dict[str, List[str]] = self.load_category_keywords()

    def load_category_keywords(self) -> Dict[str, List[str]]:
        """Loads the keyword dictionary used to classify CIM labels into UVL branches."""
        categories: Dict[str, List[str]] = {}

        with self.CSV_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row["category"].strip()
                keyword = row["keyword"].strip().lower()
                if not category or not keyword:
                    continue
                categories.setdefault(category, []).append(keyword)
        logger.debug(
            "Loaded UVL category keywords: path=%s, categories=%s",
            self.CSV_PATH,
            list(categories.keys()),
        )
        return categories

    def _normalize_text(self, text: str) -> str:
        """Normalizes labels so dictionary lookups ignore accents and punctuation noise."""
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", ascii_text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _split_words(self, label: str) -> List[str]:
        text = self._normalize_text(label)
        if not text:
            return []
        return text.split(" ")

    def format_feature_name(self, label: str) -> str:
        """Formats one source label into the UVL feature naming convention."""
        words = self._split_words(label)
        if not words:
            return ""
        result = words[0].capitalize()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        return result

    def format_attribute_name(self, label: str) -> str:
        """Formats one source label into the UVL attribute naming convention."""
        words = self._split_words(label)
        if not words:
            return ""

        result = words[0].lower()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        return result

    def _resolve_category_match(self, label: str) -> Optional[str]:
        """Finds the most specific category key that matches the normalized label."""
        lower = self._normalize_text(label).lower()

        for category in self.CATEGORY_ORDER:
            for word in self.category_keywords.get(category, []):
                if word in lower:
                    return category
        return None

    def assign_category(self, label: str) -> str:
        """Returns the main UVL category for one label using the project dictionary."""
        category = self._resolve_category_match(label)
        if category is None:
            return "@Functionality"

        if category.startswith("@Algorithm."):
            return "@Algorithm"

        return category

    def assign_subgroup(self, label: str, category: str) -> Optional[str]:
        """Returns the UVL subgroup when the selected category supports nested branches."""
        if category != "@Algorithm":
            return None

        resolved_category = self._resolve_category_match(label)
        if resolved_category is None:
            return None

        subgroup_by_category = {
            "@Algorithm.Classical": "Classical",
            "@Algorithm.Quantum": "Quantum",
        }
        return subgroup_by_category.get(resolved_category)

    def classify_feature(self, label: str) -> Tuple[str, Optional[str]]:
        """Classifies one label into UVL category and optional subgroup in one step."""
        category = self.assign_category(label)
        subgroup = self.assign_subgroup(label, category)
        return category, subgroup

    def parse_uvl_to_dict(self, uvl_text: str) -> dict:
        """Builds a lightweight interaction DTO from the current UVL text format."""
        namespace = "default"
        features = []

        for raw_line in uvl_text.splitlines():
            line = raw_line.strip()
            if line.startswith("namespace "):
                parts = line.split()
                if len(parts) >= 2:
                    namespace = parts[1]
                continue

            if line in {
                "Functionality",
                "Algorithm",
                "Programming",
                "Integration_model",
                "Quantum_HW_constraint",
            }:
                features.append({"name": line, "category": "HQCSPL"})

        return {
            "namespace": namespace,
            "features": features,
            "constraints": [],
            "or_groups": {},
        }

    def extract_functionality_names(self, uvl_text: str) -> List[str]:
        """Extracts direct functionality feature names from the current UVL structure."""
        lines = uvl_text.splitlines()
        names: List[str] = []
        in_functionality = False
        in_mandatory_group = False
        functionality_indent = 0
        mandatory_indent = 0

        for raw_line in lines:
            stripped = raw_line.strip()
            indent = len(raw_line) - len(raw_line.lstrip(" "))

            if not stripped:
                continue

            if stripped == "Functionality":
                in_functionality = True
                in_mandatory_group = False
                functionality_indent = indent
                continue

            if in_functionality and indent <= functionality_indent:
                in_functionality = False
                in_mandatory_group = False

            if not in_functionality:
                continue

            if stripped == "mandatory":
                in_mandatory_group = True
                mandatory_indent = indent
                continue

            if in_mandatory_group and indent <= mandatory_indent:
                in_mandatory_group = False

            if not in_mandatory_group:
                continue

            if stripped in {"mandatory", "or"}:
                continue

            if stripped.startswith("#"):
                continue

            if stripped in {
                "Functionality",
                "Algorithm",
                "Programming",
                "Integration_model",
                "Quantum_HW_constraint",
                "Classical",
                "Quantum",
            }:
                continue

            feature_name = stripped
            if feature_name == "{" or feature_name == "}":
                continue
            if feature_name.endswith("{"):
                feature_name = feature_name[:-1].strip()
            if feature_name.endswith("}"):
                feature_name = feature_name[:-1].strip()
            if not feature_name:
                continue
            if ' "' in feature_name:
                continue

            if feature_name not in names:
                names.append(feature_name)

        return names
