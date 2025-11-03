from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from app.models.transformation_result import TransformationResult


Node = Dict[str, Any]
Edge = Dict[str, Any]


class CimToPim:
    ACTOR_TYPES = {"actor", "agent", "role"}
    FEATURE_TYPES = {"goal", "softgoal"}
    RESTRICTION_TYPES = {"task", "boundary", "limit", "constraint"}

    def normalise_nodes_with_identifier_validation(self, nodes: Iterable[Node]) -> List[Node]:
        valid_nodes: List[Node] = []
        for node in nodes:
            if node.get("id"):
                valid_nodes.append(node)
        return valid_nodes

    def normalise_edges_with_required_endpoints(self, edges: Iterable[Edge]) -> List[Edge]:
        valid_edges: List[Edge] = []
        for edge in edges:
            if edge.get("source") and edge.get("target"):
                valid_edges.append(edge)
        return valid_edges

    def transform_actor_nodes_into_metadata_entries(self, nodes: Iterable[Node]) -> List[Dict[str, Any]]:
        metadata: List[Dict[str, Any]] = []
        for node in self.normalise_nodes_with_identifier_validation(nodes):
            if node.get("type") in self.ACTOR_TYPES:
                metadata.append(
                    {
                        "id": node["id"],
                        "name": node.get("label") or node.get("id"),
                        "actor_type": node.get("type"),
                        "attributes": node.get("attributes", {}),
                    }
                )
        return metadata

    def classify_feature_nodes_into_sections(self, nodes: Iterable[Node]) -> Dict[str, List[Dict[str, Any]]]:
        primary: List[Dict[str, Any]] = []
        quality: List[Dict[str, Any]] = []

        for node in self.normalise_nodes_with_identifier_validation(nodes):
            if node.get("type") not in self.FEATURE_TYPES:
                continue

            feature_entry = {
                "id": node["id"],
                "name": node.get("label") or node.get("id"),
            }

            if node.get("type") == "softgoal":
                quality.append(feature_entry)
            else:
                primary.append(feature_entry)

        return {"primary": primary, "quality": quality}

    def convert_restriction_nodes_to_catalogue(self, nodes: Iterable[Node]) -> List[Dict[str, Any]]:
        restricciones: List[Dict[str, Any]] = []
        for node in self.normalise_nodes_with_identifier_validation(nodes):
            if node.get("type") in self.RESTRICTION_TYPES:
                restricciones.append(
                    {
                        "id": node["id"],
                        "name": node.get("label") or node.get("id"),
                        "restriction_type": node.get("type"),
                    }
                )
        return restricciones

    def convert_edges_to_relations(self, edges: Iterable[Edge]) -> List[Dict[str, Any]]:
        relations: List[Dict[str, Any]] = []
        for edge in self.normalise_edges_with_required_endpoints(edges):
            relation: Dict[str, Any] = {
                "id": edge.get("id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
            }

            contribution_type = self.infer_contribution_type_from_edge_style(edge.get("style"))
            if contribution_type:
                relation["contribution"] = contribution_type

            if edge.get("label"):
                relation["label"] = edge["label"]

            relations.append(relation)

        return relations

    def infer_contribution_type_from_edge_style(self, style: Optional[str]) -> Optional[str]:
        if not style:
            return None

        style_lower = style.lower()
        if "dashed" in style_lower or "dash" in style_lower:
            return "weak"
        if "strokeColor=#" in style_lower:
            colour = style_lower.split("strokeColor=#")[-1][:6]
            if colour in {"82b366", "388e3c", "2e7d32"}:
                return "positive"
            if colour in {"b85450", "c62828", "d32f2f"}:
                return "negative"
        return None

    def transform_cim_model_to_pim_structure(self, model: Dict[str, List[Dict[str, Any]]]) -> TransformationResult:
        nodes = model.get("nodes", [])
        edges = model.get("edges", [])

        metadata = self.transform_actor_nodes_into_metadata_entries(nodes)
        features = self.classify_feature_nodes_into_sections(nodes)
        restrictions = self.convert_restriction_nodes_to_catalogue(nodes)
        relations = self.convert_edges_to_relations(edges)

        return TransformationResult(
            metadata=metadata,
            features=features,
            restrictions=restrictions,
            relations=relations,
        )
