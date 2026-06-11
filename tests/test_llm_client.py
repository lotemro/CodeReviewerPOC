import pytest
from app.llm.ollama_client import OllamaClient
import httpx
import respx

@pytest.mark.asyncio
@respx.mock
async def test_ollama_generate_success():
    client = OllamaClient(base_url="http://localhost:11434", model="llama3")
    
    # Mock the Ollama API response
    respx.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "True"})
    )
    
    result = await client.generate("test prompt")
    assert result == "True"

@pytest.mark.asyncio
@respx.mock
async def test_ollama_generate_failure():
    client = OllamaClient(base_url="http://localhost:11434", model="llama3")
    
    respx.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(500)
    )
    
    with pytest.raises(Exception, match="Ollama generation failed"):
        await client.generate("test prompt")
