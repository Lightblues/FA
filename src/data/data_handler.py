"""updated @240906
WorkflowType: text, code, flowchart, pdl
    with different subdirs and suffixes!
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from common import Config
from .data_manager import DataManager
from .pdl import PDL, ExtToolSpec


class WorkflowType(str, Enum):
    TEXT = "TEXT"
    CODE = "CODE"
    FLOWCHART = "FLOWCHART"
    PDL = "PDL"
    CORE = "CORE"

    @property
    def description(self) -> str:
        return {
            "TEXT": "format for natural language",
            "CODE": "format of code",
            "FLOWCHART": "format of flowchart",
            "PDL": "format of PDL",
            "CORE": "format of CoRE",
        }[self.value]

    @property
    def suffix(self) -> str:
        return {"TEXT": ".txt", "CODE": ".py", "FLOWCHART": ".md", "PDL": ".yaml", "CORE": ".txt"}[self.value]

    @property
    def subdir(self) -> str:
        return self.value.lower()


class WorkflowTypeStr(str, Enum):
    TEXT = "text"
    CODE = "code"
    FLOWCHART = "flowchart"
    PDL = "pdl"
    CORE = "core"


class DataHandler(BaseModel):  # rename -> Data
    type: Optional[WorkflowType] = None
    id: Optional[str] = None  # 000
    name: Optional[str] = None
    task_description: Optional[str] = None

    workflow: Optional[str] = None
    toolbox: List[ExtToolSpec] = Field(default_factory=list)
    pdl: Optional[PDL] = None
    # core_flow: Optional[CoreFlow] = None

    # user_profiles: Optional[List[UserProfile]] = None
    # reference_conversations: Optional[List[ConversationWithIntention]] = None
    # user_oow_intentions: Optional[List[OOWIntention]] = None

    cfg: Optional[Config] = None

    @classmethod
    def create(cls, cfg: Config, data_manager: Optional[DataManager] = None, id_or_name: Optional[str] = None) -> "DataHandler":
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
        data_manager = data_manager or DataManager(cfg)
        self.type = WorkflowType[cfg.workflow_type.upper()]
        self.id = self._get_workflow_id(id_or_name or cfg.workflow_id, data_manager.workflow_infos)

        # 1. load basic info
        infos = data_manager.workflow_infos[self.id]
        self.name = infos["name"]
        self.task_description = infos["task_description"]
        # self.task_detailed_description = infos['task_detailed_description']

        # 2. load the workflow & toolbox
        # TODO: update toolbox
        with open(data_manager.DIR_data_workflow / f"tools/{self.id}.yaml", "r") as f:
            self.toolbox = [ExtToolSpec(**tool) for tool in yaml.safe_load(f)]
        if self.type == WorkflowType.PDL:  # sepcial for PDL
            _dir = data_manager.DIR_data_workflow / self.cfg.pdl_version / f"{self.id}.yaml"
            self.pdl = PDL.load_from_file(_dir)
            self.pdl.tools = [tool.to_tool_definition() for tool in self.toolbox]  # NOTE to add apis to pdl
            self.workflow = self.pdl.to_str()  # self.pdl.procedure
        else:
            with open(
                data_manager.DIR_data_workflow / f"{self.type.subdir}/{self.id}{self.type.suffix}",
                "r",
            ) as f:
                self.workflow = f.read().strip()
        # if self.type == WorkflowType.CORE:
        #     self.core_flow = CoreFlow.load_from_file(data_manager.DIR_data_workflow / f"core/{self.id}.txt")
        # 3. load the user infos
        # load user profiles only when exp!
        # if self.cfg.mode == "exp":
        #     if self.cfg.exp_mode == "session":  # load_user_profiles:
        #         with open(data_manager.DIR_data_workflow / f"user_profile/{self.id}.json", "r") as f:
        #             user_profiles = json.load(f)
        #         self.user_profiles = [UserProfile.load_from_dict(profile) for profile in user_profiles]
        #         # if user in OOW mode!
        #         if "oow" in self.cfg.user_mode.lower():
        #             with open(data_manager.DIR_data_root / f"meta/oow.yaml", "r") as f:
        #                 data = yaml.safe_load(f)
        #             self.user_oow_intentions = [OOWIntention.from_dict(d) for d in data]
        #     if self.cfg.exp_mode == "turn":  # load_reference_conversation:
        #         with open(
        #             data_manager.DIR_data_workflow / f"user_profile_w_conversation/{self.id}.json",
        #             "r",
        #         ) as f:
        #             data = json.load(f)
        #         self.reference_conversations = []
        #         for d in data:
        #             self.reference_conversations.append(
        #                 ConversationWithIntention(
        #                     d["user_intention"],
        #                     Conversation.load_from_json(d["conversation"]),
        #                 )
        #             )
        return self

    def _get_workflow_id(self, id_or_name: str, workflow_infos: dict):
        if id_or_name in workflow_infos:
            return id_or_name
        for id, info in workflow_infos.items():
            if info["name"] == id_or_name:
                return id
        raise ValueError(f"[ERROR] {id_or_name} not found in {workflow_infos.keys()}")

    # def refresh_config(self, cfg: Config) -> "DataHandler":
    #     """used for UI!
    #     TODO: check if is used!
    #     """
    #     print(f"> [workflow] refresh config: {cfg.workflow_dataset, cfg.pdl_version, cfg.workflow_id}")
    #     data_manager = DataManager(cfg)
    #     self.cfg = cfg
    #     self.id = self.cfg.workflow_id
    #     assert self.id in data_manager.workflow_infos, f"[ERROR] {self.id} not found in {data_manager.workflow_infos.keys()}"
    #     with open(data_manager.DIR_data_workflow / f"tools/{self.id}.yaml", "r") as f:
    #         self.toolbox = yaml.safe_load(f)
    #     _dir = data_manager.DIR_data_workflow / self.cfg.pdl_version / f"{self.id}.yaml"
    #     self.pdl = PDL.load_from_file(_dir)
    #     self.workflow = self.pdl.to_str()  # self.pdl.procedure
    #     return self

    # @property
    # def num_user_profile(self):
    #     if self.user_profiles is not None:
    #         return len(self.user_profiles)
    #     if self.reference_conversations is not None:
    #         return len(self.reference_conversations)
    #     raise NotImplementedError

    def to_str(self):
        # return f"ID: {self.type}-{self.id}\nName: {self.name}\nTask: {self.task_description}\nWorkflow: {self.workflow}"
        info_dict = {
            "ID": f"{self.type}-{self.id}",
            "Name": self.name,
            "Task": self.task_description,
            "Workflow": self.task_description,  # just use natural language-format workflow?
        }
        return "".join([f"{k}: {v}\n" for k, v in info_dict.items()])

    # def get_toolbox_by_names(self, names: List[str]):
    #     return [tool for tool in self.toolbox if tool["API"] in names]
