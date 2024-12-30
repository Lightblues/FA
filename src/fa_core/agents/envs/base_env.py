"""
ref:
    https://github.com/geekan/MetaGPT/blob/main/metagpt/context_mixin.py
"""

from typing import Any, Dict

from pydantic import BaseModel, Field

from fa_core.common import Config, PromptUtils
from fa_core.data import BotOutput, Conversation, FAWorkflow


class StatusForPrompt(BaseModel):
    """
    Status for prompt
    """

    current_time: str = Field(default_factory=lambda: PromptUtils.get_formated_time())  # FIXME: update time each status?
    user_additional_constraints: str = ""
    api_duplication_controller: Dict[str, str] = Field(default_factory=dict)
    api_dependency_controller: Dict[str, str] = Field(default_factory=dict)
    session_length_controller: Dict[str, str] = Field(default_factory=dict)

    # s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."

    def to_str(self) -> str:
        """Generate status string suitable for prompt"""
        return "\n".join(f"{k}: {v}" for k, v in self.model_dump().items() if v)


class Context(BaseModel):
    cfg: Config
    workflow: FAWorkflow
    conv: Conversation

    status_for_prompt: StatusForPrompt = Field(default_factory=StatusForPrompt)
