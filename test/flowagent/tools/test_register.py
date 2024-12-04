from flowagent.tools import function_to_schema, execute_tool_call, web_search, register_tool, TOOL_SCHEMAS, TOOLS_MAP

tool_name = "web_search"
tool_args = {"query": "上海 今天 天气"}
res = execute_tool_call(tool_name, tool_args)
print(res)
print()
