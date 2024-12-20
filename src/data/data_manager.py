import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from common import Config


@dataclass
class DataManager:
    cfg: Config = None

    DIR_root = Path(__file__).resolve().parent.parent.parent
    DIR_src_base = DIR_root / "src"

    DIR_config = DIR_root / "src/flowagent/configs"
    DIR_template = DIR_root / "src/common/templates/flowagent"
    DIR_wandb = DIR_root / "_wandb"
    DIR_ui_log = DIR_root / "log/ui"
    DIR_backend_log = DIR_root / "log/backend"

    DIR_data_root = DIR_root / "dataset"

    DIR_data_workflow = None  # subdir for specific dataset
    FN_data_workflow_infos = None

    data_version: str = None
    workflow_infos: dict = field(default_factory=dict)

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._build_workflow_infos(cfg.workflow_dataset)

    def _build_workflow_infos(self, workflow_dataset: str):
        """Load workflow infors from `task_infos.json`

        Args:
            workflow_dataset (str): dataset name
        """
        self.DIR_data_workflow = self.DIR_data_root / workflow_dataset
        self.FN_data_workflow_infos = self.DIR_data_workflow / "task_infos.json"
        infos: dict = json.load(open(self.FN_data_workflow_infos, "r"))
        self.workflow_dataset = workflow_dataset
        self.data_version = infos["version"]
        self.workflow_infos = infos["task_infos"]

    def refresh_config(self, cfg: Config) -> None:
        self.cfg = cfg
        self._build_workflow_infos(cfg.workflow_dataset)

    @property
    def num_workflows(self):
        return len(self.workflow_infos)

    def get_workflow_dataset_names(self):
        # return folder name in self.DIR_data_root
        all_entries = os.listdir(self.DIR_data_root)
        names = [entry for entry in all_entries if os.path.isdir(os.path.join(self.DIR_data_root, entry))]
        return names

    # --------------------- for ui ---------------------
    @staticmethod
    def get_template_name_list(prefix: str = "bot_"):
        fns = [fn for fn in os.listdir(DataManager.DIR_template) if fn.startswith(prefix)]
        return sorted(fns)

    @staticmethod
    def get_workflow_dirs():
        dirs = [entry for entry in os.listdir(DataManager.DIR_data_root) if os.path.isdir(os.path.join(DataManager.DIR_data_root, entry))]
        return dirs

    @staticmethod
    def get_workflow_versions(workflow_dataset):
        _dir = DataManager.DIR_data_root / workflow_dataset  # cfg.workflow_dataset | "PDL_zh"
        dirs = [d for d in os.listdir(_dir) if d.startswith("pdl") and os.path.isdir(os.path.join(_dir, d))]
        return dirs

    @staticmethod
    def get_workflow_names_map():
        """
        Return:
            names_map: {PDL_zh: ["task1", "task2"]}
            name_id_map: {PDL_zh: {"task1": "000"}}
        """
        dirs = DataManager.get_workflow_dirs()
        names_map = {}  # {PDL_zh: ["task1", "task2"]}
        name_id_map = {}  # {PDL_zh: {"task1": "000"}}
        for dir in dirs:
            fn = DataManager.DIR_data_root / dir / "task_infos.json"
            if not os.path.exists(fn):
                continue
            infos = json.load(open(fn, "r"))
            names_map[dir] = [task_info["name"] for task_info in infos["task_infos"].values()]
            name_id_map[dir] = {task_info["name"]: key for key, task_info in infos["task_infos"].items()}
        return names_map, name_id_map
