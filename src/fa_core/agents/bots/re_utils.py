import re


def re_parse_react_output(llm_response: str) -> dict:
    """Parse output with full `Tought, Action, Action Input`.
    NOTE:
    - unify the format of `Thought`, `Action`, `Action Input`
    - use `[END]` to mark the end of the output
    """
    pattern = r"(Thought|Action|Action Input):\s*(.*?)(?:\s*\[END\])?\s*(?=Thought:|Action:|Action Input:|\Z)"
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    result = {match.group(1): match.group(2).strip() for match in matches}
    return result


def re_parse_react_v01(llm_response: str) -> dict:
    """Parse output with full `Tought, Action, Action Input, Response`.
    NOTE:
    - deprecated!
    - use `Response` to differentiate between Action and Response
    - open-sourced LLM may generate two T/A/AI pairs, this re can only parse the last one! -- use `[END]` mark!
    """
    pattern = r"(Thought|Action|Action Input|Response):\s*(.*?)\s*(?=Thought:|Action:|Action Input:|Response:|\Z)"
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    result = {match.group(1): match.group(2).strip() for match in matches}
    return result
