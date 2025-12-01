# app/services/xml_service.py
import re
import html
import xml.etree.ElementTree as ET

class XmlService:
    def __init__(self, file_path: str):
        self.file_path = file_path

    # ============ ELEMENTS ============
    def get_root(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        return root

    def get_raw_diagram_elements(self, root):
        elements                = root.find("./diagram/mxGraphModel/root")
        raw_diagram_elements    = []

        for child in elements.iter():
            tag     = child.tag
            attrib  = child.attrib
            raw_diagram_elements.append({
                "tag"   : tag,
                "attrib": attrib,
            })
        return raw_diagram_elements

    def get_elements_without_metadata(self, raw_diagram_elements):
        excluded_tags   = {"Array", "root", "mxPoint", "mxGeometry"}
        filtered        = []
        for element in raw_diagram_elements:
            tag             = element.get("tag")
            attrib          = element.get("attrib")
            is_dependency   = self.verify_social_dependency(tag, attrib)

            if tag in excluded_tags : continue
            if tag in {"mxCell"} and not is_dependency : continue

            filtered.append({"tag": tag, "attrib": attrib})
        return filtered

    def get_elements(self):
        root        = self.get_root()
        raw         = self.get_raw_diagram_elements(root)
        elements    = self.get_elements_without_metadata(raw)
        return elements

    # ============ SOCIAL DEPENDENCIES ============
    def verify_social_dependency(self, tag: str, attrib: dict) -> bool:
        is_mxcell     = tag == "mxCell"
        is_edge       = attrib.get("edge") == "1"
        has_source    = "source" in attrib
        has_target    = "target" in attrib
        is_dependency = is_mxcell and is_edge and has_source and has_target
        return is_dependency

    def get_social_dependencies(self, filtered_elements):
        social_dependencies = []
        for element in filtered_elements:
            tag     = element.get("tag")
            attrib  = element.get("attrib")
            source  = attrib.get("source")
            target  = attrib.get("target")
            is_dependency   = self.verify_social_dependency(tag, attrib)
            if not is_dependency : continue
            social_dependencies.append({"source": source, "target": target})
        return social_dependencies

    # ============ LABELS / GOALS ============
    def format_label(self, label):
        if not label : return label
        unescaped   = html.unescape(label)
        text        = re.sub(r"<.*?>", " ", unescaped)
        text        = re.sub(r"\s+", " ", text).strip()
        return text

    def get_goals(self, filtered_elements):
        goals = []
        for element in filtered_elements:
            attrib          = element.get("attrib")
            label           = attrib.get("label")
            formatted_label = self.format_label(label)
            id              = attrib.get("id")
            goals.append(
                {
                    "label" : formatted_label, 
                    "id"    : id
                }
            )
        return goals

    def get_elements_by_type(self, elements, attrib_type: str):
        labels = []
        for element in elements:
            attrib          = element["attrib"]
            label           = attrib.get("label")
            formatted_label = self.format_label(label)
            element_type    = attrib.get("type")
            if element_type == str(attrib_type):
                labels.append(formatted_label)
        return labels

    def map_id_to_label(self, filtered_elements):
        labels = {}
        for element in filtered_elements:
            attrib          = element.get("attrib")
            id              = attrib.get("id")
            if not id : continue
            label           = attrib.get("label")
            formatted_label = self.format_label(label)
            labels[id]     = formatted_label
        return labels

    # ============ ENLACES ENTRE ELEMENTOS INTERNOS ============ 
    def get_internal_links(self):
        root      = self.get_root()
        root_node = root.find("./diagram/mxGraphModel/root")
        links     = []
        if root_node is None : return links

        for obj in root_node.findall("object"):
            link_type = obj.attrib.get("type")
            if link_type not in {"needed-by", "qualification-link", "contribution"} : continue

            mxcell = obj.find("mxCell")
            if mxcell is None : continue

            mx_attrib = mxcell.attrib
            if mx_attrib.get("edge") != "1" : continue

            links.append(
                {
                    "type"      : link_type,
                    "source"    : mx_attrib.get("source"),
                    "target"    : mx_attrib.get("target"),
                    "value"     : obj.attrib.get("value") or obj.attrib.get("label") or "",
                }
            )
        return links
