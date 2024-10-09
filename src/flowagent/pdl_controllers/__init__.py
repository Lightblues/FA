from typing import Dict
from .base_controller import BaseController
from .dep_controller import NodeDependencyController
from .api_controller import APIDuplicationController

def build_attr_map(base_class: BaseController, name_to_class_dict: Dict[str, BaseController], attr: str="name"):
    for cls in base_class.__subclasses__():
        name_to_class_dict[cls.__dict__[attr]] = cls
        build_attr_map(cls, name_to_class_dict, attr)
CONTROLLER_NAME2CLASS = {}
build_attr_map(BaseController, CONTROLLER_NAME2CLASS, attr="name")

