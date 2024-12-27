"""updated
@240906
- [x] WorkflowType: text, code, flowchart, pdl
    with different subdirs and suffixes!
@241226
- [x] seperate other WorkflowType from PDL (e.g. another repo `FA_baselines`)
- [x] remove config from FADataHandler

todos
"""

from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from fa_core.common import Config
from fa_core.data.data_manager import FADataManager
from fa_core.data.pdl import PDL, ExtToolSpec


class FAWorkflow(BaseModel):
    """Data structure for a single task

    Usage::

        # 1. create directly
        workflow = FAWorkflow(workflow_dataset="PDL", workflow_id="000")
        # ... or from config
        workflow = FAWorkflow.from_config(Config.from_yaml("default.yaml"))

        # 2. with the FADataManager
        workflow = FADataManager.get_workflow(workflow_dataset="PDL", workflow_id="000")
    """

    workflow_dataset: str
    workflow_id: str  # 000

    name: Optional[str] = None
    task_description: Optional[str] = None

    toolbox: Optional[List[ExtToolSpec]] = None
    pdl: Optional[PDL] = None

    def model_post_init(self, __context: Any) -> None:
        self.workflow_id = FADataManager.unify_workflow_name(self.workflow_dataset, self.workflow_id)

        # 1. load basic info
        infos = FADataManager.get_workflow_infos(self.workflow_dataset)[self.workflow_id]
        self.name = infos["name"]
        self.task_description = infos["task_description"]
        # self.task_detailed_description = infos['task_detailed_description']

        # 2. load the workflow & toolbox
        with open(FADataManager.DIR_data_root / self.workflow_dataset / f"tools/{self.workflow_id}.yaml", "r") as f:
            self.toolbox = [ExtToolSpec(**tool) for tool in yaml.safe_load(f)]
        self.pdl = PDL.load_from_file(FADataManager.DIR_data_root / self.workflow_dataset / f"pdl/{self.workflow_id}.yaml")
        self.pdl.tools = [tool.to_tool_definition() for tool in self.toolbox]  # NOTE to add apis to pdl

    @classmethod
    def from_config(cls, cfg: Config) -> "FAWorkflow":
        return cls(workflow_dataset=cfg.workflow_dataset, workflow_id=cfg.workflow_id)

    # def to_str(self):
    #     # return f"ID: {self.type}-{self.id}\nName: {self.name}\nTask: {self.task_description}\nWorkflow: {self.workflow}"
    #     info_dict = {
    #         "ID": f"{self.type}-{self.id}",
    #         "Name": self.name,
    #         "Task": self.task_description,
    #         "Workflow": self.task_description,  # just use natural language-format workflow?
    #     }
    #     return "".join([f"{k}: {v}\n" for k, v in info_dict.items()])
