import copy
import re
from typing import List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from .role import CustomRole, Role
from .tool_call import ToolCall


class Message(BaseModel):
    role: Union[str, CustomRole] = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")
    llm_name: Optional[str] = Field(None, description="Name of the language model")
    llm_prompt: Optional[str] = Field(None, description="Optional prompt associated with the message")
    llm_response: Optional[str] = Field(None, description="Response from the language model")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")
    utterance_id: Optional[int] = Field(None, description="ID of the utterance")
    type: Optional[str] = Field(None, description="Type of the message")
    apis: Optional[List[ToolCall]] = Field(None, description="List of API calls associated with the message")
    content_predict: Optional[str] = Field(None, description="Predicted content of the message")

    def model_post_init(self, __context):
        if isinstance(self.role, str):
            self.role = Role.get_by_rolename(self.role)
        # if self.apis:
        #     if not isinstance(apis[0], ToolCall):
        #         apis = [ToolCall.from_dict(i) for i in apis]
        #     self.apis = apis

    def to_str(self):
        return f"{self.role.prefix}{self.content}"

    def to_dict(self):
        data = self.model_dump()
        data["role"] = self.role.rolename
        return data

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return self.to_str()

    def copy(self):
        return copy.deepcopy(self)

    # auto determined api v.s. GT api calls (.apis, .type)
    def is_api_calling(self, content: str = None) -> bool:
        if content:
            return content.startswith("<Call API>")
        return self.role == Role.BOT and self.content.startswith("<Call API>")

    def get_api_infos(self, content: str = None) -> Tuple[str, str]:
        """
        return: action_name, action_parameters
        """
        # content = f"<Call API> {action_name}({action_parameters})"
        if content is None:
            content = self.content
        assert self.is_api_calling(content), f"Must be API calling message! But got {content}"
        content = content[len("<Call API> ") :].strip()
        re_pattern = r"(.*?)\((.*)\)"
        re_match = re.match(re_pattern, content)
        name, paras = re_match.group(1), re_match.group(2)
        return name, eval(paras)

    # def substitue_with_GT_content(self, GT_content: str):
    #     self.content, self.content_predict = GT_content, self.content

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if isinstance(self.role, (Role, CustomRole)):
            data["role"] = self.role.rolename
        return data
