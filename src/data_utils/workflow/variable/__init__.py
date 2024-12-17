from pydantic import BaseModel
from typing import *
from enum import Enum



class _UserInput(BaseModel):
    UserInputValue: List[str]

class _InputTypeEnum(Enum):
    REFERENCE_OUTPUT = "REFERENCE_OUTPUT"       # Reference -> _Reference
    USER_INPUT = "USER_INPUT"                   # Fixed value -> _UserInput
    CUSTOM_VARIABLE = "CUSTOM_VARIABLE"         # Custom variable. e.g., session_id


class _Reference(BaseModel):
    NodeID: str
    JsonPath: str

class Variable(BaseModel):
    """ 
    {
        "InputType": "USER_INPUT",
        "UserInputValue": {
            "Values": ["白金卡"]
        }
    },
    {
        "InputType": "REFERENCE_OUTPUT",
        "Reference": {
            "NodeID": "0fa5e5a6-95fb-016e-8d08-50901034a8ea",
            "JsonPath": "Output.invoicing_progress"
        }
    }
    """
    InputType: _InputTypeEnum
    Reference: _Reference = None
    UserInput: Union[_UserInput, None] = None # NOTE that UserInput can be None whetn InputType="USER_INPUT" (default branch)
    CustomVarID: str = None

    def __str__(self):
        if self.InputType == _InputTypeEnum.REFERENCE_OUTPUT:
            return f"Reference({self.Reference.NodeID}.{self.Reference.JsonPath})"
        elif self.InputType == _InputTypeEnum.USER_INPUT:
            return 'Default' if self.UserInput is None else  f"UserInput({self.UserInput.UserInputValue})"
        elif self.InputType == _InputTypeEnum.CUSTOM_VARIABLE:
            return f"CustomVariable({self.CustomVarID})"
        else:
            raise ValueError(f"Invalid input type: {self.InputType}")
