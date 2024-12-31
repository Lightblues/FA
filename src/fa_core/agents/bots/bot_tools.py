from fa_core.data import ToolDefinition


tool_response = {
    "type": "function",
    "function": {
        "name": "response_to_user",
        "description": "Response to user, and wait for user's next message",
        "parameters": {
            "type": "object",
            "properties": {"content": {"type": "string", "description": "your response content to user"}},
            "required": ["content"],
        },
    },
}

tool_switch_main = {
    "type": "function",
    "function": {
        "name": "workflow_main",
        "description": "Switch to main workflow (when you cannot handle user's current request)",
        "parameters": {
            "type": "object",
            "properties": {"reason": {"type": "string", "description": "the reason to switch to main workflow"}},
            "required": ["reason"],
        },
    },
}

tool_response = ToolDefinition(**tool_response)
tool_switch_main = ToolDefinition(**tool_switch_main)
