from app.llm.interfaces import BaseLLMClient
from app.llm.ollama_client import OllamaClient
from app.core.config import settings

def get_llm_client() -> BaseLLMClient:
    """
    Factory function to get the configured LLM client.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        return OllamaClient()
    
    # We could add more providers here easily:
    # elif provider == "openai":
    #     return OpenAIClient()
    
    raise ValueError(f"Unsupported LLM provider: {provider}")
