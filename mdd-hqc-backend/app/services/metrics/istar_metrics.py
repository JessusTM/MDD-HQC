import logging
from typing import Any, Dict
from app.models.istar import IstarModel

logger = logging.getLogger(__name__)


class IstarMetricsService:
    def __init__(self, xml_service: IstarModel):
        self.xml_service = xml_service

    def calculate(self) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}

        goals = self.xml_service.get_intentional_element_by_type("goal")
        tasks = self.xml_service.get_intentional_element_by_type("task")
        softgoals = self.xml_service.get_intentional_element_by_type("softgoal")
        resources = self.xml_service.get_intentional_element_by_type("resource")
        actors = self.xml_service.get_intentional_element_by_type("actor")
        agents = self.xml_service.get_intentional_element_by_type("agent")
        roles = self.xml_service.get_intentional_element_by_type("role")

        metrics["goals"] = len(goals)
        metrics["tasks"] = len(tasks)
        metrics["softgoals"] = len(softgoals)
        metrics["resources"] = len(resources)
        metrics["actors"] = len(actors)
        metrics["agents"] = len(agents)
        metrics["roles"] = len(roles)

        social_dependencies = self.xml_service.get_social_dependencies()
        metrics["social_dependencies"] = len(social_dependencies)

        internal_links = self.xml_service.get_internal_links()
        needed_by_count = 0
        qualification_count = 0
        contribution_count = 0

        for link in internal_links.values():
            link_type = link.get("type")
            if link_type == "needed-by":
                needed_by_count += 1
            elif link_type == "qualification-link":
                qualification_count += 1
            elif link_type == "contribution":
                contribution_count += 1

        metrics["internal_links"] = {
            "needed_by": needed_by_count,
            "qualification_links": qualification_count,
            "contributions": contribution_count,
        }

        refinements = self.xml_service.get_refinements()
        and_count = 0
        or_count = 0

        for ref in refinements.values():
            kind = (ref.get("value") or "").strip().lower()
            if kind == "and":
                and_count += 1
            elif kind == "or":
                or_count += 1

        metrics["refinements"] = {
            "and": and_count,
            "or": or_count,
        }

        total_elements = (
            len(goals)
            + len(tasks)
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

        logger.debug(
            "iStar metrics calculated: total_nodes=%s, total_links=%s",
            total_elements,
            total_links,
        )
        return metrics
