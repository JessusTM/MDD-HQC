from app.services.xml_service import XmlService
from app.models.uvl import UVL

class CimToPim:
    def __init__(self, xml_service: XmlService, uvl: UVL, elements : list):
        self.xml_service    = xml_service
        self.uvl            = uvl
        self.elements       = elements 

    def apply_r1(self):
        actors   = self.xml_service.get_elements_by_type(self.elements, "actor")
        self.uvl.create_file()
        self.uvl.set_metadata(actors) 

    def apply_r2(self):
        goals       = self.xml_service.get_elements_by_type(self.elements, "goal")
        self.uvl.set_section("features", goals)

    def apply_r3(self):
        tasks       = self.xml_service.get_elements_by_type(self.elements, "task")
        self.uvl.set_section("constraints", tasks)
