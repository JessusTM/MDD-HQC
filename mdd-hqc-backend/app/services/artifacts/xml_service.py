"""Services that parse draw.io iStar XML files into in-memory model indexes."""

import logging
import xml.etree.ElementTree as ET

from app.models.istar import IstarModel

logger = logging.getLogger(__name__)


class XmlService(IstarModel):
    """Parses a draw.io iStar XML export and fills the in-memory iStar indexes.

    This service extends the base iStar model with the loading logic required to turn
    the XML artifact into the indexed structures used by metrics and transformations.
    """

    def __init__(self, file_path: str):
        """Initializes the parser and builds the iStar indexes from one XML file.

        This method is used at the start of CIM-related flows so the rest of the backend
        can work with the parsed iStar model instead of raw XML.
        """
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

    # ====== Private Helpers ======
    # Internal methods below parse the XML file and populate the inherited iStar indexes.

    # ------------ Root and Raw Extraction ------------
    # Methods below read the XML document and extract the raw diagram elements to index.
    def _get_root(self):
        """Parses the XML file located at `self.file_path` and returns its root element.

        This helper starts the loading process by giving the rest of the parser access to
        the root tree structure of the source draw.io file.
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
        """Extracts the raw diagram elements that can later be indexed.

        This helper merges semantic object data with graph-level mxCell data so the
        downstream indexers can classify each element with full context.
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

    # ------------ Validations ------------
    # Methods below validate whether raw XML nodes match the supported iStar link types.
    def _verify_social_dependency(self, tag: str, attrib: dict) -> bool:
        """Returns `True` when the given node represents a social dependency link.

        This helper keeps the link checks centralized before the parser stores a raw edge
        as a social dependency in the in-memory model.
        """
        is_mxcell = tag == "mxCell"
        is_edge = attrib.get("edge") == "1"
        has_source = "source" in attrib
        has_target = "target" in attrib
        link_type = attrib.get("type")
        return (
            is_mxcell
            and is_edge
            and has_source
            and has_target
            and link_type == "dependency-link"
        )

    # ------------ Index Builders ------------
    # Methods below classify raw XML nodes and store them in the inherited iStar indexes.
    def _index_intentional_element(self, tag, attrib):
        """Indexes one iStar intentional element when the raw node is valid.

        This helper populates the main intentional-element index so later backend steps
        can query goals, tasks, resources, and related nodes by type and id.
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
        """Indexes one social dependency edge by its id.

        This helper stores the dependency links that metrics and transformations later
        inspect when deriving cross-element relations from the iStar model.
        """
        id = attrib.get("id")
        source = attrib.get("source")
        target = attrib.get("target")
        label = attrib.get("label")

        if id is None:
            return
        if not self._verify_social_dependency(tag, attrib):
            return

        self._social_dependencies[id] = {
            "id": id,
            "source": source,
            "target": target,
            "label": self._format_label(label),
        }

    def _index_internal_link(self, tag, attrib):
        """Indexes one supported internal link between intentional elements.

        This helper stores needed-by, qualification, and contribution links so later
        backend steps can process those semantics without re-reading the XML.
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
        """Indexes one refinement edge by its id.

        This helper stores decomposition relations so transformations can later rebuild
        the refinement structure of the source iStar model.
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

    # ------------ Actor Ownership Resolution ------------
    # Methods below derive which actor owns each relevant iStar element.
    def _index_element_to_actor(self, root) -> dict:
        """Builds the mapping `{element_id: actor_label}` from the parsed XML root.

        This helper derives ownership information so later transformations can attach
        actor traceability metadata to the generated UVL model.
        """
        objects = root.findall("./diagram/mxGraphModel/root/object")
        if not objects:
            return {}

        parent_by_id = {}
        type_by_id = {}
        label_by_id = {}
        actor_by_boundary = {}

        self._collect_object_indexes(
            objects=objects,
            parent_by_id=parent_by_id,
            type_by_id=type_by_id,
            label_by_id=label_by_id,
            actor_by_boundary=actor_by_boundary,
        )

        element_to_actor = {}

        self._assign_element_to_actor(
            objects=objects,
            parent_by_id=parent_by_id,
            actor_by_boundary=actor_by_boundary,
            element_to_actor=element_to_actor,
        )

        return element_to_actor

    def _collect_object_indexes(
        self, objects, parent_by_id, type_by_id, label_by_id, actor_by_boundary
    ) -> None:
        """Fills the lookup dictionaries needed for actor-ownership resolution.

        This helper prepares the indexes that let the ownership step walk boundaries and
        resolve which actor controls each relevant element.
        """
        owns_links = []

        for object in objects:
            id = object.attrib.get("id")
            if id is None:
                continue

            type_by_id[id] = object.attrib.get("type")
            label_by_id[id] = object.attrib.get("label")

            mxcell = object.find("mxCell")
            if mxcell is not None:
                parent_by_id[id] = mxcell.attrib.get("parent")

            if object.attrib.get("type") == "owns":
                owns_links.append(object)

        for object in owns_links:
            mxcell = object.find("mxCell")
            if mxcell is None:
                continue

            source_id = mxcell.attrib.get("source")
            target_id = mxcell.attrib.get("target")
            if not source_id or not target_id:
                continue
            if type_by_id.get(source_id) != "agent":
                continue

            raw_actor_label = label_by_id.get(source_id)
            if not raw_actor_label:
                continue

            actor_label = self._format_label(raw_actor_label)
            actor_by_boundary[target_id] = actor_label

            target_parent = parent_by_id.get(target_id)
            if target_parent:
                actor_by_boundary[target_parent] = actor_label

    def _assign_element_to_actor(
        self,
        objects,
        parent_by_id,
        actor_by_boundary,
        element_to_actor,
    ) -> None:
        """Populates `element_to_actor` in place for goals, tasks, and resources.

        This helper walks the containment chain until it reaches an owned boundary so the
        parser can preserve actor ownership in the in-memory model.
        """
        for object in objects:
            id = object.attrib.get("id")
            if id is None:
                continue

            if object.attrib.get("type") not in {"goal", "task", "resource"}:
                continue

            current_parent = parent_by_id.get(id)
            while current_parent:
                actor_label = actor_by_boundary.get(current_parent)
                if actor_label:
                    element_to_actor[id] = actor_label
                    break
                current_parent = parent_by_id.get(current_parent)

    # ------------ Index Build ------------
    # Methods below orchestrate the full XML-to-index parsing process.
    def _build_indexes(self):
        """Builds all in-memory indexes from the XML file.

        This helper is the main internal parsing step that fills every inherited iStar
        index before public consumers start querying the model.
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
