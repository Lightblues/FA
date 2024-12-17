from pydantic import BaseModel
from typing import *
from .base import NodeDataBase
from ...variable import Variable

# --- Tool Node Data ---
class _TOOL_API(BaseModel):
    URL: str
    Method: str
    authType: str
    KeyLocation: str
    KeyParamName: str
    KeyParamValue: str

    def __str__(self):
        return f"{self.Method} {self.URL}"

class _TOOL_QUERY(BaseModel):
    ParamName: str
    ParamDesc: str
    ParamType: str
    Input: Variable
    IsRequired: bool
    SubParams: List[Dict[str, Any]]  # TODO: sub params? 

    def __str__(self):
        return f"{self.ParamName} (type: {self.ParamType}) (required: {self.IsRequired}) (input: {self.Input})"

class ToolNodeData(NodeDataBase):
    """Tool node data

    "ToolNodeData": {
        'API': {'URL': 'http://11.141.203.151:8089/get_invoicing_method', 'Method': 'GET', 'authType': 'NONE', 'KeyLocation': 'HEADER', 'KeyParamName': '', 'KeyParamValue': ''}, 
        'Header': [], 
        'Query': [
            {'ParamName': 'order_id', 'ParamDesc': '订单编号', 'ParamType': 'STRING', 'Input': {'InputType': 'REFERENCE_OUTPUT', 'Reference': {'NodeID': '5d1e2abc-3308-b490-7ff0-591f6ec9f640', 'JsonPath': 'Output.订单编号'}}, 'IsRequired': True, 'SubParams': []}
        ], 
        'Body': []
    }
    "ToolNodeData": {
        "API": {"URL": "http://11.141.203.151:8089/search_invoicing_progress", "Method": "POST", "authType": "NONE", "KeyLocation": "HEADER", "KeyParamName": "", "KeyParamValue": ""},
        "Header": [],
        "Query": [],
        "Body": [
            {"ParamName": "name", "ParamDesc": "姓名", "ParamType": "STRING", "Input": {"InputType": "REFERENCE_OUTPUT", "Reference": {"NodeID": "5d1e2abc-3308-b490-7ff0-591f6ec9f640", "JsonPath": "Output.姓名"}}, "IsRequired": true, "SubParams": []}
        ]
    }
    """
    API: _TOOL_API
    Header: List[Dict[str, Any]]
    Query: List[_TOOL_QUERY]
    Body: List[_TOOL_QUERY]

    def __str__(self):
        return f"[API] {self.API}  [Query] {self.Query} [Body] {self.Body}"