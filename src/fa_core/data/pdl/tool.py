"""
openai function_calling: https://platform.openai.com/docs/assistants/tools/function-calling
https://platform.openai.com/docs/guides/function-calling

@241221
- [x] #feat  ExtToolSpec & ToolDefinition @OpenAI
"""

# from openai import BaseModel
# from openai.types.shared_params import FunctionDefinition, FunctionParameters
# from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function
# from openai.types.chat.chat_completion_message import ChatCompletionMessage
# from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from typing import Dict, Optional, List, Any
from typing_extensions import Literal, Required, TypedDict

from pydantic import BaseModel, Field
from typing_extensions import TypeAlias


""" --------------------------------------------
Function Definition
NOTE: use TypedDict instead of BaseModel for parameters definition
"""
# class FunctionDefinition(BaseModel):
#     name: str
#     description: Optional[str] = None
#     parameters: Optional[FunctionParameters] = None

FunctionParameters: TypeAlias = Dict[str, object]


class FunctionDefinition(TypedDict, total=False):
    name: Required[str]
    description: str
    parameters: FunctionParameters


class ChatCompletionToolParam(TypedDict, total=False):
    function: FunctionDefinition
    type: Literal["function"]


""" --------------------------------------------
Function Call & Message
"""


class Function(BaseModel):
    arguments: str
    name: str


class ChatCompletionMessageToolCall(BaseModel):
    id: str
    function: Function
    type: Literal["function"]


class ChatCompletionMessage(BaseModel):
    content: Optional[str] = None
    refusal: Optional[str] = None
    role: Literal["assistant"]
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None


""" -------------------------------------------------------------------
Customized Tool Definition with BaseModel
see https://platform.openai.com/docs/api-reference/chat/create for typings
"""
ToolParameterType = Literal[
    "string",
    "number",
    "integer",
    "object",
    "array",
    "boolean",
    "null",
    "int",
    "float",
    "bool",
    "object",
    "array_string",
    "array_int",
    "array_float",
    "array_bool",
    "array_object",  # extend from @data_utils.workflow.base.TypeEnum
]


class ToolParameter(BaseModel):
    # https://json-schema.org/understanding-json-schema/reference/type
    type: ToolParameterType = None
    description: str = ""
    enum: Optional[List[str]] = None

    name: Optional[str] = None  # NOTE: extended for Workflow


class ToolProperties(BaseModel):
    # NOTE:
    # https://json-schema.org/understanding-json-schema
    type: Literal["object"] = "object"
    properties: dict[str, ToolParameter] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class ToolSpec(BaseModel):
    """Tool Specification aligned with OpenAI"""

    name: str
    description: str = ""
    # The parameters the functions accepts, described as a JSON Schema object. See the guide for examples, and the JSON Schema reference for documentation about the format.
    parameters: ToolProperties = Field(default_factory=ToolProperties)

    def __str__(self):
        return str(self.model_dump(exclude_none=True, exclude_unset=True))

    def to_tool_definition(self) -> "ToolDefinition":
        return ToolDefinition(type="function", function=self)


class ToolDefinition(BaseModel):
    type: Literal["function"] = "function"
    function: ToolSpec

    def __str__(self):
        return str(self.model_dump())


class ExtToolSpec(ToolSpec):
    """Extended Tool Specification for Workflow"""

    # Add: url, method
    url: str = ""
    method: Literal["GET", "POST"] = "GET"
    extra_infos: Optional[Any] = None  # used for special needs during development!!!

    def to_tool_spec(self) -> ToolSpec:
        return ToolSpec(**self.model_dump())
