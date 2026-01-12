from typing import List, Dict 
from app.services.llm.base import LLMInterface
from app.models.uvl import UVL
from app.services.xml_service import XmlService

class CIMInteractionService:
 
    def __init__(self, llm_client: LLMInterface, xml_service: XmlService, elements: List[Dict]):
        self.llm_client = llm_client
        self.xml_service = xml_service
        self.elements = elements
        self.uvl = UVL()

    def apply_user_answers(self, answers: Dict) -> Dict:

        for block, value in answers.items():
            category = f"@{block}" if f"@{block}" in self.uvl.allowed_categories else "@Functionality"
            self.uvl.add_feature(name=value, category=category)
        
        self.uvl.create_file()

        uvl_content = ""
        if self.uvl.FILE_NAME.exists():
            uvl_content = self.uvl.FILE_NAME.read_text(encoding="utf-8")
        
        return {"uvl_updated": uvl_content}
    
    def _build_questions(self, llm_analysis: Dict) -> List[Dict]:

        questions = []
        for missing in llm_analysis.get("missing", []):
            if missing == "Algorithm":
                questions.append({"block": "Algorithm", "question": "¿Qué tipo de algoritmo se utilizará?"})
            elif missing == "Programming": 
                questions.append({"block": "Programming", "question": "¿Qué framework/lenguaje se usará para programar?"}) 
            elif missing == "Integration_model": 
                questions.append({"block": "Integration_model", "question": "¿Qué modelo de integración se usará? (SOA, middleware, etc.)"}) 
            elif missing == "Quantum_HW_constraint": 
                questions.append({"block": "Quantum_HW_constraint", "question": "¿Qué restricciones de hardware cuántico aplican?"}) 
            elif missing == "Functionality": 
                questions.append({"block": "Functionality", "question": "¿Qué funcionalidad principal debe cubrir el sistema?"})
        
        return questions
    
    def generate_draft_and_questions(self) -> Dict:
       
        self.uvl.clear()

        for el in self.elements:
            label = self.xml_service.format_label(el["attrib"].get("label"))
            type_ = el["attrib"].get("type")

            if type_ and label:
                category = f"@{type_}" if f"@{type_}" in self.uvl.allowed_categories else "@Functionality"
                self.uvl.add_feature(name=label, category=category)
            
        self.uvl.create_file()

        istar_elements = [
            {"type": el["attrib"].get("type"), "text": self.xml_service.format_label(el["attrib"].get("label"))}
            for el in self.elements
            if el["attrib"].get("type") and el["attrib"].get("label")

        ]

        llm_analysis = self.llm_client.analyze_istar_elements(istar_elements)

        questions = self._build_questions(llm_analysis)
        
        uvl_content = ""
        if self.uvl.FILE_NAME.exists():
            uvl_content = self.uvl.FILE_NAME.read_text(encoding="utf-8")
        
        return {
            "uvl_draft": uvl_content,
            "questions": questions,
            "analysis": llm_analysis,
        }
    