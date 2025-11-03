from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class XmlService:
    """Handle XML diagram parsing and transformation into cleaned graph structures."""
    DRAWIO_ROOT_PATH = "./diagram/mxGraphModel/root"

    def parse_from_path(self, path: Path) -> ET.Element:
        """Load the XML file from disk and return its root element."""

        return ET.parse(path).getroot()

    def parse_from_string(self, xml_content: str) -> ET.Element:
        """Convert raw XML content into an element tree representation."""

        try:
            return ET.fromstring(xml_content)
        except ET.ParseError as exc:
            raise ValueError("Archivo no válido...") from exc

    def collect_diagram_root_child_elements(self, root: ET.Element) -> Iterable[ET.Element]:
        """Collect child elements located under the main diagram root section."""

        diagram_root = root.find(self.DRAWIO_ROOT_PATH)
        if diagram_root is None:
            return []
        diagram_children = list(diagram_root)
        return diagram_children

    def normalise_xml_element_label_text(self, value: Optional[str]) -> str:
        """Normalise label values coming from Draw.io node attributes."""

        if not value:
            return ""
        decoded_value = unescape(value)
        value_without_tags = re.sub(r"<[^>]+>", " ", decoded_value)
        normalised_spaces = re.sub(r"\s+", " ", value_without_tags)
        cleaned_value = normalised_spaces.strip()
        return cleaned_value

    def extract_mxcell_geometry_attributes(self, node: Optional[ET.Element]) -> Dict[str, Any]:
        """Extract available geometry information stored within an mxCell node."""

        if node is None:
            return {}
        geometry = node.find("mxGeometry")
        if geometry is None:
            return {}
        geometry_data = {
            key: geometry.attrib.get(key)
            for key in ("x", "y", "width", "height")
            if geometry.attrib.get(key) is not None
        }
        return geometry_data

    def build_relevant_nodes_from_diagram_elements(
        self, children: Iterable[ET.Element]
    ) -> List[Dict[str, Any]]:
        """Build the collection of relevant nodes derived from diagram elements."""

        nodes: List[Dict[str, Any]] = []
        for element in children:
            if element.tag != "object":
                continue

            mx_cell = element.find("mxCell")
            node: Dict[str, Any] = {
                "id": element.attrib.get("id"),
                "type": element.attrib.get("type"),
                "label": self.normalise_xml_element_label_text(
                    element.attrib.get("label")
                ),
            }

            if mx_cell is not None:
                node["style"] = mx_cell.attrib.get("style")
                node["parent"] = mx_cell.attrib.get("parent")
                geometry = self.extract_mxcell_geometry_attributes(mx_cell)
                if geometry:
                    node["geometry"] = geometry

            extra_attributes = {}
            for key, value in element.attrib.items():
                if key in {"id", "type", "label"}:
                    continue
                extra_attributes[key] = value

            if extra_attributes:
                node["attributes"] = extra_attributes

            nodes.append(node)
        return nodes

    def build_connecting_edges_from_diagram_elements(
        self, children: Iterable[ET.Element]
    ) -> List[Dict[str, Any]]:
        """Generate edges that connect nodes within the cleaned diagram."""

        edges: List[Dict[str, Any]] = []
        for element in children:
            if element.tag != "mxCell":
                continue
            if element.attrib.get("edge") != "1":
                continue

            edge: Dict[str, Any] = {
                "id": element.attrib.get("id"),
                "source": element.attrib.get("source"),
                "target": element.attrib.get("target"),
                "label": self.normalise_xml_element_label_text(element.attrib.get("value")),
            }

            style = element.attrib.get("style")
            if style:
                edge["style"] = style
            edges.append(edge)
        return edges

    def get_raw_diagram_elements(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Return a direct dump of the diagram root child elements."""

        children = self.collect_diagram_root_child_elements(root)
        raw_elements: List[Dict[str, Any]] = []

        for child in children:
            raw_element = {
                "tag": child.tag,
                "attrib": dict(child.attrib),
            }
            raw_elements.append(raw_element)
        return raw_elements

    def remove_non_cell_metadata_elements(
        self, raw_diagram_elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out elements that do not represent diagram cells or geometries."""

        filtered: List[Dict[str, Any]] = []
        for element in raw_diagram_elements:
            tag = element.get("tag")
            if tag not in {"mxCell", "mxGeometry"}:
                filtered.append(element)
        return filtered

    def transform_frontend_xml_into_graph_structure(
        self, xml_content: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Transform XML received from the frontend into node and edge collections."""

        root = self.parse_from_string(xml_content)
        children = self.collect_diagram_root_child_elements(root)
        nodes = self.build_relevant_nodes_from_diagram_elements(children)
        edges = self.build_connecting_edges_from_diagram_elements(children)
        result = {"nodes": nodes, "edges": edges}
        return result

xml_service = XmlService()
