import xml.etree.ElementTree as ET
from pathlib import Path
from cli_args_service import CliArgs

class XmlService:
    def get_root(self, path : Path):
        tree    = ET.parse(path)
        root    = tree.getroot()
        return root

    def get_raw_diagram_elements(self, root):
        elements                = root.find("./diagram/mxGraphModel/root")
        raw_diagram_elements    = []

        for child in elements:
            tag     = child.tag
            attrib  = child.attrib
            raw_diagram_elements.append({
                "tag"   : tag, 
                "attrib": attrib,
            })
        return raw_diagram_elements
      
    def delete_metadata_elements(self, raw_diagram_elements):
        filtered = []
        for element in raw_diagram_elements:
            tag     = element.get("tag")
            attrib  = element.get("attrib")
            if tag not in {"mxCell", "mxGeometry"}:
                filtered.append({
                    "tag"   : tag,
                    "attrib": attrib,
                })
        print(filtered)
        return filtered

cli_args_service        = CliArgs() 
xml_service             = XmlService()
input_path              = cli_args_service.read_cli_args()
root                    = xml_service.get_root(input_path)
raw_diagram_elements    = xml_service.get_raw_diagram_elements(root)
filter_diagram_elements = xml_service.delete_metadata_elements(raw_diagram_elements)
