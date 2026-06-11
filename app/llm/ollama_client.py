import httpx
from app.llm.interfaces import BaseLLMClient
from app.core.config import settings

class OllamaClient(BaseLLMClient):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.LLM_URL
        self.model = model or settings.LLM_NAME
        self.generate_url = f"{self.base_url}/api/generate"

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.generate_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                # In a real app, we might want more specific error handling
                raise Exception(f"Ollama generation failed: {str(e)}")
