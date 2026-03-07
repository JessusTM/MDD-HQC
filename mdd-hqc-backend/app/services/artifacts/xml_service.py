import logging
import xml.etree.ElementTree as ET

from app.models.istar import IstarModel

logger = logging.getLogger(__name__)


class XmlService(IstarModel):
    """
    XmlService parses a draw.io XML export of an iStar 2.0 model and builds in-memory indexes.

    Indexes built:
    - _intentional_elements : iStar intentional elements grouped by type, then by id.
    - _social_dependencies  : social dependency edges (mxCell edges with source/target), keyed by id.
    - _internal_links       : internal links (needed-by, qualification-link, contribution), keyed by id.
    - _refinements          : refinement edges (type='refinement'), keyed by id.
    - _element_to_actor     : mapping {element_id: actor_label} for ownership resolution.
    """

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

        logger.debug("Parsing iStar XML: path=%s", file_path)
        self._build_indexes()
        logger.info(
            "XML indexes built: path=%s, intentional_types=%s, social_deps=%s, internal_links=%s, refinements=%s",
            file_path,
            len(self._intentional_elements),
            len(self._social_dependencies),
            len(self._internal_links),
            len(self._refinements),
        )

    # ============ ROOT / RAW EXTRACTION ============
    def _get_root(self):
        """
        Parse the XML file located at self.file_path and return its root element.
        """
        try:
            tree = ET.parse(self.file_path)
            return tree.getroot()
        except ET.ParseError as exc:
            logger.error(
                "XML parse error: path=%s, error=%s", self.file_path, exc, exc_info=True
            )
            raise
        except OSError as exc:
            logger.error(
                "Failed to read XML file: path=%s, error=%s",
                self.file_path,
                exc,
                exc_info=True,
            )
            raise

    def _get_raw_diagram_elements(self, root):
        """
        Extract indexable diagram elements from draw.io XML.

        We merge <object> attributes (semantic: type/label/value/id)
        with its inner <mxCell> attributes (graph: edge/source/target/parent),
        because downstream indexers require both views at once.
        """
        objects = root.findall("./diagram/mxGraphModel/root/object")
        raw_elements = []

        for obj in objects:
            obj_attrib = obj.attrib or {}

            mxcell = obj.find("mxCell")
            mx_attrib = mxcell.attrib if mxcell is not None else {}

            merged = dict(mx_attrib)
            merged.update(obj_attrib)

            is_edge = mx_attrib.get("edge") == "1"
            tag = "mxCell" if is_edge else obj.tag
            raw_elements.append({"tag": tag, "attrib": merged})

        return raw_elements

    # ============ VALIDATIONS ============
    def _verify_social_dependency(self, tag: str, attrib: dict) -> bool:
        """
        Return True if the given node represents a social dependency edge:
        an mxCell edge with both source and target attributes.
        """
        is_mxcell = tag == "mxCell"
        is_edge = attrib.get("edge") == "1"
        has_source = "source" in attrib
        has_target = "target" in attrib
        return is_mxcell and is_edge and has_source and has_target

    # ============ INDEXERS (SELF-VALIDATING) ============
    def _index_intentional_element(self, tag, attrib):
        """
        Index an iStar intentional element (goals, tasks, softgoals, resources, actors, etc.).
        Metadata nodes are excluded. mxCell nodes are only included if they encode a social dependency.
        """
        excluded_tags = {"Array", "root", "mxPoint", "mxGeometry"}

        id = attrib.get("id")
        element_type = attrib.get("type")
        raw_label = attrib.get("label")
        formatted_label = self._format_label(raw_label)

        if id is None:
            return
        if tag in excluded_tags:
            return
        is_social_dependency = self._verify_social_dependency(tag, attrib)
        if tag == "mxCell" and not is_social_dependency:
            return
        if element_type is None:
            return

        # NOTE: Stores by type -> id without overwriting same-type elements
        self._intentional_elements.setdefault(element_type, {})[id] = {
            "id": id,
            "type": element_type,
            "tag": tag,
            "label": formatted_label,
        }

    def _index_social_dependency(self, tag, attrib):
        """
        Index a social dependency edge (mxCell) by its id.
        """
        id = attrib.get("id")
        source = attrib.get("source")
        target = attrib.get("target")

        if id is None:
            return
        if not self._verify_social_dependency(tag, attrib):
            return

        self._social_dependencies[id] = {
            "id": id,
            "source": source,
            "target": target,
        }

    def _index_internal_link(self, tag, attrib):
        """
        Index internal links among intentional elements:
        - needed-by
        - qualification-link
        - contribution
        """
        internal_link_types = {"needed-by", "qualification-link", "contribution"}

        id = attrib.get("id")
        source = attrib.get("source")
        target = attrib.get("target")
        link_type = attrib.get("type")
        raw_label = attrib.get("label")
        formatted_label = self._format_label(raw_label)

        if id is None:
            return
        if tag != "mxCell":
            return
        if attrib.get("edge") != "1":
            return
        if link_type not in internal_link_types:
            return

        self._internal_links[id] = {
            "id": id,
            "type": link_type,
            "source": source,
            "target": target,
            "label": formatted_label,
        }

    def _index_refinement(self, tag, attrib):
        """
        Index refinement edges (type='refinement') by their id.
        """
        id = attrib.get("id")
        source = attrib.get("source")
        target = attrib.get("target")
        value = attrib.get("value")
        edge = attrib.get("edge")
        link_type = attrib.get("type")

        if id is None:
            return
        if tag != "mxCell":
            return
        if edge != "1":
            return
        if link_type != "refinement":
            return

        self._refinements[id] = {
            "id": id,
            "source": source,
            "target": target,
            "value": value,
        }

    # ============ ACTOR OWNERSHIP (ORCHESTRATOR + HELPERS) ============
    def _index_element_to_actor(self, root) -> dict:
        """
        Build a mapping {element_id: actor_label} using the already-parsed XML root.

        Steps:
        1) Read all <object> nodes and collect quick indexes: type, label, and mxCell parent.
        2) For each target element (goal/task), walk its parent chain until an agent is found.
        """
        objects = root.findall("./diagram/mxGraphModel/root/object")
        if not objects:
            return {}

        parent_by_id = {}
        type_by_id = {}
        label_by_id = {}

        self._collect_object_indexes(
            objects=objects,
            parent_by_id=parent_by_id,
            type_by_id=type_by_id,
            label_by_id=label_by_id,
        )

        element_to_actor = {}

        self._assign_element_to_actor(
            objects=objects,
            parent_by_id=parent_by_id,
            type_by_id=type_by_id,
            label_by_id=label_by_id,
            element_to_actor=element_to_actor,
        )

        return element_to_actor

    def _collect_object_indexes(
        self, objects, parent_by_id, type_by_id, label_by_id
    ) -> None:
        """
        Fill lookup dicts keyed by object id:

        - type_by_id[id]  : element kind (goal, task, agent, ...)
        - label_by_id[id] : raw label (later formatted when needed)
        - parent_by_id[id]: mxCell parent id (used to walk "who contains who")
        """
        for object in objects:
            id = object.attrib.get("id")
            if id is None:
                continue

            type_by_id[id] = object.attrib.get("type")
            label_by_id[id] = object.attrib.get("label")

            mxcell = object.find("mxCell")
            if mxcell is not None:
                parent_by_id[id] = mxcell.attrib.get("parent")

    def _assign_element_to_actor(
        self,
        objects,
        parent_by_id,
        type_by_id,
        label_by_id,
        element_to_actor,
    ) -> None:
        """
        Populate element_to_actor in-place.

        For each goal/task:
        - Start from its parent
        - Move up parent -> parent -> parent
        - Stop when an 'agent' is reached, and assign that agent's label as the owner
        """
        for object in objects:
            id = object.attrib.get("id")
            if id is None:
                continue

            if object.attrib.get("type") not in {"goal", "task"}:
                continue

            current_parent = parent_by_id.get(id)
            while current_parent:
                if type_by_id.get(current_parent) == "agent":
                    raw_label = label_by_id.get(current_parent)
                    element_to_actor[id] = (
                        self._format_label(raw_label) if raw_label else ""
                    )
                    break
                current_parent = parent_by_id.get(current_parent)

    # ============ INDEX BUILD ============
    def _build_indexes(self):
        """
        Build all in-memory indexes from the XML file.
        """
        root = self._get_root()
        raw_elements = self._get_raw_diagram_elements(root)

        for element in raw_elements:
            tag = element.get("tag")
            attrib = element.get("attrib", {})
            if not attrib:
                continue

            self._index_intentional_element(tag, attrib)
            self._index_social_dependency(tag, attrib)
            self._index_internal_link(tag, attrib)
            self._index_refinement(tag, attrib)
        self._element_to_actor = self._index_element_to_actor(root)
