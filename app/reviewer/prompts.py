def get_review_prompt(code: str, rule_instruction: str) -> str:
    return f"""
Analyze the following Python code based on the specific rule provided.
Respond ONLY with either "TRUE" if the code adheres to the rule, or "FALSE" if it does not.
Do not provide any explanation.

Rule to check:
{rule_instruction}

Code to analyze:
```python
{code}
```

Adheres to rule? (TRUE/FALSE):
"""
