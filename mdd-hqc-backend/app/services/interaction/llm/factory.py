"""Factory helpers that instantiate the configured LLM interaction client."""

from .ollama_client import OllamaClient
from .lmstudio_client import LMStudioClient


def get_llm_client(provider: str):
    """Returns the LLM client that matches the requested provider name.

    This helper keeps provider selection in one place so the interaction layer can swap
    implementations without changing its orchestration code.
    """
    if provider == "ollama":
        return OllamaClient(model_name="mistral:latest")
    elif provider == "lmstudio":
        return LMStudioClient(model_name="Meta-Llama-3-8B-Instruct")
    else:
        raise ValueError(f"Proveedor LLM desconocido: {provider}")
