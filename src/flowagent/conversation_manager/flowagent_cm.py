""" updated @240919
"""
from typing import List
from ..data import (
    Config, Workflow, 
    BotOutput, UserOutput, BotOutputType, APIOutput,
    Role, Message, Conversation
)
from ..roles import (
    USER_NAME2CLASS, BOT_NAME2CLASS, API_NAME2CLASS, PDLBot
)
from .base_cm import BaseConversationManager
from utils.wrappers import Timer
from ..pdl_controllers import NodeDependencyController, APIDuplicationController, CONTROLLER_NAME2CLASS, BaseController


class FlowagentConversationManager(BaseConversationManager):
    """ main loop of a simulated conversation
    USAGE:
        controller = FlowagentController(cfg)
        controller.start_conversation()
    """
    def __init__(self, cfg:Config) -> None:
        super().__init__(cfg)
        self.workflow = Workflow(cfg)
        self.bot = BOT_NAME2CLASS[cfg.bot_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        
        if self.cfg.exp_mode == "session":
            self.user = USER_NAME2CLASS[cfg.user_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
            self.api = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
            if isinstance(self.bot, PDLBot):    # for PDLBot, build the controllers
                self.controllers: List[BaseController] = []
                for c in self.cfg.bot_pdl_controllers:
                    controller = CONTROLLER_NAME2CLASS[c['name']](cfg, self.conv, self.workflow.pdl, c['config'])
                    self.controllers.append(controller)
        
    def conversation(self, verbose:bool=True) -> Conversation:
        """ given three roles (system/user/bot), start a conversation
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
                bot_output: BotOutput = None
                while True:         # limit the bot prediction steps
                    # 0. pre-control
                    self._pre_control(bot_output)
                    # 1. bot predict an action
                    with Timer("bot process", print=self.cfg.log_utterence_time):
                        bot_output: BotOutput = self.bot.process()
                    self.log_msg(self.conv.get_last_message(), verbose=verbose)
                    # 2. STOP: break until bot RESPONSE
                    if bot_output.action_type == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_type == BotOutputType.ACTION:
                        # 3. ACTION loop: call the API, append results to conversation
                        # 3.1. post-check the action! (will be ignored for non-PDLBot)
                        if not self._post_check(bot_output):
                            self.log_msg(self.conv.get_last_message(), verbose=verbose)  # log the error info!
                            continue
                        # 3.2 call the API (system)
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
    
    def _post_check(self, bot_output: BotOutput) -> bool:
        """ Check the validation of bot's action
        NOTE: if not validated, the error infomation will be added to self.conv!
        """
        if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return True
        for controller in self.controllers:
            if not controller.if_post_check: continue
            if not controller.post_check(bot_output): return False
        return True
    
    def _pre_control(self, bot_output: BotOutput) -> None:
        """ Make pre-control on the bot
        will change the PDLBot's prompt! 
        """
        if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return
        for controller in self.controllers:
            if not controller.if_pre_check: continue
            controller.pre_control(bot_output)

    def conversation_teacher_forcing(self, verbose:bool=True) -> Conversation:
        """ given a reference conversation, test the bot in a teacher-forcing manner
        """
        ref_conv = self.workflow.reference_conversations[self.cfg.user_profile_id].conversation
        for msg in ref_conv.msgs:
            if msg.role != Role.BOT:
                self.conv.add_message(msg.copy())
            else:
                # 1. bot predict an action (NOTE: will add a msg in self.conv)
                with Timer("bot process", print=self.cfg.log_utterence_time):
                    bot_output: BotOutput = self.bot.process()
                # 2. convert the msg! 
                self.conv.substitue_message(msg.copy(), old_to_prediction=True, idx=-1)
                self.logger.log(f"<teacher_forcing> gt: {self.conv.get_last_message().content}\n  predicted: {self.conv.get_last_message().content_predict}", with_print=verbose)
        return self.conv
