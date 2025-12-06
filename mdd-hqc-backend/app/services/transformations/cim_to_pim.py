from app.services.xml_service import XmlService
from app.models.uvl import UVL
from app.services.uvl_service import UvlService

class CimToPim:
    def __init__(self, xml_service: XmlService, uvl: UVL, elements: list):
        self.xml_service        = xml_service
        self.uvl                = uvl
        self.elements           = elements
        self.uvl_service        = UvlService()
        self.element_to_actor   = {}

    # R1: Actores / Recursos -> Comentarios
    def apply_r1(self) -> None:
        self.element_to_actor = self.xml_service.get_element_to_actor_mapping()

    # R2: Goals / Tasks -> Features 
    def apply_r2(self) -> None:
        goal_elements = []
        task_elements = []
        for element in self.elements:
            attrib          = element.get("attrib", {})
            element_type    = attrib.get("type")
            element_id      = attrib.get("id")
            label           = self.xml_service.format_label(attrib.get("label", ""))
            
            if element_type == "goal" and element_id and label:
                goal_elements.append(
                    {
                        "id"    : element_id, 
                        "label" : label,
                    }
                )
            elif element_type == "task" and element_id and label:
                task_elements.append(
                    {
                        "id"    : element_id, 
                        "label" : label,
                    }
                )

        for goal_elem in goal_elements:
            goal_id         = goal_elem["id"]
            goal_label      = goal_elem["label"]
            feature_name    = self.uvl_service.format_feature_name(goal_label)
            category        = self.uvl_service.assign_category(goal_label)
            
            comments        = []
            actor_label     = self.element_to_actor.get(goal_id)
            if actor_label : comments.append(f"actor: {actor_label}")
            
            self.uvl.add_feature(
                name     = feature_name,
                category = category,
                kind     = "goal",
                comments = comments,
            )

        for task_elem in task_elements:
            task_id         = task_elem["id"]
            task_label      = task_elem["label"]
            feature_name    = self.uvl_service.format_feature_name(task_label)
            category        = self.uvl_service.assign_category(task_label)
            
            comments        = []
            actor_label     = self.element_to_actor.get(task_id)
            if actor_label : comments.append(f"actor: {actor_label}")
            
            self.uvl.add_feature(
                name     = feature_name,
                category = category,
                kind     = "task",
                comments = comments,
            )

    # R3: Softgoals -> Atributos (via qualification-link)
    def apply_r3(self) -> None:
        softgoal_labels = set(
            self.xml_service.get_elements_by_type(self.elements, "softgoal")
        )

        id_to_label = self.xml_service.map_id_to_label(self.elements)
        links       = self.xml_service.get_internal_links()

        for link in links:
            if link.get("type") != "qualification-link" : continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id : continue

            source_label = id_to_label.get(source_id)
            target_label = id_to_label.get(target_id)
            if not source_label or not target_label : continue

            if source_label in softgoal_labels and target_label not in softgoal_labels:
                softgoal_label = source_label
                feature_label  = target_label
            elif target_label in softgoal_labels and source_label not in softgoal_labels:
                softgoal_label = target_label
                feature_label  = source_label
            else:
                continue

            feature_name = self.uvl_service.format_feature_name(feature_label)
            category     = self.uvl_service.assign_category(feature_label)
            attr_name    = self.uvl_service.format_feature_name(softgoal_label)
            attr_value   = "true"

            self.uvl.add_attribute_to_feature(
                feature_name    = feature_name,
                category        = category,
                attr_name       = attr_name,
                attr_value      = attr_value,
            )

    # R4: Dependencias sociales -> requires
    def apply_r4(self) -> None:
        id_to_label = self.xml_service.map_id_to_label(self.elements)
        links       = self.xml_service.get_social_dependencies(self.elements)

        for link in links:
            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id : continue

            source_label = id_to_label.get(source_id)
            target_label = id_to_label.get(target_id)
            if not source_label or not target_label : continue

            depender_name = self.uvl_service.format_feature_name(source_label)
            dependee_name = self.uvl_service.format_feature_name(target_label)

            expr = f"{depender_name} => {dependee_name}"
            self.uvl.add_constraint(expr)

    # R5: needed-by / qualification-link / contribution / refinement
    def apply_r5(self) -> None:
        id_to_label = self.xml_service.map_id_to_label(self.elements)
        links       = self.xml_service.get_internal_links()
        refinements = self.xml_service.get_refinements()

        # R5.1: needed-by / qualification-link -> requires
        for link in links:
            link_type = link.get("type")
            if link_type not in {"needed-by", "qualification-link"} : continue

            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id : continue

            source_label = id_to_label.get(source_id)
            target_label = id_to_label.get(target_id)
            if not source_label or not target_label : continue

            src_name = self.uvl_service.format_feature_name(source_label)
            tgt_name = self.uvl_service.format_feature_name(target_label)

            expr = f"{tgt_name} => {src_name}"
            self.uvl.add_constraint(expr)

        # R5.2: contribution -> comentarios
        for link in links:
            if link.get("type") != "contribution" : continue

            raw_value = (link.get("value") or "").strip().lower()
            source_id = link.get("source")
            target_id = link.get("target")
            if not source_id or not target_id : continue

            source_label = id_to_label.get(source_id)
            target_label = id_to_label.get(target_id)
            if not source_label or not target_label : continue

            source_name         = self.uvl_service.format_feature_name(source_label)
            target_name         = self.uvl_service.format_feature_name(target_label)
            contribution_text   = f"{source_name} {raw_value} {target_name}"
            self.uvl.add_contribution(contribution_text)

        # R5.3: refinement AND / OR
        for ref in refinements:
            parent_id = ref.get("source")
            child_id  = ref.get("target")
            kind      = (ref.get("value") or "").strip().lower()
            if not parent_id or not child_id or kind not in {"and", "or"} : continue

            parent_label = id_to_label.get(parent_id)
            child_label  = id_to_label.get(child_id)
            if not parent_label or not child_label : continue

            parent_name = self.uvl_service.format_feature_name(parent_label)
            child_name  = self.uvl_service.format_feature_name(child_label)

            if kind == "and":
                expr = f"{child_name} => {parent_name}"
                self.uvl.add_constraint(expr)
            elif kind == "or":
                self.uvl.add_or_group(parent_name, child_name)