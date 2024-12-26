"""updated
@240906
- [x] WorkflowType: text, code, flowchart, pdl
    with different subdirs and suffixes!
@241226
- [x] seperate other WorkflowType from PDL (e.g. another repo `FA_baselines`)

todos
"""

from enum import Enum
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from fa_core.common import Config
from fa_core.data.data_manager import FADataManager
from fa_core.data.pdl import PDL, ExtToolSpec


class WorkflowType(str, Enum):
    PDL = "PDL"
    # TEXT = "TEXT"
    # CODE = "CODE"
    # FLOWCHART = "FLOWCHART"
    # CORE = "CORE"


class DataHandler(BaseModel):
    type: Optional[WorkflowType] = None
    id: Optional[str] = None  # 000
    name: Optional[str] = None
    task_description: Optional[str] = None

    workflow_str: Optional[str] = None
    toolbox: List[ExtToolSpec] = Field(default_factory=list)
    pdl: Optional[PDL] = None

    cfg: Optional[Config] = None

    @classmethod
    def create(cls, cfg: Config, data_manager: Optional[FADataManager] = None, id_or_name: Optional[str] = None) -> "DataHandler":
        """Factory method to create a Workflow instance with all the initialization logic
        Args:
            cfg (Config): config
            data_manager (DataManager): data manager
            id_or_name (str): workflow id or name -> replace cfg.workflow_id

        1. setup .cfg, .data_manager
        2. set .type, .id, & .name, .task_description (from data_manager.workflow_infos)
        3. load .toolbox (f"tools/{self.id}.yaml")
        4. load .workflow (f"{self.type.subdir}/{self.id}{self.type.suffix}")
        """
        self = cls(cfg=cfg)  # Initialize with basic fields
        data_manager = data_manager or FADataManager(workflow_dataset=cfg.workflow_dataset)
        self.type = WorkflowType[cfg.workflow_type.upper()]
        self.id = self._get_workflow_id(id_or_name or cfg.workflow_id, data_manager.workflow_infos)

        # 1. load basic info
        infos = data_manager.workflow_infos[self.id]
        self.name = infos["name"]
        self.task_description = infos["task_description"]
        # self.task_detailed_description = infos['task_detailed_description']

        # 2. load the workflow & toolbox
        with open(data_manager.DIR_data_workflow / f"tools/{self.id}.yaml", "r") as f:
            self.toolbox = [ExtToolSpec(**tool) for tool in yaml.safe_load(f)]

        _dir = data_manager.DIR_data_workflow / self.cfg.pdl_version / f"{self.id}.yaml"
        self.pdl = PDL.load_from_file(_dir)
        self.pdl.tools = [tool.to_tool_definition() for tool in self.toolbox]  # NOTE to add apis to pdl
        self.workflow_str = self.pdl.to_str()  # self.pdl.procedure
        return self

    def _get_workflow_id(self, id_or_name: str, workflow_infos: dict):
        if id_or_name in workflow_infos:
            return id_or_name
        for id, info in workflow_infos.items():
            if info["name"] == id_or_name:
                return id
        raise ValueError(f"[ERROR] {id_or_name} not found in {workflow_infos.keys()}")

    def to_str(self):
        # return f"ID: {self.type}-{self.id}\nName: {self.name}\nTask: {self.task_description}\nWorkflow: {self.workflow}"
        info_dict = {
            "ID": f"{self.type}-{self.id}",
            "Name": self.name,
            "Task": self.task_description,
            "Workflow": self.task_description,  # just use natural language-format workflow?
        }
        return "".join([f"{k}: {v}\n" for k, v in info_dict.items()])
