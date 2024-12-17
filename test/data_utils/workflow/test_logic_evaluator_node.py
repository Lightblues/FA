from data_utils.workflow import WorkflowNodeBase


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

    logic_node = WorkflowNodeBase(**logic_node_dict)
    print(logic_node)
    print()


if __name__ == "__main__":
    test_logic_node()
