""" updated @240906 
"""
import yaml, copy
from pydantic import BaseModel
from typing import Optional, List, Dict

class Config(BaseModel):
    mode: str = "ui"

    workflow_dataset: str = "STAR"
    workflow_type: str = "pdl"     # text, code, flowchart
    workflow_id: str = "000"
    exp_version: str = "default"
    exp_mode: str = "session"       # turn, session
    exp_save_config: bool = False
    exp_check_if_run: bool = True
    
    user_mode: str = "llm_profile"  # llm_oow, manual, llm_profile
    user_llm_name: str = "gpt-4o"
    user_template_fn: Optional[str] = None    # "flowagent/user_llm.jinja"
    # user_profile: bool = True # controlled by exp_mode
    user_profile_id: int = 0
    user_retry_limit: int = 3
    user_oow_ratio: float = 0.1
    
    bot_mode: str = "react_bot"
    bot_template_fn: Optional[str] = None     # "flowagent/bot_flowbench.jinja"
    bot_llm_name: str = "gpt-4o"
    bot_action_limit: int = 5
    bot_retry_limit: int = 3
    # pdl_check_dependency: bool = True
    # pdl_check_api_dup_calls: bool = True
    # pdl_check_api_dup_calls_threshold: int = 2
    # pdl_check_api_w_tool_manipulation: bool = False  # whether to check API calls with tool manipulation
    bot_pdl_controllers: List[Dict] = []
    pdl_version: str = "pdl"
    
    api_mode: str = "llm"           # request/v01, llm
    api_template_fn: Optional[str] = None     # "flowagent/api_llm.jinja"
    api_llm_name: str = "gpt-4o"
    api_entity_linking: bool = False
    api_entity_linking_llm: str = "gpt-4o"
    api_entity_linking_template: str = "flowagent/entity_linking.jinja"
    
    ui_available_models: Optional[List[str]] = None
    ui_available_templates: Optional[List[str]] = None
    ui_available_workflow_datasets: Optional[List[str]] = None
    ui_default_workflow_dataset: str = "PDL_zh"
    ui_available_workflow_dirs: Optional[List[str]] = None    # subdirs
    ui_available_workflows: Optional[List[str]] = None        # NOTE: 暂未生效
    ui_default_model: str = "default"
    ui_default_template: str = "bot_pdl_ui.jinja"
    ui_bot_template_fn: str = "flowagent/bot_pdl_ui.jinja"
    ui_bot_llm_name: str = "gpt-4o"
    ui_greeting_msg: str = "Hi, I'm HuaBu bot. How can I help you?"
    # ui_user_additional_constraints: str = None # move to ss.
    ui_tools: List[Dict] = []
    
    mui_available_workflows: Optional[List[str]] = None  # 可用的工作流列表
    # 下面两个为实际会用到的, 后面为UI配置项
    mui_agent_main_template_fn: str = "flowagent/bot_mui_main_agent.jinja"
    mui_agent_main_llm_name: str = "gpt-4o"
    mui_available_models: Optional[List[str]] = None
    mui_agent_main_available_templates: Optional[List[str]] = None
    mui_agent_main_default_model: str = "gpt-4o"
    mui_agent_main_default_template: str = "bot_mui_main_agent.jinja"
    # 同上
    # mui_agent_workflow_llm_name: str = "gpt-4o" # reuse `mui_agent_main_llm_name`
    mui_agent_workflow_template_fn: str = "flowagent/bot_mui_workflow_agent.jinja"
    mui_agent_workflow_default_template: str = "bot_mui_workflow_agent.jinja"
    mui_agent_workflow_available_templates: Optional[List[str]] = None
    mui_default_workflow_dataset: str = "PDL_zh"

    conversation_turn_limit: int = 20
    log_utterence_time: bool = True
    log_to_db: bool = True

    db_uri: str = 'mongodb://localhost:27017/'
    db_name: str = "agent-pdl"
    db_message_collection_name: str = "messages"
    db_meta_collection_name: str = "config"
    
    simulate_num_persona: int = -1
    simulate_max_workers: int = 10
    simulate_force_rerun: bool = False
    
    judge_max_workers: int = 10
    judge_model_name: str = "gpt-4o"
    judge_conversation_id: Optional[str] = None   # the conversation to be judged
    # judge_passrate_threshold: int = 3
    judge_log_to: str = "wandb"
    judge_force_rejudge: bool = False
    judge_retry_limit: int = 3

    def to_dict(self):
        return self.model_dump()  # .dict()
    #     return asdict(self)

    @classmethod
    def from_yaml(cls, yaml_file: str):
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        return cls(**data)
     
    def to_yaml(self, yaml_file: str):
        with open(yaml_file, 'w') as file:
            yaml.dump(self.model_dump(), file, sort_keys=False)
    
    @classmethod
    def from_dict(cls, dic: dict):
        return cls(**dic)
    
    def copy(self):
        return copy.deepcopy(self)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"Key '{key}' not found in Config")

if __name__ == '__main__':
    config_dict = {
        "workflow_dataset": "xxx",
        "workflow_type": "xxx",
        "workflow_id": "000",
        "xxx": "xxx"
    }
    cfg = Config.from_dict(config_dict)
    print(cfg)
