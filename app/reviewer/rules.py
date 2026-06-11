from typing import List, Dict

RULES: List[Dict[str, str]] = [
    {
        "id": "meaningful_variables",
        "description": "All variables have meaningful names",
        "prompt_instruction": "Check if all variables in the following Python code have meaningful and descriptive names. Single-letter variables (except in loops like i, j) should be flagged."
    },
    {
        "id": "docstring_logic",
        "description": "Docstring of function reflects the actual code's logic",
        "prompt_instruction": "Check if the docstrings for functions accurately describe what the code is doing. If there is a mismatch between the docstring description and the implementation logic, flag it."
    }
]
