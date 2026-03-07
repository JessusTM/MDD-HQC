"""iStar in-memory model.

This module defines an in-memory representation of an iStar 2.0 model.

Important:
- This model is intentionally I/O-free.
- Parsers/loaders (e.g. draw.io XML) live under services and populate this model.
"""

import html
import re


class IstarModel:
    """In-memory representation of an iStar model.

    Storage is kept close to the current prototype needs:
    - _intentional_elements : iStar intentional elements grouped by type, then by id.
    - _social_dependencies  : social dependency edges (mxCell edges with source/target), keyed by id.
    - _internal_links       : internal links (needed-by, qualification-link, contribution), keyed by id.
    - _refinements          : refinement edges (type='refinement'), keyed by id.
    - _element_to_actor     : mapping {element_id: actor_label} for ownership resolution.
    """

    def __init__(self) -> None:
        self._intentional_elements: dict = {}
        self._social_dependencies: dict = {}
        self._internal_links: dict = {}
        self._refinements: dict = {}
        self._element_to_actor: dict = {}

    # ============ LABEL NORMALIZATION ============
    def _format_label(self, label):
        """Normalize a label by unescaping HTML, stripping markup, and collapsing whitespace."""
        if not label:
            return label
        unescaped = html.unescape(label)
        text = re.sub(r"<.*?>", " ", unescaped)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ============ PUBLIC GETTERS ============
    def get_intentional_element_by_type(self, element_type):
        """Return all indexed intentional elements matching the requested iStar type.

        Returns:
            dict[str, dict] -> keyed by element id
        """

        return self._intentional_elements.get(element_type, {})

    def get_social_dependencies(self):
        """Return the social dependency index (mxCell edges)."""

        return self._social_dependencies

    def get_refinements(self):
        """Return the refinement index (mxCell edges)."""

        return self._refinements

    def get_internal_links(self):
        """Return the internal links index (needed-by, qualification-link, contribution)."""

        return self._internal_links

    def get_element_to_actor_mapping(self):
        """Return the element -> actor ownership mapping."""

        return self._element_to_actor

    def get_label_by_id(self, element_id: str) -> str:
        """Resolve an element label by its id.

        In the XML export, relationships (e.g., internal links, social dependencies, refinements) are encoded as edges
        that reference elements only through `source`/`target` ids. The human-readable text, however, is stored in the
        intentional element nodes themselves (goal/task/softgoal/etc.) under their `label` field.

        This helper exists to bridge that representation: given an element id coming from an edge, it searches the
        indexed intentional elements (across all iStar types) and returns the corresponding label. If the id is unknown
        or has no label, it returns an empty string.
        """

        if not element_id:
            return ""

        for elements in self._intentional_elements.values():
            element = elements.get(element_id)
            if element:
                return element.get("label") or ""

        return ""
