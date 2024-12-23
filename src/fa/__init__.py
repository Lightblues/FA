from typing import Dict

from .envs import Context

from .bots import BaseBot, ReactBot, UIMultiMainBot, UIMultiWorkflowBot, UISingleBot, UISingleFCBot
from .controllers import APIDuplicationController, BaseController, NodeDependencyController, SessionLengthController
from .tools import BaseTool, RequestTool
from .users import BaseUser, InputUser


BaseRole = BaseUser | BaseBot | BaseTool | BaseController


def build_attr_list_map(base_class: BaseRole, name_to_class_dict: Dict[str, BaseRole], attr: str = "names"):
    for cls in base_class.__subclasses__():
        # print(f"> building {base_class.__name__} -> {cls.__name__} ({type(cls)})...")
        for name in getattr(cls, attr):
            name_to_class_dict[name] = cls
        # recursive!
        build_attr_list_map(cls, name_to_class_dict)


USER_NAME2CLASS: Dict[str, BaseUser] = {}
build_attr_list_map(BaseUser, USER_NAME2CLASS, attr="names")
BOT_NAME2CLASS: Dict[str, BaseBot] = {}
build_attr_list_map(BaseBot, BOT_NAME2CLASS, attr="names")
TOOL_NAME2CLASS: Dict[str, BaseTool] = {}
build_attr_list_map(BaseTool, TOOL_NAME2CLASS, attr="names")

CONTROLLER_NAME2CLASS: Dict[str, BaseController] = {}
build_attr_list_map(BaseController, CONTROLLER_NAME2CLASS, attr="names")
