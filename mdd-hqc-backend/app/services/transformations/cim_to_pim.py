from app.services.xml_service import XmlService
from app.models.uvl import UVL

class CimToPim:
    def __init__(self, xml_service: XmlService, uvl: UVL, elements : list):
        self.xml_service    = xml_service
        self.uvl            = uvl
        self.elements       = elements 

    def apply_r1(self):
        actors  = self.xml_service.get_elements_by_type(self.elements, "actor")
        agents  = self.xml_service.get_elements_by_type(self.elements, "agent")
        roles   = self.xml_service.get_elements_by_type(self.elements, "role")
        self.uvl.create_file()
        self.uvl.set_metadata(actors) 
        self.uvl.set_metadata(agents)
        self.uvl.set_metadata(roles)        

    def apply_r2(self):
        goals       = self.xml_service.get_elements_by_type(self.elements, "goal")
        softgoals   = self.xml_service.get_elements_by_type(self.elements, "softgoal")
        self.uvl.set_section("features", goals, softgoals)

    def apply_r3(self):
        links           = self.xml_service.get_internal_links()
        labels          = self.xml_service.map_id_to_label(self.elements)
        constraints     = []

        for link in links:
            link_type = link.get("type")
            source_id = link.get("source")
            target_id = link.get("target")
            raw_value = (link.get("value") or "").strip().lower()
            if not source_id or not target_id : continue

            source_label = labels.get(source_id)
            target_label = labels.get(target_id)
            if not source_label or not target_label : continue

            if link_type == "needed-by":
                constraints.append(f"{target_label} => {source_label}")
                continue

            if link_type == "qualification-link":
                constraints.append(f"{target_label} => {source_label}")
                continue

            if link_type == "contribution":
                if raw_value in {"make", "help"}:
                    constraints.append(f"{source_label} => {target_label}")
                elif raw_value in {"hurt", "break"}:
                    constraints.append(f"{source_label} => !{target_label}")
                continue
        if constraints:
            self.uvl.set_section("constraints", constraints)

    def apply_r4(self):
        links   = self.xml_service.get_social_dependencies(self.elements)
        labels  = self.xml_service.map_id_to_label(self.elements)

        constraints = []
        for link in links:
            source_id = link.get("source")
            target_id = link.get("target")

        source_label = labels.get(source_id)
        target_label = labels.get(target_id)

        if source_label and target_label:
            constraint_expression = f"{source_label} => {target_label}"
            constraints.append(constraint_expression)

        self.uvl.set_section("constraints", constraints)
