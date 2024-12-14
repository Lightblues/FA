from data_utils.workflow import WorkflowNodeBase

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
            "Prompt": "根据<格式要求>处理<槽位值>中的槽位取值。\n\n<槽位名>\n医院名称\n</槽位名>\n\n<槽位值>\n{{hospital}}\n</槽位值>\n\n<槽位取值范围>\n北京积水潭医院，北京天坛医院，北京安贞医院，北京协和医院，北京中医药大学东方医院，北京朝阳医院，北京中日友好医院，北京世纪坛医院，北京大学人民医院，北京301医院，北京宣武医院，北京儿童医院，北京大学第一医院\n</槽位取值范围>\n\n<格式要求>\n- 如果<槽位取值范围>中存在与<槽位值>匹配的元素，则返回列表中的最匹配的元素作为处理后的槽位值。否则保持当前槽位值不变。\n- 只返回处理后的槽位值。\n</格式要求>"
        },
        "Inputs": [
            {
                "Name": "hospital",
                "Type": "STRING",
                "Input": {
                    "InputType": "REFERENCE_OUTPUT",
                    "Reference": {
                        "NodeID": "afb1f0c2-25c8-4891-4372-5dcdb1da1331",
                        "JsonPath": "Output.医院名称"
                    }
                },
                "Desc": "医院名称"
            }
        ],
        "Outputs": [],
        "NextNodeIDs": [
            "cc5e6402-0a10-8845-1cbc-edd08b468a42"
        ],
        "NodeUI": ""
    }
    llm_node = WorkflowNodeBase(**llm_node_dict)
    print(llm_node)
    print()

if __name__ == '__main__':
    test_llm_node()