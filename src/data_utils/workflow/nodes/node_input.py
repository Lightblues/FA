from typing import *

from pydantic import BaseModel


# ---------------------------------------------------
# Inputs & Outputs
# ---------------------------------------------------


# class _InputData(BaseModel):
#     InputType: str
#     Reference: Dict[str, Any]  # TODO: reference node representation

#     def __str__(self):
#         return f"{self.InputType} {self.Reference}"

# class NodeInput(BaseModel):
#     Name: str
#     Type: str           # STRING
#     Input: _InputData
#     Desc: str

#     def __str__(self):
#         return f"[{self.Name}] ({self.Type}) {self.Input}"


class _NodeOutputProperty(BaseModel):
    Title: str
    Type: str
    Required: List[Any]
    Properties: List[Any]
    Desc: str


class NodeOutput(BaseModel):
    """
    - It seems that only the TOOL node has Outputs
    {
        "Title": "Output",
        "Type": "OBJECT",
        "Required": [],
        "Properties": [
            {"Title": "invoicing_method", "Type": "STRING", "Required": [], "Properties": [], "Desc": "开票方式"}
        ],
        "Desc": "输出内容"
    }
    """

    Title: str
    Type: str
    Required: List[str]
    Properties: List[_NodeOutputProperty]
    Desc: str
