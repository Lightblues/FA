""" 
/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tmp.py
/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
"""

# %%
import json
from engine_v2.role_api import exec_custom_tool

custom_functions = [
    {
        "name": "API-新闻查询",
        "description": "查询新闻",
        "parameters": {
            "type": "object",
            "properties": {
                "news_location": {
                    "type": "string",
                    "name": "新闻发生地",
                    "description": "新闻发生地",
                },
                "news_type": {
                    "type": "string",
                    "name": "新闻类型",
                    "enum": ["热搜", "时事"],
                    "description": "新闻类型",
                },
                "news_time": {
                    "type": "string",
                    "name": "新闻时间",
                    "description": "新闻时间",
                }
            },
            "required": ["news_location", "news_type"],
        },
        "response": {
            "type": "object",
            "properties": {
                "news_list": {
                    "type": "array",
                    "name": "查询到的新闻列表",
                    "description": "查询到的新闻列表",
                }
            }
        },
        "URL": "http://11.141.203.151:8089/search_news",
        "Method": "POST"
    },
    {
        "name": "API-校验挂号医院",
        "description": "校验挂号医院",
        "parameters": {
            "type": "object",
            "properties": {
                "hos_name": {
                    "type": "string",
                    "name": "医院名称",
                    "description": "需要校验的医院名称"
                }
            },
            "required": ["hos_name"]
        },
        "response": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "name": "医院存在类型",
                    "description": "医院存在的类型"
                }
            }
        },
        "URL": "http://11.141.203.151:8089/jiaoyanyiyuan",
        "Method": "GET"
    }

]

# 测试API传入方式, 报错处理等
action_info = {
    "tool_name": "API-新闻查询",
    "tool_args": 
    {
        "news_location": "北京",
        "news_type": "热搜",
        "news_time": "2022-01-01"
    }
}
action_info = {
    "tool_name": "API-校验挂号医院",
    "tool_args": 
    {
        # "hos_name": "北京大学人民医院",
        "hos_name_xxx": "xxx",
    }
}
res = exec_custom_tool(action_info, custom_functions)
print(res)