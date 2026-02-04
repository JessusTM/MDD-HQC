from typing import Dict 
from app.models.llm_contract import InteractionInput, InteractionReport 
from app.services.interaction.llm_client import LLMInteractionEngine 
from app.services.interaction.rule_based import RuleBasedInteractionEngine 
from app.services.interaction.llm.factory import get_llm_client 
from app.models.uvl import UVL

def get_interaction_engine(provider: str = "ollama") -> object:

    if provider == "rule_based": 
        return RuleBasedInteractionEngine()
    
    if provider in ["ollama", "lmstudio"]: 
        llm_client = get_llm_client(provider) 
        return LLMInteractionEngine(llm_client)
    
    return RuleBasedInteractionEngine()

def run_interaction(payload: InteractionInput, provider: str = "ollama") -> InteractionReport:

    engine = get_interaction_engine(provider) 
    return engine.run(payload)

def apply_user_answers(uvl: UVL, answers: Dict) -> str:

    for block, value in answers.items(): 
        category = f"@{block}" if f"@{block}" in uvl.allowed_categories else "@Functionality" 
        uvl.add_feature(name=value, category=category)
    
    uvl.create_file()

    if uvl.FILE_NAME.exists(): 
        return uvl.FILE_NAME.read_text(encoding="utf-8") 
    return ""
