""" updated @240906 
"""
import yaml, copy
from dataclasses import dataclass, asdict, field

@dataclass
class Config:
    workflow_dataset: str = "STAR"
    workflow_type: str = "text"     # text, code, flowchart
    workflow_id: str = "000"
    exp_version: str = "default"
    
    user_mode: str = "llm_profile"
    user_llm_name: str = "gpt-4o"
    user_template_fn: str = "baselines/user_llm.jinja"
    user_profile: bool = True
    user_profile_id: int = 0
    
    bot_mode: str = "react_bot"
    bot_template_fn: str = "baselines/flowbench.jinja"
    bot_llm_name: str = "gpt-4o"
    bot_action_limit: int = 5
    pdl_check_dependency: bool = True
    pdl_check_api_dup_calls: bool = True
    pdl_check_api_dup_calls_threshold: int = 2
    
    api_mode: str = "llm"
    api_template_fn: str = "baselines/api_llm.jinja"
    api_llm_name: str = "gpt-4o"

    conversation_turn_limit: int = 20
    log_utterence_time: bool = True
    log_to_db: bool = True

    db_uri: str = 'mongodb://localhost:27017/'
    db_name: str = "pdl"
    db_message_collection_name: str = "messages"
    db_meta_collection_name: str = "config"
    
    simulate_num_persona: int = -1
    simulate_max_workers: int = 10
    
    judge_max_workers: int = 10
    judge_model_name: str = "gpt-4o"
    judge_conversation_id: str = None
    # judge_passrate_threshold: int = 3

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_yaml(cls, yaml_file: str):
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        obj = cls(**data)
        return obj
    
    def to_yaml(self, yaml_file: str):
        with open(yaml_file, 'w') as file:
            yaml.dump(asdict(self), file)
    
    def copy(self):
        return copy.deepcopy(self)
