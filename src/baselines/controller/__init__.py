from .base import BaseController
from .flowbench import FlowbenchController
from .pdl import PDLController

WORKFLOW_TYPE2CONTROLLER = {}
for cls in BaseController.__subclasses__():
    for name in cls.workflow_types:
        WORKFLOW_TYPE2CONTROLLER[name] = cls
        WORKFLOW_TYPE2CONTROLLER[name.upper()] = cls