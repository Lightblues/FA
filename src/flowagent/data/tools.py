""" 
- [ ] add to af_core

openai function_calling: https://platform.openai.com/docs/assistants/tools/function-calling
https://platform.openai.com/docs/guides/function-calling
"""
# from openai.types import FunctionDefinition, FunctionParameters
from typing import Optional, Dict
from typing_extensions import TypeAlias
from openai import BaseModel

FunctionParameters: TypeAlias = Dict[str, object]

class FunctionDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[FunctionParameters] = None

