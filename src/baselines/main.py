""" 
-----------------------------------------------------------------------
Conversation:
    .add_message(msg)
    .to_str()
"""

from .common import (
    Config, Workflow, BaseRole, BaseBot, BaseUser, BaseAPIHandler, 
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from engine import (
    Role, Message, Conversation, ActionType, ConversationInfos, Logger
)

class BaselineController:
    cfg: Config = None
    user: BaseUser = None
    bot: BaseBot = None
    api: BaseAPIHandler = None
    logger: Logger = None
    def __init__(self, cfg:Config) -> None:
        pass

    def conversation(self, workflow: Workflow):
        """ 
        1. initiation: initialize the variables, logger, etc.
        2. main loop
            stop: by user (or bot?) -- only user!
            controller: 
                > bot can take several actions in one turn? 
        """
        conversation = Conversation()
        # ...init, log meta infos
        role: BaseRole = Role.USER      # current role!
        
        num_turns = 0
        while True:
            if role == Role.USER:
                user_output: UserOutput = self.user.process(conversation)
                # ...infos, log
                role = Role.BOT
            elif role == Role.BOT:
                num_bot_actions = 0
                while True:         # limit the bot prediction steps
                    bot_output: BotOutput = self.bot.process(conversation, ...)
                    if bot_output.action_input == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_input == BotOutputType.ACTION:
                        # ... call the API, append results to conversation
                        api_output: APIOutput = self.api.process(bot_output.action, bot_output.action_input)
                    
                    num_bot_actions += 1
                    if num_bot_actions > self.cfg.bot_action_limit: 
                        # ... the default response
                        role = Role.USER
                        break
            num_turns += 1
            if num_turns > self.cfg.bot_action_limit: break
        
        return conversation


