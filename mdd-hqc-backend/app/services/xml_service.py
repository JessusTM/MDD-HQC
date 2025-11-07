import xml.etree.ElementTree as ET
from app.services.cli_service import CliService 

class XmlService:
    def __init__(self, cli_service : CliService):
        self.cli_service = cli_service 

    def get_root(self):
        path    = self.cli_service.read_cli_args() 
        tree    = ET.parse(path)
        root    = tree.getroot()
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
    
    def verify_social_dependency(self, tag: str, attrib: dict) -> bool:
        is_mxcell     = tag == "mxCell"
        is_edge       = attrib.get("edge") == "1"
        has_source    = "source" in attrib
        has_target    = "target" in attrib
        is_dependency = is_mxcell and is_edge and has_source and has_target
        return is_dependency

    def get_elements_without_metadata(self, raw_diagram_elements):
        filtered = []
        for element in raw_diagram_elements:
            tag    = element.get("tag")
            attrib = element.get("attrib")

            is_dependency = self.verify_social_dependency(tag, attrib)

            if tag in {"Array", "root", "mxPoint"} : continue
            if tag in {"mxCell", "mxGeometry"} and not is_dependency : continue

            filtered.append({"tag": tag, "attrib": attrib})
        return filtered

    def get_elements(self):
        root        = self.get_root()
        raw         = self.get_raw_diagram_elements(root)
        elements    = self.get_elements_without_metadata(raw)
        return elements 

    def get_elements_by_type(self, elements, attrib_type : str):
        labels = []
        for element in elements:
            attrib          = element["attrib"] 
            label           = attrib.get("label")
            element_type    = attrib.get("type")
            if element_type == str(attrib_type):
                labels.append(label)
        return labels 
