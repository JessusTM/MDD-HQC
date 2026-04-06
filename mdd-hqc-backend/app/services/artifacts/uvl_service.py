"""Services that classify labels and extract lightweight views of UVL content."""

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
    """Provides naming, classification, and parsing helpers for UVL-related workflows.

    This service supports the CIM-to-PIM pipeline and the interaction endpoints by
    turning free-form labels and UVL text into backend-friendly structures.
    """

    def __init__(self):
        """Initializes the service and loads the keyword catalog used for classification.

        This setup prepares the lookup tables required by naming and category detection
        before other backend steps start processing source labels.
        """
        self.category_keywords: Dict[str, List[str]] = self._load_category_keywords()

    # ------------ CATEGORY KEYWORD LOADING ------------
    # Helpers to load category keywords from the CSV file.

    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """Loads the keyword catalog that maps CIM labels to UVL categories.

        This helper prepares the classification data that the service reuses whenever a
        label must be assigned to one of the supported UVL categories.
        """
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
        """Normalizes a label so lookups ignore accents, symbols, and extra spaces.

        This helper keeps classification and formatting stable even when source labels
        contain punctuation or accented characters.
        """
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", ascii_text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _split_words(self, label: str) -> List[str]:
        """Splits a normalized label into words used by the naming formatters.

        This helper gives the public naming methods a clean token list before they build
        feature or attribute names for the UVL model.
        """
        text = self._normalize_text(label)
        if not text:
            return []
        return text.split(" ")

    # ------------ CATEGORY MATCHING ------------
    # Helpers to find the best UVL category for a label.

    def _find_matching_category(self, label: str) -> Optional[str]:
        """Finds the first matching category for a label using the configured priority order.

        This helper keeps category detection consistent so higher-level methods can rely
        on one shared matching strategy across the backend flow.
        """
        lower = self._normalize_text(label).lower()

        for category in FEATURE_MODEL_HQC:
            for word in self.category_keywords.get(category, []):
                if word in lower:
                    return category
        return None

    # ====== Public API ======
    # Methods below expose the naming, classification, and parsing helpers used by other layers.

    # ------------ NAME FORMATTING ------------
    # Helpers to format source labels as UVL names.

    def format_feature_name(self, label: str) -> str:
        """Formats a source label into the PascalCase convention used for UVL features.

        This method is used when services need a consistent feature name before storing
        or exporting the UVL model.
        """
        words = self._split_words(label)
        if not words:
            return ""

        result = words[0].capitalize()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        return result

    def format_attribute_name(self, label: str) -> str:
        """Formats a source label into the camelCase convention used for UVL attributes.

        This method is used when feature properties must be stored with the attribute
        naming style expected by the generated UVL model.
        """
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
        """Returns the main UVL category that should contain the given source label.

        This method is used by transformation services when they need a stable top-level
        category before a feature is added to the UVL model.
        """
        category = self._find_matching_category(label)
        if category is None:
            return "@Functionality"

        if category.startswith("@Algorithm."):
            return "@Algorithm"

        return category

    def assign_subcategory(self, label: str, category: str) -> Optional[str]:
        """Returns the nested algorithm subcategory when the selected category supports it.

        This method refines algorithm placement so the UVL model can distinguish between
        classical and quantum branches when needed.
        """
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
        """Classifies a label and returns its UVL category plus an optional subcategory.

        This method gives transformation services one direct entry point for deciding how
        a new feature should be placed inside the UVL structure.
        """
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
        """Extracts direct functionality feature names from the mandatory Functionality block.

        This method is used by interaction endpoints when they need a simple list of the
        main functionality names already declared in the UVL model.
        """
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
