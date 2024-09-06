""" updated @240906
WorkflowType: text, code, flowchart
    with different subdirs and suffixes!
"""
import yaml, json
from dataclasses import dataclass, asdict, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Dict, Optional, Union
from .user_profile import UserProfile

@dataclass
class DataManager:
    DIR_root = Path(__file__).resolve().parent.parent.parent.parent
    DIR_data_base = (DIR_root / "dataset/v240830")
    DIR_src_base = (DIR_root / "src")
    
    DIR_engine_config = DIR_root / "src/baselines/configs"
    
    DIR_data_flowbench = DIR_root / "dataset/flowbench"
    FN_data_flowbench_infos = DIR_data_flowbench / "task_infos.json"

    def normalize_workflow_dir(self, workflow_dir:Union[str, Path]):
        # Convert Path to string if necessary
        if isinstance(workflow_dir, Path):
            workflow_dir = str(workflow_dir)
        if not workflow_dir.startswith("/apdcephfs"):
            file_name = workflow_dir.split("/")[-1]
            workflow_dir = self.DIR_data_base / file_name
        return workflow_dir
    
    def normalize_config_name(self, config_name:str):
        config_fn = self.DIR_engine_config / config_name
        return config_fn



class WorkflowType(Enum):
    TEXT = ("TEXT", "format for natural language", ".txt", 'text')
    CODE = ("CODE", "format of code", ".py", 'code')
    FLOWCHART = ("FLOWCHART", "format of flowchart", ".md", 'flowchart')

    def __init__(self, workflow_type, description, suffix, subdir):
        self.workflow_type: str = workflow_type
        self.description: str = description
        self.suffix: str = suffix
        self.subdir: str = subdir
    
    @property
    def types(self):
        types_upper = list(map(lambda x: x.value[0], WorkflowType))
        types_lower = list(map(lambda x: x.value[0].lower(), WorkflowType))
        return types_upper + types_lower

    def __str__(self):
        return self.workflow_type

class WorkflowTypeStr(str, Enum):
    TEXT = "TEXT"
    CODE = "CODE"
    FLOWCHART = "FLOWCHART"

@dataclass
class Tool:
    api_name: str = None
    api_desc: str = None
    input_paras: Dict = None
    output_paras: Dict = None

@dataclass
class Workflow:  # rename -> Data
    type: WorkflowType = None
    id: str = None              # 000
    name: str = None
    task_background: str = None
    workflow: str = None
    toolbox: List[Tool] = field(default_factory=list)   # apis
    user_profiles: List[UserProfile] = field(default_factory=list) # user profiles
    
    def __init__(self, type:str, id:str, name:str, task_background:str, load_user_profiles=False, **kwargs):
        _type: WorkflowType = WorkflowType[type.upper()]
        self.type = _type
        self.id = id
        self.name = name
        self.task_background = task_background
        # load the workflow & toolbox
        with open(DataManager.DIR_data_flowbench / f"tools/{id}.yaml", 'r') as f:
            self.toolbox = yaml.safe_load(f)
        with open(DataManager.DIR_data_flowbench / f"{_type.subdir}/{id}{_type.suffix}", 'r') as f:
            self.workflow = f.read().strip()
        if load_user_profiles:
            with open(DataManager.DIR_data_flowbench / f"user_profiles/{id}.json", 'r') as f:
                user_profiles = json.load(f)
            self.user_profiles = [UserProfile.load_from_dict(profile) for profile in user_profiles]
    
    @classmethod
    def load_by_id(cls, id:str, type:str, **kwargs):
        workflow_infos: dict = json.load(open(DataManager.FN_data_flowbench_infos, 'r'))
        assert id in workflow_infos, f"[ERROR] {id} not found in {DataManager.FN_data_flowbench_infos.keys()}"
        infos = workflow_infos[id]
        assert all([k in infos for k in ['name', 'task_background']]), f"[ERROR] missing key in {infos}"
        return cls(type, id, **infos, **kwargs)


if __name__ == '__main__':
    workflow = Workflow(
        _type='text',
        id="000",
        name="flight_booking_inquiry",
        task_background="search for flight tickets",
    )
    print(workflow)