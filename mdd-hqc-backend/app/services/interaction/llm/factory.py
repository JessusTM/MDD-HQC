from .ollama_client import OllamaClient
from .lmstudio_client import LMStudioClient

def get_llm_client(provider: str):
    if provider == "ollama":
        return OllamaClient(model_name="mistral:latest")
    elif provider == "lmstudio":
        return LMStudioClient(model_name="Meta-Llama-3-8B-Instruct")
    else:
        raise ValueError(f"Proveedor LLM desconocido: {provider}")