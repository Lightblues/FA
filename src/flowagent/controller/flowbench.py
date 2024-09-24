""" updated @240919
"""

from ..data import (
    Config, Workflow, 
    BotOutput, UserOutput, BotOutputType, APIOutput,
    Role, Message, Conversation
)
from ..roles import (
    USER_NAME2CLASS, BOT_NAME2CLASS, API_NAME2CLASS, 
)
from .base import BaseController
from utils.wrappers import Timer

class FlowbenchController(BaseController):
    """ main loop of a simulated conversation
    USAGE:
        controller = FlowbenchController(cfg)
        controller.start_conversation()
    """
    bot_types = ["ReactBot", "react_bot"]
    
    def __init__(self, cfg:Config) -> None:
        super().__init__(cfg)
        self.workflow = Workflow.load_by_id(
            data_manager=self.data_namager,
            id=cfg.workflow_id, type=cfg.workflow_type,
            load_user_profiles=cfg.user_profile
        )
        self.user = USER_NAME2CLASS[cfg.user_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        self.bot = BOT_NAME2CLASS[cfg.bot_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        self.api = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
    
    def conversation(self, verbose:bool=True) -> Conversation:
        """ 
        1. initiation: initialize the variables, logger, etc.
        2. main loop
            stop: by user (or bot?) -- only user!
            controller: 
                > bot can take several actions in one turn? 
        """
        role: Role = Role.USER      # current role!
        
        num_UB_turns:int = 0           # cnt of user & bot conversation
        # num_utterance:int = 0       # cnt of u/b/s utterance (conversation length)
        while True:
            if role == Role.USER:
                with Timer("user process", print=self.cfg.log_utterence_time):
                    user_output: UserOutput = self.user.process()
                self.log_msg(self.conv.get_last_message(), verbose=verbose)
                role = Role.BOT
                if user_output.is_end:
                    self.logger.log(f"  <main> ended by user!", with_print=verbose)
                    break
            elif role == Role.BOT:
                num_bot_actions = 0
                while True:         # limit the bot prediction steps
                    with Timer("bot process", print=self.cfg.log_utterence_time):
                        bot_output: BotOutput = self.bot.process()
                    self.log_msg(self.conv.get_last_message(), verbose=verbose)
                    if bot_output.action_type == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_type == BotOutputType.ACTION:
                        # call the API, append results to conversation
                        with Timer("api process", print=self.cfg.log_utterence_time):
                            api_output: APIOutput = self.api.process(bot_output)
                        self.log_msg(self.conv.get_last_message(), verbose=verbose)
                    else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
                    
                    num_bot_actions += 1
                    if num_bot_actions > self.cfg.bot_action_limit: 
                        # ... the default response
                        self.logger.log(f"  <main> bot retried actions reach limit!", with_print=verbose)
                        break
                role = Role.USER
            num_UB_turns += 1
            if num_UB_turns > self.cfg.conversation_turn_limit: 
                self.logger.log("  <main> end due to conversation turn limit!", with_print=verbose)
                break
        
        return self.conv
