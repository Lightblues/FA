from typing import Dict, Optional, Union

from pydantic import BaseModel


# class BotOutputType(Enum):
#     RESPONSE = ("RESPONSE", "response to the user")
#     ACTION = ("ACTION", "call an API")
#     END = ("END", "end the conversation")
#     SWITCH = ("SWITCH", "switch to another workflow")

#     def __init__(self, actionname, description):
#         self.actionname = actionname
#         self.description = description


class UserOutput(BaseModel):
    response_content: str = ""

    end_flag: str = "[END]"

    @property
    def is_end(self) -> bool:
        return self.end_flag in self.response_content


class BotOutput(BaseModel):
    thought: Optional[str] = None
    action: Optional[str] = None  # api name
    action_input: Optional[Dict] = None  # api paras. deprecated: Union[str, Dict]
    response: Optional[str] = None

    @property
    def workflow(self) -> str:
        """Get the target workflow name (if switched)"""
        if self.action and self.action.startswith("workflow_"):
            return self.action.split("_")[1]
        return None


class APIOutput(BaseModel):
    name: Optional[str] = None
    request: Optional[Union[str, Dict]] = None
    response_status_code: Optional[int] = None
    response_data: Optional[Union[str, Dict]] = None


# class MainBotOutput(BaseModel):
#     thought: Optional[str] = None
#     workflow: Optional[str] = None  # workflow name
#     response: Optional[str] = None
#     action: Optional[str] = None
#     action_input: Optional[Dict] = None


# class WorkflowBotOutput(BaseModel):
#     thought: Optional[str] = None
#     workflow: Optional[str] = None  # workflow name
#     response: Optional[str] = None
#     action: Optional[str] = None  # api name
#     action_input: Optional[Dict] = None  # api paras. deprecated: Union[str, Dict]
