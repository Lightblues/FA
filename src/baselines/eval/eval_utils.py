from ..main import BaselineController
from ..data.config import Config
from .judger import Judger


def task_simulate(cfg: Config) -> None:
    """ One simulation task
    """
    controller = BaselineController(cfg)
    controller.start_conversation(verbose=False)
    
def task_judge(cfg: Config) -> None:
    """ One evaluation task
    return: True if pass
    """
    judger = Judger(cfg)
    judger.start_judge(verbose=False)
