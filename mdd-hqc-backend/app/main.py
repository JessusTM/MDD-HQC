from app.services.xml_service import XmlService
from app.services.transformations.cim_to_pim import CimToPim
from app.services.cli_service import CliService
from app.models.uvl import UVL

def main():
    cli_service = CliService()
    xml_service = XmlService(cli_service)
    uvl         = UVL()
    elements    = xml_service.get_elements()      
    cim_to_pim  = CimToPim(xml_service, uvl, elements)
    cim_to_pim.apply_r1()
    cim_to_pim.apply_r2()

if __name__ == "__main__":
    main()
