from typing import Dict, Any
from app.llm.interfaces import BaseLLMClient
from app.reviewer.rules import RULES
from app.reviewer.prompts import get_review_prompt

class ReviewerEngine:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    async def review_code(self, code: str) -> Dict[str, bool]:
        results = {}
        for rule in RULES:
            prompt = get_review_prompt(code, rule["prompt_instruction"])
            response = await self.llm_client.generate(prompt)
            
            # Simple parsing: check for TRUE/FALSE in the response
            clean_response = response.strip().upper()
            if "TRUE" in clean_response:
                results[rule["id"]] = True
            elif "FALSE" in clean_response:
                results[rule["id"]] = False
            else:
                # Default to False if we can't parse it, or we could raise an error
                # For POC, let's be strict
                raise ValueError(f"Could not parse LLM response for rule {rule['id']}: {response}")
        
        return results
