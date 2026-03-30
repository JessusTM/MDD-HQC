import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

BASE_PATH = Path(__file__).resolve().parent
CSV_PATH = BASE_PATH / "uvl_category_keywords.csv"
FEATURE_MODEL_HQC = (
    "@Algorithm.Classical",
    "@Algorithm.Quantum",
    "@Algorithm",
    "@Programming",
    "@Integration_model",
    "@Quantum_HW_constraint",
    "@Functionality",
)


class UvlService:
    def __init__(self):
        """Initializes the service and loads the keyword catalog used for classification."""
        self.category_keywords: Dict[str, List[str]] = self._load_category_keywords()

    # ------------ CATEGORY KEYWORD LOADING ------------
    # Helpers to load category keywords from the CSV file.

    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """Loads the keyword catalog that maps CIM labels to UVL categories."""
        categories: Dict[str, List[str]] = {}

        with CSV_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row["category"].strip()
                keyword = row["keyword"].strip().lower()
                if not category or not keyword:
                    continue
                categories.setdefault(category, []).append(keyword)
        logger.debug(
            "Loaded UVL category keywords: path=%s, categories=%s",
            CSV_PATH,
            list(categories.keys()),
        )
        return categories

    # ------------ TEXT NORMALIZATION ------------
    # Helpers to normalize labels before matching and formatting.

    def _normalize_text(self, text: str) -> str:
        """
        Normalizes a label so lookups ignore accents, symbols, and extra spaces.

        NOTE: NFKD splits base characters from diacritics so accents can be removed safely.
        """
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", ascii_text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _split_words(self, label: str) -> List[str]:
        """Splits a normalized label into words used by the naming formatters."""
        text = self._normalize_text(label)
        if not text:
            return []
        return text.split(" ")

    # ------------ CATEGORY MATCHING ------------
    # Helpers to find the best UVL category for a label.

    def _find_matching_category(self, label: str) -> Optional[str]:
        """Finds the first matching category for a label using the configured priority order."""
        lower = self._normalize_text(label).lower()

        for category in FEATURE_MODEL_HQC:
            for word in self.category_keywords.get(category, []):
                if word in lower:
                    return category
        return None

    # ====== PUBLIC API ======

    # ------------ NAME FORMATTING ------------
    # Helpers to format source labels as UVL names.

    def format_feature_name(self, label: str) -> str:
        """Formats a source label into the PascalCase convention used for UVL features."""
        words = self._split_words(label)
        if not words:
            return ""

        result = words[0].capitalize()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        return result

    def format_attribute_name(self, label: str) -> str:
        """Formats a source label into the camelCase convention used for UVL attributes."""
        words = self._split_words(label)
        if not words:
            return ""

        result = words[0].lower()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        return result

    # ------------ FEATURE CLASSIFICATION ------------
    # Helpers to assign category and subcategory to a feature label.

    def assign_category(self, label: str) -> str:
        """Returns the main UVL category that should contain the given source label."""
        category = self._find_matching_category(label)
        if category is None:
            return "@Functionality"

        if category.startswith("@Algorithm."):
            return "@Algorithm"

        return category

    def assign_subcategory(self, label: str, category: str) -> Optional[str]:
        """Returns the nested algorithm subcategory when the selected category supports it."""
        if category != "@Algorithm":
            return None

        resolved_category = self._find_matching_category(label)
        if resolved_category is None:
            return None

        if resolved_category == "@Algorithm.Classical":
            return "Classical"
        if resolved_category == "@Algorithm.Quantum":
            return "Quantum"
        return None

    def classify_feature(self, label: str) -> Tuple[str, Optional[str]]:
        """Classifies a label and returns its UVL category plus an optional subcategory."""
        category = self.assign_category(label)
        subcategory = self.assign_subcategory(label, category)
        return category, subcategory

    # ------------ UVL PARSING ------------
    # Helpers to build lightweight data structures from UVL text.

    def parse_uvl_to_dict(self, uvl_text: str) -> dict:
        """Parses the current UVL text into the lightweight dictionary consumed by interactions.

        This helper is used in the interaction flow when the backend needs a simple DTO-like
        representation of the UVL content instead of the raw text. At this stage of the flow,
        only the namespace and the top-level HQC feature groups are required, so the method
        extracts those elements and returns empty placeholders for constraints and OR groups.
        """
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

    # ------------ FUNCTIONALITY EXTRACTION ------------
    # Helpers to extract direct functionality names from the UVL model.

    def extract_functionality_names(self, uvl_text: str) -> List[str]:
        """Extracts direct functionality feature names from the mandatory Functionality block."""
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
