"""
- [x] #fix remove Config from DataManager
"""

import json
import os
from pydantic import BaseModel, Field
from typing import Dict, Optional, ClassVar, TYPE_CHECKING
from pathlib import Path


class FADataManager(BaseModel):
    workflow_dataset: str

    # NOTE: Use ClassVar to define class-level constants
    DIR_root: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent.parent
    DIR_src_base: ClassVar[Path] = DIR_root / "src"
    DIR_config: ClassVar[Path] = DIR_root / "src/configs"
    DIR_template: ClassVar[Path] = DIR_root / "src/templates/flowagent"
    DIR_wandb: ClassVar[Path] = DIR_root / "log/_wandb"
    DIR_ui_log: ClassVar[Path] = DIR_root / "log/ui"
    DIR_backend_log: ClassVar[Path] = DIR_root / "log/backend"
    DIR_data_root: ClassVar[Path] = DIR_root / "dataset"

    # Instance variables
    DIR_data_workflow: Optional[Path] = None
    FN_data_workflow_infos: Optional[Path] = None
    data_version: Optional[str] = None
    workflow_infos: Dict = Field(default_factory=dict)

    model_config = {
        "arbitrary_types_allowed": True  # Allow Path type
    }

    def model_post_init(self, __context) -> None:
        workflow_dataset = self.workflow_dataset

        self.DIR_data_workflow = self.DIR_data_root / workflow_dataset
        self.FN_data_workflow_infos = self.DIR_data_workflow / "task_infos.json"
        _infos: dict = json.load(open(self.FN_data_workflow_infos, "r"))
        self.data_version = _infos["version"]
        self.workflow_infos = _infos["task_infos"]

    @property
    def num_workflows(self) -> int:
        return len(self.workflow_infos)

    def get_workflow_dataset_names(self):
        # return folder name in self.DIR_data_root
        all_entries = os.listdir(self.DIR_data_root)
        names = [entry for entry in all_entries if os.path.isdir(os.path.join(self.DIR_data_root, entry))]
        return names

    # --------------------- for ui ---------------------
    @staticmethod
    def get_template_name_list(prefix: str = "bot_"):
        fns = [fn for fn in os.listdir(FADataManager.DIR_template) if fn.startswith(prefix)]
        return sorted(fns)

    @staticmethod
    def get_workflow_dirs():
        dirs = [entry for entry in os.listdir(FADataManager.DIR_data_root) if os.path.isdir(os.path.join(FADataManager.DIR_data_root, entry))]
        return dirs

    @staticmethod
    def get_workflow_versions(workflow_dataset):
        _dir = FADataManager.DIR_data_root / workflow_dataset
        dirs = [d for d in os.listdir(_dir) if d.startswith("pdl") and os.path.isdir(os.path.join(_dir, d))]
        return dirs

    @staticmethod
    def get_workflow_names_map():
        """
        Return:
            names_map: {PDL_zh: ["task1", "task2"]}
            name_id_map: {PDL_zh: {"task1": "000"}}
        """
        dirs = FADataManager.get_workflow_dirs()
        names_map = {}  # {PDL_zh: ["task1", "task2"]}
        name_id_map = {}  # {PDL_zh: {"task1": "000"}}
        for dir in dirs:
            fn = FADataManager.DIR_data_root / dir / "task_infos.json"
            if not os.path.exists(fn):
                continue
            infos = json.load(open(fn, "r"))
            names_map[dir] = [task_info["name"] for task_info in infos["task_infos"].values()]
            name_id_map[dir] = {task_info["name"]: key for key, task_info in infos["task_infos"].items()}
        return names_map, name_id_map
