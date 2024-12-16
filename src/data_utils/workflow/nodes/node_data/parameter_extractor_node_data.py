from pydantic import BaseModel
from typing import *
from .base import NodeDataBase

class _PE_Parameter(BaseModel):
    RefParameterID: str
    Required: bool

class ParameterExtractorNodeData(NodeDataBase):
    """ 
    "Parameters": [
            {
                "RefParameterID": "89f2a582-d7c0-4518-bb5b-ab1225e5145f",
                "Required": true
            }
        ],
        "UserConstraint": "当需要对“发票类型”参数进行追问时，请严格按照以下内容进行追问：“ 您好，根据您的需求，您需要开发票。请问您需要哪种类型的发票呢？是电子普票、纸质普票还是纸质专票？”"
    }, 
    """
    Parameters: List[_PE_Parameter]
    UserConstraint: str
    def __str__(self):
        return "[PARAMETER_EXTRACTOR] " + " | ".join(str(p) for p in self.Parameters)
