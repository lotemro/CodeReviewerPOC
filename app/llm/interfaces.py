from typing import Protocol, runtime_checkable

@runtime_checkable
class BaseLLMClient(Protocol):
    async def generate(self, prompt: str) -> str:
        """Generates a response from the LLM based on the prompt."""
        ...
