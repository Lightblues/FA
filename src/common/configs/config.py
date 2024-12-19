"""Config class for FlowAgent @241219
@241219
- [x] #feat implement YAML loader
"""

import copy
from pathlib import Path

from pydantic import BaseModel

from .mixins.config_v010 import V010Mixin
from .yaml_loader import YAMLLoader


_CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"


class ConfigBase(BaseModel):
    version: str = "0.0.1"

    @classmethod
    def from_yaml(cls, yaml_file: str | Path):
        yaml_file = cls._get_full_path(yaml_file)
        data = YAMLLoader.load_yaml(yaml_file)
        return cls(**data)

    def to_yaml(self, yaml_file: str | Path):
        yaml_file = self._get_full_path(yaml_file)
        data = self.model_dump()
        YAMLLoader.save_yaml(data, yaml_file)

    @staticmethod
    def _get_full_path(yaml_file: str | Path):
        """If yaml_file is a relative path, it will be converted to an absolute path"""
        if isinstance(yaml_file, str):
            yaml_file = Path(yaml_file)
        if not yaml_file.is_absolute():
            yaml_file = _CONFIG_DIR / yaml_file
        return yaml_file

    def copy(self):
        return copy.deepcopy(self)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"Key '{key}' not found in Config")


class Config(ConfigBase, V010Mixin):
    """
    Usage::

        from common.configs import Config

        cfg = Config.from_yaml("default.yaml")
    """

    pass
