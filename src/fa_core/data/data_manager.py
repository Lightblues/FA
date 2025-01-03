"""
- [x] #fix remove Config from DataManager
"""

import json
import os
import yaml
from functools import cache
from pydantic import BaseModel, Field
from typing import Dict, Optional, ClassVar, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from fa_core.data.workflow import FAWorkflow


class PathConfig(BaseModel):
    # Base directories
    DIR_root: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent.parent
    DIR_src_base: ClassVar[Path] = DIR_root / "src"

    # Configuration and template directories
    DIR_config: ClassVar[Path] = DIR_root / "src/configs"
    DIR_template: ClassVar[Path] = DIR_root / "src/templates/flowagent"

    # Log directories
    DIR_log: ClassVar[Path] = DIR_root / "log"
    DIR_wandb: ClassVar[Path] = DIR_log / "_wandb"
    DIR_ui_log: ClassVar[Path] = DIR_log / "ui"
    DIR_backend_log: ClassVar[Path] = DIR_log / "backend"

    # Data directory
    DIR_data_root: ClassVar[Path] = DIR_root / "dataset"
    DIR_data_eval_fixed_queries: ClassVar[Path] = DIR_data_root / "eval_fixed_queries"

    model_config = {
        "arbitrary_types_allowed": True  # Allow Path type
    }


class FADataManager(PathConfig):
    @classmethod
    @cache
    def get_workflow_infos(cls, workflow_dataset: str) -> dict:
        """Get the workflow infos map"""
        fn = cls.DIR_data_root / workflow_dataset / "task_infos.json"
        return json.load(open(fn, "r"))["task_infos"]

    @classmethod
    @cache
    def get_workflow(cls, workflow_dataset: str, workflow_id: str) -> "FAWorkflow":
        return FAWorkflow(workflow_dataset=workflow_dataset, workflow_id=workflow_id)

    @classmethod
    def unify_workflow_name(cls, workflow_dataset: str, workflow_name_or_id: str) -> str:
        workflow_infos = cls.get_workflow_infos(workflow_dataset)
        workflow_name_id_map = {info["name"]: id for id, info in workflow_infos.items()}
        if workflow_name_or_id in workflow_name_id_map:
            workflow_name_or_id = workflow_name_id_map[workflow_name_or_id]
        else:
            assert workflow_name_or_id in workflow_infos, f"[ERROR] {workflow_name_or_id} not found in {workflow_infos.keys()}"
        return workflow_name_or_id

    @classmethod
    def unify_workflow_id(cls, workflow_dataset: str, workflow_id_or_name: str) -> str:
        workflow_infos = cls.get_workflow_infos(workflow_dataset)
        workflow_id_name_map = {id: info["name"] for id, info in workflow_infos.items()}
        if workflow_id_or_name in workflow_id_name_map:
            workflow_id_or_name = workflow_id_name_map[workflow_id_or_name]
        else:
            assert workflow_id_or_name in workflow_infos, f"[ERROR] {workflow_id_or_name} not found in {workflow_infos.keys()}"
        return workflow_id_or_name

    # --------------------- for ui ---------------------
    @classmethod
    def get_template_name_list(cls, prefix: str = "bot_"):
        fns = [fn for fn in os.listdir(cls.DIR_template) if fn.startswith(prefix)]
        return sorted(fns)

    @classmethod
    @cache
    def get_workflow_names_map(cls):
        """
        TODO: add `dataset_infos.json` to register dataset unifiedly
        Return:
            names_map: {PDL_zh: ["task1", "task2"]}
            name_id_map: {PDL_zh: {"task1": "000"}}
        """
        dataset_infos = yaml.load(open(cls.DIR_data_root / "dataset_infos.yaml", "r"), Loader=yaml.FullLoader)
        names_map = {}  # {PDL_zh: ["task1", "task2"]}
        name_id_map = {}  # {PDL_zh: {"task1": "000"}}
        for dir in dataset_infos.keys():
            fn = cls.DIR_data_root / dir / "task_infos.json"
            if not os.path.exists(fn):
                continue
            infos = json.load(open(fn, "r"))
            names_map[dir] = [task_info["name"] for task_info in infos["task_infos"].values()]
            name_id_map[dir] = {task_info["name"]: key for key, task_info in infos["task_infos"].items()}
        return names_map, name_id_map
