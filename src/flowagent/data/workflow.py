""" updated @240906
WorkflowType: text, code, flowchart, pdl
    with different subdirs and suffixes!
"""
import yaml, json, os
from dataclasses import dataclass, asdict, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Dict, Optional, Union
from .user_profile import UserProfile
from .config import Config
from .pdl import PDL

@dataclass
class DataManager:
    cfg: Config = None
    
    DIR_root = Path(__file__).resolve().parent.parent.parent.parent
    DIR_src_base = (DIR_root / "src")
    
    DIR_config = DIR_root / "src/baselines/configs"
    
    DIR_data_root = DIR_root / "dataset"
    
    DIR_data_flowbench = None               # subdir for specific dataset
    FN_data_flowbench_infos = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self._build_workflow_infos(cfg.workflow_dataset)
        
    def _build_workflow_infos(self, workflow_dataset: str):
        self.DIR_data_flowbench = self.DIR_data_root / workflow_dataset
        self.FN_data_flowbench_infos = self.DIR_data_flowbench / "task_infos.json"
        infos: dict = json.load(open(self.FN_data_flowbench_infos, 'r'))
        self.data_version = infos['version']
        self.workflow_infos = infos['task_infos']
    
    def refresh_config(self, cfg: Config) -> None:
        self.cfg = cfg
        self._build_workflow_infos(cfg.workflow_dataset)

    @staticmethod
    def normalize_config_name(config_name:str):
        config_fn = DataManager.DIR_config / config_name
        return config_fn

    @property
    def num_workflows(self):
        return len(self.workflow_infos)
    
    def get_workflow_dataset_names(self):
        # return folder name in self.DIR_data_root
        all_entries = os.listdir(self.DIR_data_root)
        names = [entry for entry in all_entries if os.path.isdir(os.path.join(self.DIR_data_root, entry))]
        return names


class WorkflowType(Enum):
    TEXT = ("TEXT", "format for natural language", ".txt", 'text')
    CODE = ("CODE", "format of code", ".py", 'code')
    FLOWCHART = ("FLOWCHART", "format of flowchart", ".md", 'flowchart')
    PDL = ("PDL", "format of PDL", ".yaml", 'pdl')

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
    PDL = "PDL"

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
    
    data_manager: DataManager = None
    
    pdl: PDL = None         # only for PDL
    
    def __init__(self, data_manager:DataManager, type:str, id:str, name:str, task_background:str, load_user_profiles=False, **kwargs):
        self.data_manager = data_manager
        
        _type: WorkflowType = WorkflowType[type.upper()]
        self.type = _type
        self.id = id
        self.name = name
        self.task_background = task_background
        # load the workflow & toolbox
        with open(data_manager.DIR_data_flowbench / f"tools/{id}.yaml", 'r') as f:
            self.toolbox = yaml.safe_load(f)
        with open(data_manager.DIR_data_flowbench / f"{_type.subdir}/{id}{_type.suffix}", 'r') as f:
            self.workflow = f.read().strip()
        if load_user_profiles:
            with open(data_manager.DIR_data_flowbench / f"user_profile/{id}.json", 'r') as f:
                user_profiles = json.load(f)
            self.user_profiles = [UserProfile.load_from_dict(profile) for profile in user_profiles]
        
        if _type == WorkflowType.PDL:
            self.pdl = PDL.load_from_file(data_manager.DIR_data_flowbench / f"pdl/{id}.yaml")
    
    @classmethod
    def load_by_id(cls, data_manager:DataManager, id:str, type:str, **kwargs):
        assert id in data_manager.workflow_infos, f"[ERROR] {id} not found in {data_manager.workflow_infos.keys()}"
        infos = data_manager.workflow_infos[id]
        assert all([k in infos for k in ['name', 'task_background']]), f"[ERROR] missing key in {infos}"
        return cls(data_manager, type, id, **infos, **kwargs)
    
    def to_str(self):
        return f"{self.type} {self.id}: {self.name}\nTask: {self.task_background}\n---\n{self.workflow}"
