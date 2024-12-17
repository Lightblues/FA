import inspect
from typing import Any, Callable, Dict


def function_to_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    """
    Convert a function to an API schema.

    The output schema is a JSON-compatible dictionary with the following structure:

    {
        "type": "function",
        "function": {
            "name": <str>,
            "description": <str>,
            "parameters": {
                "type": "object",
                "properties": {
                    <param_name>: {
                        "type": <type_name>
                    },
                    ...
                },
                "required": [<param_name>, ...]
            }
        }
    }

    The input function should have type annotations for its parameters and return type.
    The type annotations are used to determine the type of each parameter in the output schema.
    If a parameter has no type annotation, its type is assumed to be "string".
    If a parameter has a default value, it is not included in the "required" list.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for function {func.__name__}: {str(e)}")

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}")
        parameters[param.name] = {"type": param_type}

    required = [param.name for param in signature.parameters.values() if param.default == inspect._empty]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }
