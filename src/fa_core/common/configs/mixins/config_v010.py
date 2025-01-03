from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class V010Mixin(BaseModel):
    mode: str = "ui"  # exp, sim

    workflow_dataset: str = "v241127"
    workflow_type: str = "pdl"  # text, code, flowchart
    workflow_id: str = "000"  # id or name!
    exp_version: str = "default"
    exp_id: str = "default"
    # exp_mode: str = "session"  # not used yet

    user_mode: str = "llm_profile"  # llm_oow, manual, llm_profile
    user_llm_name: str = "gpt-4o"
    user_template_fn: Optional[str] = None  # "user_llm.jinja"
    user_profile_id: int = 0
    user_retry_limit: int = 3
    user_oow_ratio: float = 0.1

    bot_mode: str = "react_bot"
    bot_template_fn: Optional[str] = None  # "bot_flowbench.jinja"
    bot_llm_name: str = "gpt-4o"
    bot_llm_kwargs: Optional[Dict] = Field(default_factory=dict)
    bot_action_limit: int = 5
    bot_retry_limit: int = 3
    bot_pdl_controllers: List[Dict] = []

    api_mode: str = "llm"  # request/v01, llm
    api_template_fn: Optional[str] = None  # "api_llm.jinja"
    api_llm_name: str = "gpt-4o"
    api_entity_linking: bool = False
    api_entity_linking_llm: str = "gpt-4o"
    api_entity_linking_template: str = "entity_linking.jinja"
    api_mock_llm_name: str = "gpt-4o"

    ui_bot_mode: str = "ui_single_bot"  # ui_single_bot
    ui_available_models: Optional[List[str]] = None
    ui_available_templates: Optional[List[str]] = None
    ui_available_workflow_datasets: Optional[List[str]] = None
    ui_default_workflow_dataset: str = "v241127"
    ui_available_workflow_dirs: Optional[List[str]] = None  # subdirs
    ui_default_model: str = "default"
    ui_default_template: str = "bot_pdl_ui.jinja"
    ui_greeting_msg: str = "Hi, I'm HuaBu bot. How can I help you?"
    ui_user_additional_constraints: Optional[str] = None
    ui_tools: List[Dict] = []

    mui_available_workflows: Optional[List[str]] = None  # 可用的工作流列表
    mui_available_models: Optional[List[str]] = None
    mui_agent_main_available_templates: Optional[List[str]] = None
    mui_agent_main_default_model: str = "gpt-4o"
    mui_agent_main_default_template: str = "bot_mui_main_agent.jinja"
    mui_agent_workflow_template_fn: str = "bot_mui_workflow_agent.jinja"
    mui_agent_workflow_default_template: str = "bot_mui_workflow_agent.jinja"
    mui_agent_workflow_available_templates: Optional[List[str]] = None
    mui_default_workflow_dataset: str = "PDL_zh"
    mui_greeting_msg: str = "你好，有什么可以帮您?"
    mui_workflow_infos: List[Dict] = []

    db_uri: str = "mongodb://localhost:27017/"
    db_name: str = "agent-pdl"
    db_collection_single: str = "backend_single_sessions"
    db_collection_multi: str = "backend_multi_sessions"
    db_available_collections: List[str] = [db_collection_single, db_collection_multi]
    db_available_exp_versions: List[str] = []

    backend_url: str = "http://localhost:8100"

    st_default_page: str = "single"
    st_default_db_collection: str = db_collection_single
    st_default_exp_version: str = "default"

    simulate_num_persona: int = -1
    simulate_max_workers: int = 10
    simulate_force_rerun: bool = False

    judge_max_workers: int = 10
    judge_model_name: str = "gpt-4o"
    judge_conversation_id: Optional[str] = None  # the conversation to be judged
    # judge_passrate_threshold: int = 3
    judge_log_to: str = "wandb"
    judge_force_rejudge: bool = False
    judge_retry_limit: int = 3
