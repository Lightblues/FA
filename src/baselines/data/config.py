""" updated @240906 
"""
import yaml
from dataclasses import dataclass, asdict, field

@dataclass
class Config:
    conversation_turn_limit: int = 20
    
    user_mode: str = "llm_profile"
    user_llm_name: str = "gpt-4o"
    user_template_fn: str = "baselines/user_llm.jinja"
    user_profile: bool = True
    user_profile_id: int = 0
    
    bot_mode: str = "react_bot"
    bot_template_fn: str = "baselines/flowbench.jinja"
    bot_llm_name: str = "gpt-4o"
    bot_action_limit: int = 5
    
    api_mode: str = "llm"
    api_template_fn: str = "baselines/api_llm.jinja"
    api_llm_name: str = "gpt-4o"
    
    workflow_id: str = "000"
    workflow_type: str = "text"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_yaml(cls, yaml_file: str, normalize: bool = True):
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        obj = cls(**data)
        return obj
