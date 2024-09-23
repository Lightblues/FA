from ..controller import FlowbenchController
from ..data import Config
from .judger import Judger


def task_simulate(cfg: Config) -> None:
    """ One simulation task
    """
    controller = FlowbenchController(cfg)
    controller.start_conversation(verbose=False)
    
def task_judge(cfg: Config) -> None:
    """ One evaluation task
    return: True if pass
    """
    judger = Judger(cfg)
    judger.start_judge(verbose=False)
