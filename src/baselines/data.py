from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Union


@dataclass
class DataManager:
    DIR_root = Path(__file__).resolve().parent.parent.parent
    DIR_data_base = (DIR_root / "dataset/v240830")
    DIR_src_base = (DIR_root / "src")
    
    DIR_engine_config = DIR_root / "src/baselines/configs"

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