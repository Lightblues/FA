from data_utils.workflow import WorkflowNodeBase


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
    answer_node = WorkflowNodeBase(**answer_node_dict)
    print(answer_node)
    print()


if __name__ == "__main__":
    test_answer_node()
