import json
from functools import wraps
from typing import Union, Dict, Any, Iterator
from .schema import function_to_schema

TOOL_SCHEMAS = []
TOOLS_MAP = {}

def register_tool():
    """decorator: register tool
    
    USAGE::

        @register_tool()
        def my_tool(param1: str, param2: int):
            '''Tool description'''
            pass
    """
    def decorator(func):
        # generate schema
        schema = function_to_schema(func)
        # register to global
        TOOL_SCHEMAS.append(schema)
        TOOLS_MAP[func.__name__] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def execute_tool_call(name: str, args: Union[str, Dict]) -> Union[str, Iterator[str]]:
    """
    Execute a tool by name and arguments
    
    If the arguments are given as a string, it will be parsed as a JSON object.
    Otherwise, the arguments should be a dictionary.
    
    Args:
        name (str): The name of the tool
        args (Union[str, Dict]): The arguments for the tool
    
    Returns:
        object: The result of the tool
    """
    print(f"> [execute_tool_call]: {name}({args})")

    if isinstance(args, str):
        args = json.loads(args)

    return TOOLS_MAP[name](**args)
