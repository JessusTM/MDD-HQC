import re
import html
import xml.etree.ElementTree as ET


class XmlService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._intentional_elements = {}
        self._social_dependencies = {}
        self._internal_links = {}
        self._refinements = {}
        self._build_index()

    # ============ ELEMENTS ============
    def _get_root(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        return root

    def _get_raw_diagram_elements(self, root):
        """
        Extract all diagram elements from the iStar 2.0 export (draw.io XML).
        This output is treated as the single raw source for downstream indexing.
        """
        elements = root.find("./diagram/mxGraphModel/root")
        raw_elements = []

        for element in elements.iter():
            tag = element.tag
            attrib = element.attrib
            element_id = attrib.get("id")
            raw_elements.append(
                {
                    "id": element_id,
                    "tag": tag,
                    "attrib": attrib,
                }
            )
        return raw_elements

    def _build_intentional_elements_index(self, raw_elements):
        """
        Build an index of iStar intentional elements (goals, tasks, softgoals, resources, actors, etc.)
        excluding non-semantic metadata nodes. Social-dependency mxCells are kept.
        """
        excluded_tags = {"Array", "root", "mxPoint", "mxGeometry"}
        for element in raw_elements:
            tag = element.get("tag")
            attrib = element.get("attrib")
            raw_label = attrib.get("label")
            formatted_label = self.format_label(raw_label)
            element_id = attrib.get("id")
            if element_id is None:
                continue

            element_type = attrib.get("type")
            is_social_dependency = self.verify_social_dependency(tag, attrib)

            if tag in excluded_tags:
                continue
            if tag in {"mxCell"} and not is_social_dependency:
                continue

            self._intentional_elements[element_type] = {
                "id": element_id,
                "type": element_type,
                "tag": tag,
                "label": raw_label,
            }

    # ------------ SOCIAL DEPENDENCIES ------------
    def verify_social_dependency(self, tag: str, attrib: dict) -> bool:
        """
        Identify social dependencies encoded as mxCell edges with source/target.
        """
        is_mxcell = tag == "mxCell"
        is_edge = attrib.get("edge") == "1"
        has_source = "source" in attrib
        has_target = "target" in attrib
        return is_mxcell and is_edge and has_source and has_target

    def _build_social_dependencies_index(self, raw_elements):
        """
        Build an index of social-dependency links (mxCell edges) using element id as key.
        """
        required_tag = {"mxCell"}
        for element in raw_elements:
            tag = element.get("tag")
            if tag not in required_tag:
                continue

            attrib = element.get("attrib")
            element_id = attrib.get("id")
            if element_id is None:
                continue

            source = attrib.get("source")
            target = attrib.get("target")
            if not self.verify_social_dependency(tag, attrib):
                continue

            self._social_dependencies[element_id] = {
                "id": element_id,
                "source": source,
                "target": target,
            }

    # ------------ INTERNAL LINKS ------------
    def _build_internal_links_index(self, raw_elements):
        """
        Build an index for internal links among intentional elements:
        - needed-by
        - qualification-link
        - contribution

        These are expected to appear as mxCell edges with a 'type' attribute.
        """
        required_type = {"needed-by", "qualification-link", "contribution"}

        for element in raw_elements:
            attrib = element.get("attrib")
            element_id = attrib.get("id")
            if element_id is None:
                continue

            link_type = attrib.get("type")
            raw_label = attrib.get("label")
            formatted_label = self.format_label(raw_label)
            if link_type not in required_type:
                continue

            tag = element.get("tag")
            if tag != "mxCell":
                continue

            if attrib.get("edge") != "1":
                continue

            self._internal_links[element_id] = {
                "id": element_id,
                "type": link_type,
                "source": attrib.get("source"),
                "target": attrib.get("target"),
                "label": formatted_label,
            }

    # ------------ LABEL NORMALIZATION ------------
    def format_label(self, label):
        """
        Normalize a label by unescaping HTML and stripping markup, collapsing whitespace.
        """
        if not label:
            return label
        unescaped = html.unescape(label)
        text = re.sub(r"<.*?>", " ", unescaped)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ------------ REFINEMENT LINKS ------------
    def _build_refinements_index(self, raw_elements):
        """
        Build an index for refinement edges (AND/OR) represented as mxCell edges with type='refinement'.
        """
        required_type = {"refinement"}
        for element in raw_elements:
            attrib = element.get("attrib")
            element_id = attrib.get("id")
            if element_id is None:
                continue

            link_type = attrib.get("type")
            value = attrib.get("value")
            if link_type not in required_type:
                continue

            tag = element.get("tag")
            if tag != "mxCell":
                continue

            if attrib.get("edge") != "1":
                continue

            self._refinements[element_id] = {
                "id": element_id,
                "source": attrib.get("source"),
                "target": attrib.get("target"),
                "value": value,
            }

    # ------------ INDEX BUILD ------------
    def _build_index(self):
        """
        Build all in-memory indexes from the XML file in a single pass over raw elements.
        """
        root = self._get_root()
        raw_elements = self._get_raw_diagram_elements(root)
        self._build_intentional_elements_index(raw_elements)
        self._build_social_dependencies_index(raw_elements)
        self._build_internal_links_index(raw_elements)
        self._build_refinements_index(raw_elements)

    # ------------ PUBLIC GETTERS ------------
    def get_intentional_element_by_type(self, element_type):
        """
        Return all indexed intentional elements matching the requested iStar type.
        """
        return self._intentional_elements[element_type].iter()

    def get_social_dependencies(self):
        """
        Return the social-dependency index (mxCell edges).
        """
        return self._social_dependencies

    def get_refinements(self):
        """
        Return the refinement index (mxCell edges).
        """
        return self._refinements

    def get_internal_links(self):
        """
        Return the internal-links index (needed-by, qualification-link, contribution).
        """
        return self._internal_links

    # ============ ACTOR OWNERSHIP ============
    def get_element_to_actor_mapping(self):
        root = self._get_root()

        root_node = root.find("./diagram/mxGraphModel/root")
        if root_node is None:
            return {}

        # Minimal indexes (single pass)
        parent_by_id = {}
        type_by_id = {}
        raw_label_by_id = {}

        for obj in root_node.findall("object"):
            obj_id = obj.attrib.get("id")
            if obj_id is None:
                continue

            type_by_id[obj_id] = obj.attrib.get("type")
            raw_label_by_id[obj_id] = obj.attrib.get("label")  # raw label (may be None)

            mxcell = obj.find("mxCell")
            if mxcell is not None:
                parent_by_id[obj_id] = mxcell.attrib.get("parent")

        element_to_actor = {}
        required_actor_type = "agent"

        # Resolve only for goal/task by walking up the parent chain
        for element_id, element_type in type_by_id.items():
            if element_type not in {"goal", "task"}:
                continue

            current_parent = parent_by_id.get(element_id)
            if not current_parent:
                continue

            actor_id = None
            depth = 0
            max_depth = 10

            while current_parent and depth < max_depth:
                if type_by_id.get(current_parent) == required_actor_type:
                    actor_id = current_parent
                    break
                current_parent = parent_by_id.get(current_parent)
                depth += 1

            if actor_id:
                raw_label = raw_label_by_id.get(actor_id)
                formatted_label = self.format_label(raw_label) if raw_label else ""
                if formatted_label:
                    element_to_actor[element_id] = formatted_label

        return element_to_actor
