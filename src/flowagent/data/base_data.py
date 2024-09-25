# from engine import Role, Message, Conversation
import datetime, os, re, yaml, copy, pathlib, time
from enum import Enum, auto
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
import pandas as pd


class Role(Enum):
    SYSTEM = (0, "[SYSTEM] ", "system", 'green')
    USER = (1, "[USER] ", "user", "red")
    BOT = (2, "[BOT] ", "bot", "orange")

    def __init__(self, id, prefix, rolename, color):
        self.id = id
        self.prefix = prefix
        self.rolename = rolename
        self.color = color
    
    def __str__(self):
        return f"Role(id={self.id}, prefix={self.prefix}, name={self.rolename})"

    @classmethod
    def get_by_rolename(cls, rolename: str):
        for member in cls:
            if member.rolename == rolename.lower():
                return member
        raise KeyError(f"{rolename} is not a valid key for {cls.__name__}")


@dataclass
class APICall:
    name: str
    params: Dict
    
    @classmethod
    def from_dict(cls, d:Dict):
        data = {
            "name": d["API"],
            "params": { i['name']: i['value'] for i in d["params"] }
        }
        return cls(**data)


@dataclass
class Message:
    role: Role = None
    content: str = None
    prompt: str = None
    llm_response: str = None
    conversation_id: str = None
    utterance_id: int = None
    
    type: str = None
    apis: List[APICall] = None      # whether contain api calls
    
    content_predict: str = None

    def __init__(
        self, role: Role, content: str, 
        conversation_id: str=None, utterance_id: int=None, 
        prompt: str=None, llm_response: str=None, 
        type: str=None, apis: List[APICall]=None,
        **kwargs
    ):
        self.role = role
        self.content = content
        if prompt is not None: self.prompt = prompt
        if llm_response is not None: self.llm_response = llm_response
        if conversation_id is not None: self.conversation_id = conversation_id
        if utterance_id is not None: self.utterance_id = utterance_id
        if type is not None: self.type = type
        if apis: 
            if not isinstance(apis[0], APICall):
                apis = [APICall.from_dict(i) for i in apis]
            self.apis = apis
    
    def to_str(self):
        return f"{self.role.prefix}{self.content}"
    def to_dict(self):
        res = asdict(self)
        res["role"] = self.role.rolename
        return res
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()
    
    def copy(self):
        return copy.deepcopy(self)
    
    # auto determined api v.s. GT api calls (.apis, .type)
    def is_api_calling(self) -> bool:
        return self.role == Role.BOT and self.content.startswith("<Call API>")
    def get_api_infos(self) -> Tuple[str, str]:
        """ 
        return: action_name, action_parameters
        """
        # content = f"<Call API> {action_name}({action_parameters})"
        assert self.is_api_calling(), f"Must be API calling message! But got {self}"
        content = self.content[len("<Call API> "):].strip()
        re_pattern = r"(.*)\((.*)\)"
        re_match = re.match(re_pattern, content)
        return re_match.group(1), re_match.group(2)
    
    def substitue_with_GT_content(self, GT_content: str):
        self.content, self.content_predict = GT_content, self.content


class Conversation():
    msgs: List[Message] = []
    conversation_id: str = None
    
    def __init__(self, conversation_id: str = None):
        self.msgs = []
        if not conversation_id:
            conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.conversation_id = conversation_id

    def add_message(self, msg: Message):
        # assert isinstance(msg, Message), f"Must be Message! But got {type(msg)}"
        self.msgs.append(msg)
            
    def get_message_by_idx(self, idx: int) -> Message:
        return self.msgs[idx]
    
    def get_messages_num(self) -> int:
        return len(self.msgs)
    @property
    def current_utterance_id(self) -> int:
        return len(self.msgs)
    
    @property
    def messages(self) -> List[Message]:
        return self.msgs
    
    def get_last_message(self) -> Message:
        return self.msgs[-1]
    
    def get_called_apis(self) -> List[str]:
        """ collect all API calls in the conversation by BOT """
        apis = []
        for msg in self.msgs:
            if msg.is_api_calling():
                apis.append(msg.get_api_infos()[0])
        return apis

    @classmethod
    def from_messages(cls, msgs: List[Message]):
        assert len(msgs) > 0, f"Must have at least one message!"
        conv_id = msgs[0].conversation_id
        instance = cls(conv_id)
        instance.msgs = msgs
        return instance
    
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([m.to_dict() for m in self.msgs])

    @classmethod
    def load_from_json(cls, o:List[Dict]):
        instance = cls()
        for msg in o:
            _role = Role.get_by_rolename(msg["role"])
            instance.add_message(Message(
                _role, msg["content"], 
                type=msg.get("type", None), apis=msg.get("apis", None)
            ))
        return instance
    
    @classmethod
    def load_from_str(cls, s: str):
        ins = cls()
        for line in s.split("\n"):
            if not line.strip(): continue
            if line.startswith("[BOT]"):
                ins.add_message(Message(Role.BOT, line[len("[BOT]")+1:]))
            elif line.startswith("[USER]"):
                ins.add_message(Message(Role.USER, line[len("[USER]")+1:]))
            elif line.startswith("[SYSTEM]"):
                ins.add_message(Message(Role.SYSTEM, line[len("[SYSTEM]")+1:]))
            else:
                # append the last message
                ins.msgs[-1].content += f"\n{line}"
        return ins

    def to_str(self):
        return "\n".join([msg.to_str() for msg in self.msgs])
    def to_list(self):
        return [msg.to_dict() for msg in self.msgs]
    
    def copy(self):
        return copy.deepcopy(self)
    
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
    def __len__(self):
        return len(self.msgs)


class ConversationWithIntention():
    def __init__(self, user_intention: str, conversation: Conversation) -> None:
        self.user_intention = user_intention
        self.conversation = conversation
        
    def __str__(self):
        return f"simulated conversation with {len(self.conversation)} messages.\nUser intention: {self.user_intention}"

