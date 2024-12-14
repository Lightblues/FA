
from data_utils.workflow import WorkflowNodeBase


def test_tool_node():
    # 同程开发票 https://tde.xiaowei.cloud.tencent.com/workflow?appid=1859204753515085824&workflow_id=67a4f791-dd03-44f5-b89d-2992f9fba3d0&seat_biz_id=1736943361528737792
    tool_node_dict = {
        "NodeID": "d18b4d6a-e637-acbb-f80c-24f3a1d0831b",
        "NodeName": "查询开票方式",
        "NodeDesc": "",
        "NodeType": "TOOL",
        "Inputs": [],
        "Outputs": [{
            "Title": "Output",
            "Type": "OBJECT",
            "Required": [],
            "Properties": [
                {
                    "Title": "invoicing_method",
                    "Type": "STRING",
                    "Required": [],
                    "Properties": [],
                    "Desc": "开票方式"
                }
            ],
            "Desc": "输出内容"
        }],
        "NextNodeIDs": ["fdbd7dd2-d89a-5be2-d3d9-520626b7b738"],
        "NodeUI": "",
        "ToolNodeData": {
            "API": {"URL": "http://11.141.203.151:8089/get_invoicing_method", "Method": "GET", "authType": "NONE", "KeyLocation": "HEADER", "KeyParamName": "", "KeyParamValue": ""},
            "Header": [],
            "Query": [{'ParamName': 'order_id', 'ParamDesc': '订单编号', 'ParamType': 'STRING', 'Input': {'InputType': 'REFERENCE_OUTPUT', 'Reference': {'NodeID': '5d1e2abc-3308-b490-7ff0-591f6ec9f640', 'JsonPath': 'Output.订单编号'}}, 'IsRequired': True, 'SubParams': []}], 
            "Body": []
        }
    }
    tool_node = WorkflowNodeBase(**tool_node_dict)
    # print(type(tool_node), type(tool_node.NodeData))
    # print(tool_node.NodeData)
    print(tool_node)
    print()

if __name__ == '__main__':
    test_tool_node()