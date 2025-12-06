import csv
import re
from pathlib import Path
from typing import Dict, List


class UvlService:
    BASE_PATH = Path(__file__).resolve().parent
    CSV_PATH  = BASE_PATH / "uvl_category_keywords.csv"

    def __init__(self):
        self.category_keywords: Dict[str, List[str]] = self.load_category_keywords()

    def load_category_keywords(self) -> Dict[str, List[str]]:
        categories: Dict[str, List[str]] = {}

        with self.CSV_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row["category"].strip()
                keyword  = row["keyword"].strip().lower()
                if not category or not keyword:
                    continue
                categories.setdefault(category, []).append(keyword)
        return categories

    def format_feature_name(self, label: str) -> str:
        text = label.strip()
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^A-Za-z0-9_]", "", text)
        return text

    def assign_category(self, label: str) -> str:
        lower = label.lower()

        for category in [
            "@Algorithm",
            "@Programming",
            "@Integration_model",
            "@Quantum_HW_constraint",
            "@Functionality",
        ]:
            for word in self.category_keywords.get(category, []):
                if word in lower : return category
        return "@Functionality"
