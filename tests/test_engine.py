import pytest
from unittest.mock import AsyncMock
from app.reviewer.engine import ReviewerEngine
from app.llm.interfaces import BaseLLMClient

@pytest.mark.asyncio
async def test_review_code_success():
    mock_llm = AsyncMock(spec=BaseLLMClient)
    # Return TRUE for the first rule and FALSE for the second
    mock_llm.generate.side_effect = ["TRUE", "FALSE"]
    
    engine = ReviewerEngine(mock_llm)
    results = await engine.review_code("print('hello')")
    
    assert results["meaningful_variables"] is True
    assert results["docstring_logic"] is False
    assert mock_llm.generate.call_count == 2

@pytest.mark.asyncio
async def test_review_code_parse_error():
    mock_llm = AsyncMock(spec=BaseLLMClient)
    mock_llm.generate.return_value = "Maybe?"
    
    engine = ReviewerEngine(mock_llm)
    with pytest.raises(ValueError, match="Could not parse LLM response"):
        await engine.review_code("x = 1")
