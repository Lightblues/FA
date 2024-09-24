from ..controller import BOT_TYPE2CONTROLLER, BaseController
from ..data import Config
from .judger import Judger


def task_simulate(cfg: Config) -> None:
    """ One simulation task
    """
    controller: BaseController = BOT_TYPE2CONTROLLER[cfg.bot_mode](cfg)
    controller.start_conversation(verbose=False)
    
def task_judge(cfg: Config) -> None:
    """ One evaluation task
    return: True if pass
    """
    judger = Judger(cfg)
    judger.start_judge(verbose=False)
