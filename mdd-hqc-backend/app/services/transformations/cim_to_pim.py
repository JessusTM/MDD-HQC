from app.services.xml_service import XmlService
from app.models.uvl import UVL

class CimToPim:
    def __init__(self, xml_service: XmlService, uvl: UVL):
        self.xml_service = xml_service
        self.uvl = uvl

    def apply_r1(self):
        elements = self.xml_service.get_elements()
        actors   = self.xml_service.get_elements_by_type(elements, "actor")
        self.uvl.create_file()
        for actor in actors:
            self.uvl.write("// " + actor + "\n")
