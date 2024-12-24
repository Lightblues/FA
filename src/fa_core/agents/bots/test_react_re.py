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


def test_react_re():
    pattern = r"(Thought|Action|Action Input|Response):\s*(.*?)\s*(?=Thought:|Action:|Action Input:|Response:|\Z)"
    matches = re.finditer(pattern, llm_response, re.DOTALL)
    result = {match.group(1): match.group(2).strip() for match in matches}
    print(result)


if __name__ == "__main__":
    test_react_re()
