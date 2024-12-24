from fa_core.data import ToolDefinition


tool_response = {
    "type": "function",
    "function": {
        "name": "response_to_user",
        "description": "Response to user, and wait for user's response",
        "parameters": {
            "type": "object",
            "properties": {"content": {"type": "string", "description": "your response content to user"}},
            "required": ["content"],
        },
    },
}

tool_response = ToolDefinition(**tool_response)
