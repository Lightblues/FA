""" 
@240723 SimulatorV2
"""
import datetime, copy
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from engine import PDL, _DIRECTORY_MANAGER
from engine.main import ConversationController
from engine.role_api import LLMSimulatedAPIHandler, V01APIHandler
from engine.role_user import LLMSimulatedUserWithRefConversation
from engine.role_bot import PDLBot
from engine.controller import PDLController
from engine.common import Logger
from engine.datamodel import (
    Conversation, Message, Role, ActionType, ConversationInfos, 
    Config, 
)

class SimulatorV2(ConversationController):
    cfg: Config = None
    client: OpenAIClient = None
    api: V01APIHandler = None
    user: LLMSimulatedUserWithRefConversation = None
    bot: PDLBot = None
    logger: Logger = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.user = LLMSimulatedUserWithRefConversation(cfg=cfg)
        self.bot = PDLBot(cfg=cfg)
        if cfg.api_mode == "llm":
            self.api = LLMSimulatedAPIHandler(cfg=cfg)
        elif cfg.api_mode == "v01":
            self.api = V01APIHandler(cfg=cfg)  # paras: [fn_api_infos]
        else:
            raise ValueError(f"Unknown api_mode: {cfg.api_mode}")
        self.logger = Logger(_DIRECTORY_MANAGER.DIR_simulation_v2_log)

    def simulate(self, pdl:PDL, ref_conversation:Conversation) -> Tuple[Dict, Conversation]:
        """ 
        Q] 相较于 ConversationController.conversation 的差异?
        整体基本没有差异! 只是user从人工输入换成了LLM模拟, 在一些print还有log的地方有细微差异! 
        
        log 逻辑? 
        """
        msg_hello = Message(Role.BOT, f"你好，我是{self.cfg.workflow_name}机器人，有什么可以帮您?")
        self.logger.log_to_stdout(msg_hello.to_str(), color=msg_hello.role.color)
        conversation = Conversation()
        conversation.add_message(msg_hello)
        conversation_infos = ConversationInfos.from_components(             # useful information for bot
            curr_role=Role.BOT, curr_action_type=ActionType.START, num_user_query=0
        )
        # curr_role, curr_action_type = Role.USER, ActionType.START
        action_metas = None
        self.user.load_ref_conversation(ref_conversation=ref_conversation)
        # TODO: add constrains! 
        while conversation_infos.curr_action_type != ActionType.ANSWER:
            next_role = self.next_role(conversation_infos.curr_role, conversation_infos.curr_action_type)
            if next_role == Role.USER:
                action_type, action_metas, msg = self.user.process(conversation=conversation, pdl=pdl)
                conversation_infos.num_user_query += 1
                _debug_msg = f"{'[USER]'.center(50, '=')}\n<<prompt>>\n{action_metas['prompt']}\n\n<<response>>\n{action_metas['llm_response']}\n"
                self.logger.debug(_debug_msg)
            elif next_role == Role.BOT:
                _conversation = copy.deepcopy(conversation)
                for bot_prediction_steps in range(3):      # cfg.bot_prediction_steps_limit
                    action_type, action_metas, msg = self.bot.process(
                        conversation=_conversation, pdl=pdl, conversation_infos=conversation_infos, 
                        print_stream=False          # cfg.bot_print_stream
                    )
                    _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{action_metas['prompt']}\n\n<<response>>\n{action_metas['llm_response']}\n"
                    self.logger.debug(_debug_msg)

                    if action_type == ActionType.API:
                        check_pass, sys_msg_str = self.pdl_controller.check_validation(next_node=action_metas["action_name"])       # next_node
                        self.logger.log_to_stdout(f"  <controller> {msg.content}", color="gray")
                        self.logger.log_to_stdout(f"  <controller> {sys_msg_str}", color="gray")
                        if check_pass: break
                        else:
                            _conversation.add_message(msg)
                            _conversation.add_message(Message(Role.SYSTEM, sys_msg_str))
                    else: break
                else:
                    pass         # TODO: 增加兜底策略
            elif next_role == Role.SYSTEM:
                action_type, action_metas, msg = self.api.process(conversation=conversation, paras=action_metas)
            else:
                raise ValueError(f"Unknown role: {next_role}")
            conversation_infos.curr_role = next_role
            conversation_infos.curr_action_type = action_type
            conversation.add_message(msg)           # add msg universally
            self.logger.log(msg.to_str(), with_print=False)
            if conversation_infos.curr_role not in []: self.logger.log_to_stdout(msg.to_str(), color=conversation_infos.curr_role.color)  # also print user query in simulation mode!

        return conversation
    
    def start_simulation(self, ref_conversation:Conversation) -> Tuple[Dict, Conversation]:
        pdl = PDL.load_from_file(f"{self.cfg.workflow_dir}/{self.cfg.workflow_name}.txt")
        self.pdl_controller = PDLController(pdl=pdl)

        t_now = datetime.datetime.now()
        infos = {
            # "workflow_name": self.cfg.workflow_name,
            # "model_name": self.cfg.model_name,
            # "template_fn": self.cfg.template_fn,
            # "workflow_dir": self.cfg.workflow_dir,
            "log_file": self.logger.log_fn,
            "time": t_now.strftime("%Y-%m-%d %H:%M:%S"),
            "config": self.cfg.to_dict(),
        }
        s_infos = "\n".join([f"{k}: {v}" for k, v in infos.items()]) + "\n"
        infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
        self.logger.log_to_stdout(infos_header, color="gray")

        conversation = self.simulate(pdl=pdl, ref_conversation=ref_conversation)

        infos_end = f" END! ".center(50, "=")
        self.logger.log_to_stdout(infos_end, color="gray")
        return infos, conversation