from tools import function_to_schema, web_search


def test_function_to_schema():
    tool_schema = function_to_schema(web_search)
    print(tool_schema)


print()
