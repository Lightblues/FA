from tools import execute_tool_call


def print_stream(stream):
    for ch in stream:
        print(ch, end="", flush=True)
    print()


def test_web_search():
    tool_name = "web_search"
    tool_args = {"query": "上海 今天 天气"}
    res = execute_tool_call(tool_name, tool_args)
    print(res)
    print()


def test_hunyuan():
    tool_name = "hunyuan_search"
    tool_args = {"query": "上海 今天 天气"}
    res = execute_tool_call(tool_name, tool_args)
    print_stream(res)
    print()


# test_web_search()
test_hunyuan()
