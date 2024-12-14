from pydantic import BaseModel
from typing import *
from .base import NodeDataBase

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
    Input: Dict[str, Any] # TODO: input (reference output)
    IsRequired: bool
    SubParams: List[Dict[str, Any]]

    def __str__(self):
        return f"{self.ParamName} ({self.ParamType})"

class ToolNodeData(NodeDataBase):
    """Tool node data

    {
        'API': {'URL': 'http://11.141.203.151:8089/get_invoicing_method', 'Method': 'GET', 'authType': 'NONE', 'KeyLocation': 'HEADER', 'KeyParamName': '', 'KeyParamValue': ''}, 
        'Header': [], 
        'Query': [{'ParamName': 'order_id', 'ParamDesc': '订单编号', 'ParamType': 'STRING', 'Input': {'InputType': 'REFERENCE_OUTPUT', 'Reference': {'NodeID': '5d1e2abc-3308-b490-7ff0-591f6ec9f640', 'JsonPath': 'Output.订单编号'}}, 'IsRequired': True, 'SubParams': []}], 
        'Body': []
    }
    """
    API: _TOOL_API
    Header: List[Dict[str, Any]]
    Query: List[_TOOL_QUERY]
    Body: List[Dict[str, Any]]

    def __str__(self):
        return f"[API] {self.API}  [Query] {self.Query}"