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
        """Initializes the in-memory indexes used to store the parsed iStar model.

        These collections keep intentional elements and links separated by role so
        services can query the model efficiently after loading the source diagram.
        """

        self._intentional_elements: dict = {}
        self._social_dependencies: dict = {}
        self._internal_links: dict = {}
        self._refinements: dict = {}
        self._element_to_actor: dict = {}

    # ====== Private Helpers ======
    # Internal methods that normalize stored values before public queries use them.

    # ------------ Label Normalization ------------
    # Methods below clean raw diagram labels before the model stores or exposes them.
    def _format_label(self, label):
        """Normalizes one raw diagram label before it is stored in the iStar model.

        This helper removes HTML artifacts and extra whitespace so the public model
        queries can expose clean labels when other services inspect the parsed graph.
        """

        if not label:
            return label
        unescaped = html.unescape(label)
        text = re.sub(r"<.*?>", " ", unescaped)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ====== Public API ======
    # Methods below expose the parsed iStar structures to services and transformations.

    # ------------ Indexed Element Access ------------
    # Methods below return the stored portions of the iStar model needed by the pipeline.
    def get_intentional_element_by_type(self, element_type):
        """Returns the intentional elements stored under one iStar type.

        This query lets services inspect the model by semantic group instead of walking
        the whole graph each time.

        For example, it can return the entries behind a fragment such as:
            goal: ImproveSecurity
        """

        return self._intentional_elements.get(element_type, {})

    def get_social_dependencies(self):
        """Returns the social dependency edges stored in the iStar model.

        This query exposes actor-to-actor or actor-to-element dependencies so later
        services can interpret how responsibilities are delegated across the model.
        """

        return self._social_dependencies

    def get_refinements(self):
        """Returns the refinement edges stored in the iStar model.

        This query is used when services need the decomposition structure that explains
        how one intentional element is refined into more specific elements.
        """

        return self._refinements

    def get_internal_links(self):
        """Returns the internal links stored between intentional elements.

        This query provides access to links such as contribution or needed-by so other
        backend steps can reason about the internal semantics of the iStar model.
        """

        return self._internal_links

    def get_element_to_actor_mapping(self):
        """Returns the ownership mapping between elements and their actors.

        This query helps services recover the actor context of one intentional element
        when the original relationship is needed during analysis or transformation.
        """

        return self._element_to_actor

    def get_label_by_id(self, element_id: str) -> str:
        """Returns the stored label for one intentional element id.

        This lookup lets the model recover human-readable text when links only keep the
        source and target ids of the connected elements.

        For example, it can resolve `ImproveSecurity` from a stored element such as:
            goal: ImproveSecurity
        """

        if not element_id:
            return ""

        for elements in self._intentional_elements.values():
            element = elements.get(element_id)
            if element:
                return element.get("label") or ""

        return ""
