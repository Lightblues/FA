from data_utils.workflow.workflow_node import WorkflowNode


def test_start_node():
    start_node_dict = {
        "NodeID": "c9c9a33a-5f7b-8596-a6a6-9b31f26f3978",
        "NodeName": "开始",
        "NodeDesc": "",
        "NodeType": "START",
        "StartNodeData": {},
        "Inputs": [],
        "Outputs": [],
        "NextNodeIDs": ["afb1f0c2-25c8-4891-4372-5dcdb1da1331"],
        "NodeUI": '{"data":{"content":"","isHovering":false,"isParallel":false,"source":false,"target":false,"debug":null,"error":false,"output":[]},"position":{"x":27,"y":281},"targetPosition":"left","sourcePosition":"right","selected":false,"measured":{"width":86,"height":44},"dragging":false}',
    }
    start_node = WorkflowNode(**start_node_dict)
    print(start_node)
    print()


def test_answer_node():
    # 同程开发票 https://tde.xiaowei.cloud.tencent.com/workflow?appid=1859204753515085824&workflow_id=67a4f791-dd03-44f5-b89d-2992f9fba3d0&seat_biz_id=1736943361528737792
    answer_node_dict = {
        "NodeID": "add330cd-5f5a-c74b-0562-27cdd489d954",
        "NodeName": "结束回复1",
        "NodeDesc": "",
        "NodeType": "ANSWER",
        "AnswerNodeData": {"Answer": "您的同程开发票操作已成功执行，开票方式为{{invoicingMethod}}   。"},
        "Inputs": [
            {
                "Name": "invoicingMethod",
                "Type": "STRING",
                "Input": {
                    "InputType": "REFERENCE_OUTPUT",
                    "Reference": {
                        "NodeID": "d18b4d6a-e637-acbb-f80c-24f3a1d0831b",
                        "JsonPath": "Output.invoicing_method",
                    },
                },
                "Desc": "开票方式",
            }
        ],
        "Outputs": [],
        "NextNodeIDs": [],
        "NodeUI": '{"data":{"content":"您的同程开发票操作已成功执行，开票方式为{{invoicingMethod}}   。","isHovering":false,"isParallel":false,"source":true,"target":false,"debug":null,"error":false,"output":[]},"position":{"x":1366,"y":62},"targetPosition":"left","sourcePosition":"right","selected":false,"measured":{"width":250,"height":129},"dragging":false}',
    }
    answer_node = WorkflowNode(**answer_node_dict)
    print(answer_node)
    print()


def test_llm_node():
    # 挂号 https://tde.xiaowei.cloud.tencent.com/workflow?appid=1859204753515085824&workflow_id=2c2895cc-17ea-43c7-98c6-2d7cadaa080f&seat_biz_id=1736943361528737792
    llm_node_dict = {
        "NodeID": "63a5ebb1-4f0d-872e-0abb-28f14bbcad13",
        "NodeName": "医院名称归一化",
        "NodeDesc": "",
        "NodeType": "LLM",
        "LLMNodeData": {
            "ModelName": "cs-normal-70b",
            "Temperature": 0.7,
            "TopP": 0.4,
            "MaxTokens": 6000,
            "Prompt": "根据<格式要求>处理<槽位值>中的槽位取值。\n\n<槽位名>\n医院名称\n</槽位名>\n\n<槽位值>\n{{hospital}}\n</槽位值>\n\n<槽位取值范围>\n北京积水潭医院，北京天坛医院，北京安贞医院，北京协和医院，北京中医药大学东方医院，北京朝阳医院，北京中日友好医院，北京世纪坛医院，北京大学人民医院，北京301医院，北京宣武医院，北京儿童医院，北京大学第一医院\n</槽位取值范围>\n\n<格式要求>\n- 如果<槽位取值范围>中存在与<槽位值>匹配的元素，则返回列表中的最匹配的元素作为处理后的槽位值。否则保持当前槽位值不变。\n- 只返回处理后的槽位值。\n</格式要求>",
        },
        "Inputs": [
            {
                "Name": "hospital",
                "Type": "STRING",
                "Input": {
                    "InputType": "REFERENCE_OUTPUT",
                    "Reference": {
                        "NodeID": "afb1f0c2-25c8-4891-4372-5dcdb1da1331",
                        "JsonPath": "Output.医院名称",
                    },
                },
                "Desc": "医院名称",
            }
        ],
        "Outputs": [],
        "NextNodeIDs": ["cc5e6402-0a10-8845-1cbc-edd08b468a42"],
        "NodeUI": "",
    }
    llm_node = WorkflowNode(**llm_node_dict)
    print(llm_node)
    print()


def test_tool_node():
    # 同程开发票 https://tde.xiaowei.cloud.tencent.com/workflow?appid=1859204753515085824&workflow_id=67a4f791-dd03-44f5-b89d-2992f9fba3d0&seat_biz_id=1736943361528737792
    tool_node_dict = {
        "NodeID": "d18b4d6a-e637-acbb-f80c-24f3a1d0831b",
        "NodeName": "查询开票方式",
        "NodeDesc": "",
        "NodeType": "TOOL",
        "Inputs": [],
        "Outputs": [
            {
                "Title": "Output",
                "Type": "OBJECT",
                "Required": [],
                "Properties": [
                    {
                        "Title": "invoicing_method",
                        "Type": "STRING",
                        "Required": [],
                        "Properties": [],
                        "Desc": "开票方式",
                    }
                ],
                "Desc": "输出内容",
            }
        ],
        "NextNodeIDs": ["fdbd7dd2-d89a-5be2-d3d9-520626b7b738"],
        "NodeUI": "",
        "ToolNodeData": {
            "API": {
                "URL": "http://11.141.203.151:8089/get_invoicing_method",
                "Method": "GET",
                "authType": "NONE",
                "KeyLocation": "HEADER",
                "KeyParamName": "",
                "KeyParamValue": "",
            },
            "Header": [],
            "Query": [
                {
                    "ParamName": "order_id",
                    "ParamDesc": "订单编号",
                    "ParamType": "STRING",
                    "Input": {
                        "InputType": "REFERENCE_OUTPUT",
                        "Reference": {
                            "NodeID": "5d1e2abc-3308-b490-7ff0-591f6ec9f640",
                            "JsonPath": "Output.订单编号",
                        },
                    },
                    "IsRequired": True,
                    "SubParams": [],
                }
            ],
            "Body": [],
        },
    }
    tool_node = WorkflowNode(**tool_node_dict)
    # print(type(tool_node), type(tool_node.NodeData))
    # print(tool_node.NodeData)
    print(tool_node)
    print()


def test_logic_node():
    # 同程开发票 https://tde.xiaowei.cloud.tencent.com/workflow?appid=1859204753515085824&workflow_id=67a4f791-dd03-44f5-b89d-2992f9fba3d0&seat_biz_id=1736943361528737792
    logic_node_dict = {
        "NodeID": "fdbd7dd2-d89a-5be2-d3d9-520626b7b738",
        "NodeName": "条件判断1",
        "NodeDesc": "",
        "NodeType": "LOGIC_EVALUATOR",
        "LogicEvaluatorNodeData": {
            "Group": [
                {
                    "NextNodeIDs": ["0fa5e5a6-95fb-016e-8d08-50901034a8ea"],
                    "Logical": {
                        "LogicalOperator": "UNSPECIFIED",
                        "Compound": [],
                        "Comparison": {
                            "Left": {
                                "InputType": "REFERENCE_OUTPUT",
                                "Reference": {
                                    "NodeID": "d18b4d6a-e637-acbb-f80c-24f3a1d0831b",
                                    "JsonPath": "Output.invoicing_method",
                                },
                            },
                            "LeftType": "STRING",
                            "Operator": "EQ",
                            "Right": {
                                "InputType": "USER_INPUT",
                                "UserInputValue": {"Values": ["平台开具"]},
                            },
                            "MatchType": "SEMANTIC",
                        },
                    },
                },
                {
                    "NextNodeIDs": ["add330cd-5f5a-c74b-0562-27cdd489d954"],
                    "Logical": {
                        "LogicalOperator": "UNSPECIFIED",
                        "Compound": [],
                        "Comparison": {
                            "Left": {
                                "InputType": "REFERENCE_OUTPUT",
                                "Reference": {
                                    "NodeID": "d18b4d6a-e637-acbb-f80c-24f3a1d0831b",
                                    "JsonPath": "Output.invoicing_method",
                                },
                            },
                            "LeftType": "STRING",
                            "Operator": "EQ",
                            "Right": {
                                "InputType": "USER_INPUT",
                                "UserInputValue": {"Values": ["酒店开具"]},
                            },
                            "MatchType": "SEMANTIC",
                        },
                    },
                },
                {"NextNodeIDs": ["5dfac315-9567-9735-45f8-034f8c86a772"]},
            ]
        },
        "Inputs": [],
        "Outputs": [],
        "NextNodeIDs": [],
        "NodeUI": '{"data":{"content":[{"content":[{"leftStr":"参数提取1.Output.订单编号","rightStr":"平台开具","operatorStr":"等于"}],"index":0,"id":"25cc41bf-9ed0-2b54-72c8-77ed92505732"},{"content":[{"leftStr":"查询开票方式.Output.invoicing_method","rightStr":"酒店开具","operatorStr":"等于"}],"index":1,"id":"4d9f9c9a-3728-206b-475d-f8d965afac4e"},{"content":[],"index":2,"id":"8a604b7d-3396-2fab-bf58-6dd84d0a0c81"}],"isHovering":false,"isParallel":false,"source":true,"target":true,"debug":null,"error":false,"output":[]},"position":{"x":1081,"y":23},"targetPosition":"left","sourcePosition":"right","selected":false,"measured":{"width":250,"height":204},"dragging":false}',
    }

    logic_node = WorkflowNode(**logic_node_dict)
    print(logic_node)
    print()


def test_code_executor_node():
    code_executor_node_dict = {
        "NodeID": "00edda9b-dda5-5f11-b846-6955959d0be8",
        "NodeName": "获取挂号时间和号类",
        "NodeDesc": "",
        "NodeType": "CODE_EXECUTOR",
        "CodeExecutorNodeData": {
            "Code": "\n# 仅支持数据转换或运算等操作, 请勿手动import, 已引入numpy和pandas以及部分内置的运算相关的包；不支持IO操作，如读取文件，网络通信等。\n# 请保存函数名为main,输入输出均为dict；最终结果会以json字符串方式返回，请勿直接返回不支持json.dumps的对象（numpy和pandas已增加额外处理）\ndef main(params: dict) -> dict:\n    data_time = params.get(\"data\", [])\n    if len(data_time) == 0:\n        return {'g_time':'', 'num_type':''}\n    return {\n        'g_time': data_time[0][\"time\"],\n        \"num_type\": data_time[0][\"num_type\"]\n    }\n",
            "Language": "PYTHON3",
        },
        "Inputs": [
            {
                "Name": "data",
                "Type": "ARRAY_OBJECT",
                "Input": {
                    "InputType": "REFERENCE_OUTPUT",
                    "Reference": {"NodeID": "b892a84e-c6ee-c230-4573-efc4f2a822b7", "JsonPath": "Output.data"},
                },
                "Desc": "可挂号日期信息",
            },
            {
                "Name": "data_num_type",
                "Type": "ARRAY_OBJECT",
                "Input": {
                    "InputType": "REFERENCE_OUTPUT",
                    "Reference": {"NodeID": "b892a84e-c6ee-c230-4573-efc4f2a822b7", "JsonPath": "Output.data_num_type"},
                },
                "Desc": "号类信息",
            },
        ],
        "Outputs": [
            {
                "Title": "Output",
                "Type": "OBJECT",
                "Required": [],
                "Properties": [
                    {"Title": "g_time", "Type": "STRING", "Required": [], "Properties": [], "Desc": "挂号时间"},
                    {"Title": "num_type", "Type": "STRING", "Required": [], "Properties": [], "Desc": "号类"},
                ],
                "Desc": "输出内容",
            }
        ],
        "NextNodeIDs": ["7d8a28e3-c98c-d1e9-c436-06dfc896b174"],
        "NodeUI": '{"data":{"content":{"outputs":["Output","Output.g_time","Output.num_type"],"inputs":["data","data_num_type"]},"isHovering":false,"isParallel":false,"source":true,"target":false,"debug":null,"error":false,"output":[{"id":"a613b901-79b1-a1c9-c0a2-a70373af8480","value":"Output","label":"Output","type":"OBJECT","children":[{"id":"e837e5ce-5927-78c9-047b-32877c56d38c","value":"g_time","label":"g_time","type":"STRING","children":[]},{"id":"9c732ba9-bf10-050b-7093-cb6d28b7e302","value":"num_type","label":"num_type","type":"STRING","children":[]}]}]},"position":{"x":4402.6728822316145,"y":277.16062875586005},"targetPosition":"left","sourcePosition":"right","selected":false,"measured":{"width":250,"height":124},"dragging":false}',
    }
    code_executor_node = WorkflowNode(**code_executor_node_dict)
    print(code_executor_node)
    print()


def test_parameter_extractor_node():
    parameter_extractor_node_dict = {
        "NodeID": "933d26b0-cc22-dfa2-771a-1f3d112a1e19",
        "NodeName": "确认其他日期挂号意愿",
        "NodeDesc": "",
        "NodeType": "PARAMETER_EXTRACTOR",
        "ParameterExtractorNodeData": {
            "Parameters": [{"RefParameterID": "244977e8-1f9f-42f8-b3b8-de9256e9c8e3", "Required": True}],
            "UserConstraint": "当需要对“其他日期挂号意愿”参数进行追问时，请严格按照以下内容进行追问：“系统显示 医院名称 科室名称 挂号时间 没有号源，但 同医院同科室其他日期号源-可挂号日期 有号，您看愿意改挂 同医院同科室其他日期号源-可挂号日期 的号吗？”",
        },
        "Inputs": [],
        "Outputs": [],
        "NextNodeIDs": ["efcd83a9-98fe-7c1d-793f-0699a78c4781"],
        "NodeUI": '{"data":{"content":"参数：其他日期挂号意愿","isHovering":false,"isParallel":false,"source":true,"target":false,"debug":null,"error":false,"output":[{"label":"Output","desc":"输出内容","optionType":"REFERENCE_OUTPUT","type":"object","children":[{"value":"244977e8-1f9f-42f8-b3b8-de9256e9c8e3","label":"其他日期挂号意愿","type":"STRING"}]}]},"position":{"x":4998.6728822316145,"y":329.16062875586},"targetPosition":"left","sourcePosition":"right","selected":false,"measured":{"width":250,"height":84},"dragging":false}',
    }
    parameter_extractor_node = WorkflowNode(**parameter_extractor_node_dict)
    print(parameter_extractor_node)
    print()


if __name__ == "__main__":
    test_start_node()
    test_answer_node()
    test_llm_node()
    test_tool_node()
    test_logic_node()
    test_code_executor_node()
    test_parameter_extractor_node()
