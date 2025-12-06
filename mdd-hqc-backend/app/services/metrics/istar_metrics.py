from typing import Any, Dict, List

from app.services.xml_service import XmlService


class IstarMetricsService:
    def __init__(self, xml_service: XmlService, elements: List[dict]):
        self.xml_service = xml_service
        self.elements = elements

    def calculate(self) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}

        goal_labels = self.xml_service.get_elements_by_type(self.elements, "goal")
        task_labels = self.xml_service.get_elements_by_type(self.elements, "task")
        softgoals   = self.xml_service.get_elements_by_type(self.elements, "softgoal")
        resources   = self.xml_service.get_elements_by_type(self.elements, "resource")
        actors      = self.xml_service.get_elements_by_type(self.elements, "actor")
        agents      = self.xml_service.get_elements_by_type(self.elements, "agent")
        roles       = self.xml_service.get_elements_by_type(self.elements, "role")

        metrics["goals"]        = len(goal_labels)
        metrics["tasks"]        = len(task_labels)
        metrics["softgoals"]    = len(softgoals)
        metrics["resources"]    = len(resources)
        metrics["actors"]       = len(actors)
        metrics["agents"]       = len(agents)
        metrics["roles"]        = len(roles)

        social_dependencies             = self.xml_service.get_social_dependencies(self.elements)
        metrics["social_dependencies"]  = len(social_dependencies)

        internal_links      = self.xml_service.get_internal_links()
        needed_by_count     = 0
        qualification_count = 0
        contribution_count  = 0

        for link in internal_links:
            link_type = link.get("type")
            if link_type == "needed-by":
                needed_by_count += 1
            elif link_type == "qualification-link":
                qualification_count += 1
            elif link_type == "contribution":
                contribution_count += 1

        metrics["internal_links"] = {
            "needed_by"             : needed_by_count,
            "qualification_links"   : qualification_count,
            "contributions"         : contribution_count,
        }

        refinements = self.xml_service.get_refinements()
        and_count   = 0
        or_count    = 0

        for ref in refinements:
            kind = (ref.get("value") or "").strip().lower()
            if kind == "and":
                and_count += 1
            elif kind == "or":
                or_count += 1

        metrics["refinements"] = {
            "and"   : and_count,
            "or"    : or_count,
        }

        total_elements = (
            len(goal_labels)
            + len(task_labels)
            + len(softgoals)
            + len(resources)
            + len(actors)
            + len(agents)
            + len(roles)
        )
        metrics["total_nodes"] = total_elements

        total_links = (
            metrics["social_dependencies"]
            + needed_by_count
            + qualification_count
            + contribution_count
            + and_count
            + or_count
        )
        metrics["total_links"] = total_links

        return metrics
