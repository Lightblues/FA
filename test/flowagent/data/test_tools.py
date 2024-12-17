# import yaml, json
# with open("/work/huabu/dataset/PDL/tools/000.yaml", 'r') as f:
#     data = yaml.safe_load(f)

# print(data)
# print()

from flowagent.data.tools import FunctionDefinition


f = {
    "name": "get_rain_probability",
    "description": "Get the probability of rain for a specific location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g., San Francisco, CA",
            }
        },
        "required": ["location"],
    },
    # 增加的属性
    "response": {},
    "url": "http://example.com/query_appointment",
    "method": "POST",
}
func = FunctionDefinition(**f)
print(func)
