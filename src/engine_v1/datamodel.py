""" 
Logger: utility class for logging

PDL: abstract and parse PDL format

Role: roles in conversation, includes: SYSTEM, USER, BOT
Conversation: list of Messages

"""

import datetime, os, re
from enum import Enum, auto
from typing import List, Dict, Optional
from .common import DIR_log

class Logger:
    log_fn = "tmp.log"
    def __init__(self):
        now = datetime.datetime.now()
        s_day = now.strftime("%Y-%m-%d")
        s_second = now.strftime("%Y-%m-%d_%H-%M-%S")
        # s_millisecond = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        
        log_dir = f"{DIR_log}/{s_day}"
        os.makedirs(log_dir, exist_ok=True)
        log_fn = f"{log_dir}/{s_second}.log"
        self.log_fn = log_fn
        log_detail_fn = f"{log_dir}/{s_second}_detail.log"
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


class Role(Enum):
    SYSTEM = (0, "[SYSTEM] ")
    USER = (1, "[USER] ")
    BOT = (2, "[BOT] ")

    def __init__(self, id, prefix):
        self.id = id
        self.prefix = prefix
    
    def __str__(self):
        return f"Role(id={self.id}, prefix={self.prefix})"

class Message:
    role: Role = None
    text: str = None

    def __init__(self, role: Role, text: str):
        self.role = role
        self.text = text

    def to_str(self):
        return f"{self.role.prefix}{self.text}"

class Conversation():
    msgs:List[Message] = []

    # def add_message(self, role: Role, message: str):
    #     self.msgs.append(Message(role, message))
    def add_message(self, msg: Message):
        self.msgs.append(msg)

    def to_str(self):
        return "\n".join([msg.to_str() for msg in self.msgs])
    
    # reload the "+" op
    def __add__(self, other):
        if type(other) == list:
            assert isinstance(other[0], Message), f"Must be list of Message!"
            self.msgs += other
        elif isinstance(other, Conversation):
            self.msgs += other.msgs
        else:
            raise NotImplementedError
        return self


class PDL:
    PDL_str: str = None
    
    taskflow_name: str = ""
    taskflow_desc: str = ""
    apis: list = []
    requests: list = []
    answers: list = []
    workflow_str: str = ""      # the core logic of the taskflow

    def load_from_file(self, file_path):
        """ Load and parse the PDL file """
        with open(file_path, 'r') as f:
            self.PDL_str = f.read().strip()
        res = self.parse_PDL_str()
        if res: print(f"[ERROR] Parsing PDL file {file_path} failed!")

    def parse_PDL_str(self):
        try:
            spliter = "\n\n"
            apis, requests, answers, meta, workflow = self.PDL_str.split(spliter, 4)    # TODO: parse according to the header of each part
            self.apis = self._parse_apis(apis)
            self.requests = self._parse_apis(requests)
            self.answers = self._parse_apis(answers)
            self.taskflow_name, self.taskflow_desc = self._parse_meta(meta)
            self.workflow_str = workflow
        except Exception as e:
            print(f"[ERROR] Parsing PDL str Error: {e}")
            return -1
        return 0
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
