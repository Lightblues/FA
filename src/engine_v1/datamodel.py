""" 
@240716 新增 BaseUser, BaseAPIHandler, BaseBot 基类

Logger: utility class for logging

PDL: abstract and parse PDL format

Role: roles in conversation, includes: SYSTEM, USER, BOT
Conversation: list of Messages

"""

import datetime, os, re
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from colorama import init, Fore, Style
# 初始化 colorama
init(autoreset=True)
from .common import DIR_log

class BaseLogger:
    def __init__(self):
        pass
    def log(self, *args, **kwargs):
        pass
    def debug(self, *args, **kwargs):
        pass

    def log_to_stdout(self, message:str, color=None):
        if color == 'gray':
            colored_message = f"{Fore.LIGHTBLACK_EX}{message}"
        elif color == 'orange':
            colored_message = f"{Fore.YELLOW}{Style.BRIGHT}{message}"
        else:
            colored_message = message
        print(colored_message)

class Logger(BaseLogger):
    log_dir: str = DIR_log
    log_fn:str = "tmp.log"
    
    def __init__(self, log_dir:str=DIR_log):
        now = datetime.datetime.now()
        s_day = now.strftime("%Y-%m-%d")
        s_second = now.strftime("%Y-%m-%d_%H-%M-%S")
        s_millisecond = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        
        self.log_dir = log_dir
        log_subdir = f"{log_dir}/{s_day}"
        os.makedirs(log_subdir, exist_ok=True)
        self.log_fn = f"{log_subdir}/{s_millisecond}.log"
        log_detail_fn = f"{log_subdir}/{s_millisecond}_detail.log"
        self.log_detail_fn = log_detail_fn

    def log(self, message:str, add_line=True, with_print=False):
        with open(self.log_fn, 'a') as f:
            f.write(message + "\n" if add_line else "")
            f.flush()
        if with_print:
            print(message)
    
    def debug(self, message:str):
        with open(self.log_detail_fn, 'a') as f:
            f.write(f"{message}\n\n")
            f.flush()

class ActionType(Enum):
    START = auto()
    API = auto()
    REQUEST = auto()
    ANSWER = auto()
    USER = auto()
    API_RESPONSE = auto()

    def __str__(self):
        return f"ActionType.{self.name}"

class Role(Enum):
    SYSTEM = (0, "[SYSTEM] ", "system")
    USER = (1, "[USER] ", "user")
    BOT = (2, "[BOT] ", "bot")

    def __init__(self, id, prefix, rolename):
        self.id = id
        self.prefix = prefix
        self.rolename = rolename
    
    def __str__(self):
        return f"Role(id={self.id}, prefix={self.prefix}, name={self.rolename})"

class Message:
    role: Role = None
    text: str = None

    def __init__(self, role: Role, text: str):
        self.role = role
        self.text = text
    
    def to_str(self):
        return f"{self.role.prefix}{self.text}"
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()

class Conversation():
    msgs:List[Message] = []
    
    def __init__(self):
        self.msgs = []

    def add_message(self, msg: Message):
        assert isinstance(msg, Message), f"Must be Message! But got {type(msg)}"
        self.msgs.append(msg)

    @classmethod
    def load_from_json(cls, o:List):
        instance = cls()
        for msg in o:
            if msg["role"] == "SYSTEM":
                _role = Role.SYSTEM
            elif msg["role"] == "USER":
                _role = Role.USER
            elif msg["role"] == "BOT":
                _role = Role.BOT
            else:
                raise ValueError(f"Unknown role: {msg['role']}")
            instance.add_message(Message(_role, msg["content"]))
        return instance

    def to_str(self):
        return "\n".join([msg.to_str() for msg in self.msgs])
    
    def __add__(self, other):
        if type(other) == list:
            assert isinstance(other[0], Message), f"Must be list of Message!"
            self.msgs += other
        elif isinstance(other, Conversation):
            self.msgs += other.msgs
        else:
            raise NotImplementedError
        return self
    
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()


@dataclass
class ConversationInfos:
    previous_action_type: ActionType = None
    num_user_query: int = 0
    
    @classmethod
    def from_components(cls, previous_action_type, num_user_query):
        return cls(previous_action_type, num_user_query)

@dataclass
class ConversationHeaderInfos:
    workflow_name: str = ""
    model_name: str = ""
    start_time: str = ""
    # "template_fn": self.bot.template_fn,
    # "workflow_dir": self.workflow_dir,
    # "log_file": self.logger.log_fn,

    @classmethod
    def from_components(cls, workflow_name, model_name):
        return cls(
            workflow_name, model_name, 
            start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )


class PDL:
    PDL_str: str = None
    
    taskflow_name: str = ""
    taskflow_desc: str = ""
    apis: list = []
    requests: list = []
    answers: list = []
    workflow_str: str = ""      # the core logic of the taskflow

    def load_from_str(self, PDL_str):
        self.PDL_str = PDL_str
        # res = self.parse_PDL_str()        # FIXME: parse error! 
        # if res: print(f"[ERROR] Parsing PDL file {file_path} failed!")
    def load_from_file(self, file_path):
        """ Load and parse the PDL file """
        with open(file_path, 'r') as f:
            PDL_str = f.read().strip()
        self.load_from_str(PDL_str)

    def parse_PDL_str(self):
        spliter = "\n\n"
        splited_parts = self.PDL_str.split(spliter, 4)    # NOTE: parse according to the header of each part
        for p in splited_parts:
            if p.startswith("APIs"):
                self.apis = self._parse_apis(p)
            elif p.startswith("REQUESTs"):
                self.requests = self._parse_apis(p)
            elif p.startswith("ANSWERs"):
                self.answers = self._parse_apis(p)
            elif p.startswith("==="):
                self.taskflow_name, self.taskflow_desc = self._parse_meta(p)
            else:
                if self.workflow_str:
                    print(f"[WARNING] {self.workflow_str} v.s. {p}")
                self.workflow_str = p
    def _parse_apis(self, s:str):
        apis = s.split("\n-")[1:]
        res = []
        for s_api in apis:
            api = {}
            for line in s_api.strip().split("\n"):
                k,v = line.strip().split(":", 1)
                api[k.strip()] = v.strip()
            res.append(api)
        return res
    def _parse_meta(self, s:str):
        """ recognize `TaskFlowName: {}` and `TaskFlowDesc: {}` """
        reg_taskflow = re.compile(r"TaskFlowName: (.+)")
        reg_taskflow_desc = re.compile(r"TaskFlowDesc: (.+)")
        taskflow = reg_taskflow.search(s).group(1)
        taskflow_desc = reg_taskflow_desc.search(s).group(1)
        return taskflow, taskflow_desc

    def to_str(self):
        return self.PDL_str
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()


class BaseUser:
    def generate(self, conversation:Conversation) -> Message:
        """ 根据当前的会话进度, 生成下一轮query """
        raise NotImplementedError

class BaseAPIHandler:
    def process_query(self, conversation:Conversation, api_name: str, api_params: Dict) -> str:
        """ 给定上下文和当前的API请求, 返回API的响应 
        NOTE: API do NOT modify the conversation!!!
        """
        raise NotImplementedError

class BaseBot:
    api_handler: BaseAPIHandler = None      # 用于处理API请求
    
    def __init__(self, api_handler: BaseAPIHandler) -> None:
        self.api_handler = api_handler
    def process(self, conversation:Conversation) -> str:
        """ 处理当前轮query """
        raise NotImplementedError

class InputUser(BaseUser):
    def generate(self, conversation:Conversation) -> Message:
        user_input = input("[USER] ")
        msg = Message(Role.USER, user_input)
        conversation.add_message(msg)
        return msg