import re


def re_parse_react_output(llm_response: str) -> dict:
    """Parse output with full `Tought, Action, Action Input`."""
    pattern = r"(Thought|Action|Action Input):\s*(.*?)(?:\s*\[END\])?\s*(?=Thought:|Action:|Action Input:|\Z)"
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    result = {match.group(1): match.group(2).strip() for match in matches}
    return result
