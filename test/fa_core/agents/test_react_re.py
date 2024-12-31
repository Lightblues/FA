import re

# NOTE: When meeting double ReAct output , the forllowing regex cannot work!!! (will only parse the last one!)
llm_response = """
Thought: 用户提供了医院名称和科室名称，接下来需要调用API进行医院名称和科室名称的归一化。
Action: 医院名称归一化
Action Input: {"hospital": "301"}
Response:

Thought: 需要调用科室名称归一化API。
Action: 科室名称归一化
Action Input: {"department_name": "口腔科"}
Response:
""".strip()
llm_response = """
Thought: 用户提供了医院名称“301”，需要验证该医院是否存在。
Action: check_hospital_exist
Action Input: {"hos_name": "北京301医院"}
[END]
""".strip()


def test_react_re():
    """
    `(.*?)` -- Match any characters (except newline) 0 or more times. The `?` is a non-greedy match.
    `(?:\s*\[END\])?` -- Unmatch `[END]`. The `(?:...)` is a non-capturing group. The last `?` is an optional.
    `re.DOTALL` -- The dot matches any character including newline.
    """

    pattern = r"(Thought|Action|Action Input):\s*(.*?)(?:\s*\[END\])?\s*(?=Thought:|Action:|Action Input:|\Z)"
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    result = {match.group(1): match.group(2).strip() for match in matches}
    print(result)


if __name__ == "__main__":
    test_react_re()
