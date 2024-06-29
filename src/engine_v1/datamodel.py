import datetime, os
from enum import Enum, auto
from .common import DIR_log

class Logger:
    log_fn = "tmp.log"
    def __init__(self):
        now = datetime.datetime.now()
        s_day = now.strftime("%Y-%m-%d")
        s_second = now.strftime("%Y-%m-%d_%H-%M-%S")
        s_millisecond = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        log_dir = f"{DIR_log}/{s_day}"
        os.makedirs(log_dir, exist_ok=True)
        log_fn = f"{log_dir}/{s_second}.log"
        self.log_fn = log_fn

    def log(self, message:str, add_line=True, with_print=False):
        with open(self.log_fn, 'a') as f:
            f.write(message + "\n" if add_line else "")
            f.flush()
        if with_print:
            print(message)


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
    msgs = []

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

    def load_from_file(self, file_path):
        with open(file_path, 'r') as f:
            self.PDL_str = f.read()

    def to_str(self):
        return self.PDL_str
