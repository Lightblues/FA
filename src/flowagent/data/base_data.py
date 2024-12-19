# from engine import Role, Message, Conversation
import copy
import datetime
import re
from typing import Dict, Iterator, List, Optional, Tuple, Union

import pandas as pd
from pydantic import BaseModel, Field


class CustomRole(BaseModel):
    id: int = -1  # use negative id to distinguish built-in roles
    rolename: str
    prefix: str = Field(default="")
    color: str = Field(default="blue")

    def model_post_init(self, __context):
        if not self.prefix:  # set prefix only when it is empty
            self.prefix = f"[{self.rolename.upper()}] "
        self.rolename = self.rolename.lower()

    def __str__(self):
        return f"Role(id={self.id}, prefix={self.prefix}, name={self.rolename})"


class Role:
    """
    NOTE:
    - to use requests/pydantic, do not set Role as Enum
    """

    SYSTEM = CustomRole(id=0, rolename="system", prefix="[SYSTEM] ", color="green")
    USER = CustomRole(id=1, rolename="user", prefix="[USER] ", color="red")
    BOT = CustomRole(id=2, rolename="bot", prefix="[BOT] ", color="orange")

    @classmethod
    def get_by_rolename(cls, rolename: str) -> CustomRole:
        rolename = rolename.upper()
        if hasattr(cls, rolename):
            return getattr(cls, rolename)
        return CustomRole(rolename=rolename)


class APICall(BaseModel):
    name: str
    params: Dict

    @classmethod
    def from_dict(cls, d: Dict):
        if "name" not in d:
            data = {
                "name": d.get("API"),
                "params": {i["name"]: i["value"] for i in d["params"]},
            }
        else:
            data = d
        return cls(**data)


class Message(BaseModel):
    role: Union[str, CustomRole] = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")
    llm_name: Optional[str] = Field(None, description="Name of the language model")
    llm_prompt: Optional[str] = Field(None, description="Optional prompt associated with the message")
    llm_response: Optional[str] = Field(None, description="Response from the language model")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")
    utterance_id: Optional[int] = Field(None, description="ID of the utterance")
    type: Optional[str] = Field(None, description="Type of the message")
    apis: Optional[List[APICall]] = Field(None, description="List of API calls associated with the message")
    content_predict: Optional[str] = Field(None, description="Predicted content of the message")

    def model_post_init(self, __context):
        if isinstance(self.role, str):
            self.role = Role.get_by_rolename(self.role)
        # if self.apis:
        #     if not isinstance(apis[0], APICall):
        #         apis = [APICall.from_dict(i) for i in apis]
        #     self.apis = apis

    def to_str(self):
        return f"{self.role.prefix}{self.content}"

    def to_dict(self):
        data = self.model_dump()
        data["role"] = self.role.rolename
        return data

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return self.to_str()

    def copy(self):
        return copy.deepcopy(self)

    # auto determined api v.s. GT api calls (.apis, .type)
    def is_api_calling(self, content: str = None) -> bool:
        if content:
            return content.startswith("<Call API>")
        return self.role == Role.BOT and self.content.startswith("<Call API>")

    def get_api_infos(self, content: str = None) -> Tuple[str, str]:
        """
        return: action_name, action_parameters
        """
        # content = f"<Call API> {action_name}({action_parameters})"
        if content is None:
            content = self.content
        assert self.is_api_calling(content), f"Must be API calling message! But got {content}"
        content = content[len("<Call API> ") :].strip()
        re_pattern = r"(.*?)\((.*)\)"
        re_match = re.match(re_pattern, content)
        name, paras = re_match.group(1), re_match.group(2)
        return name, eval(paras)

    # def substitue_with_GT_content(self, GT_content: str):
    #     self.content, self.content_predict = GT_content, self.content

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if isinstance(self.role, (Role, CustomRole)):
            data["role"] = self.role.rolename
        return data


class Conversation(BaseModel):
    msgs: List[Message] = Field(default_factory=list)
    conversation_id: Optional[str] = None

    @classmethod
    def create(cls, conversation_id: Optional[str] = None) -> "Conversation":
        if not conversation_id:
            conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return cls(conversation_id=conversation_id)

    # class Config:
    #     arbitrary_types_allowed = True

    def add_message(
        self,
        msg: Union[Message, str],
        llm_name: str = None,
        llm_prompt: str = None,
        llm_response: str = None,
        role: Union[Role, str] = Role.USER,
    ):
        """Add a message to the conversation, accepting either a Message object or message parameters.

        Args:
            msg: Either a Message object or a string containing the message content
            prompt: Optional prompt string (only used if msg is str)
            llm_response: Optional LLM response string (only used if msg is str)
            role: Optional role (only used if msg is str)
        """
        if isinstance(msg, Message):
            # Handle Message object input
            msg.conversation_id = self.conversation_id
            msg.utterance_id = self.current_utterance_id
            self.msgs.append(msg)
        else:
            # Handle string input with optional parameters
            message = Message(
                role=role,
                content=msg,
                llm_name=llm_name,
                llm_prompt=llm_prompt,
                llm_response=llm_response,
                conversation_id=self.conversation_id,
                utterance_id=self.current_utterance_id,
            )
            self.msgs.append(message)

    def substitue_message(self, new_msg: Message, idx: int = -1, old_to_prediction: bool = True):
        new_msg.conversation_id = self.conversation_id
        new_msg.utterance_id = self.msgs[idx].utterance_id
        if old_to_prediction:
            new_msg.content_predict = self.msgs[idx].content
        self.msgs[idx] = new_msg

    def clear(self):
        self.msgs = []

    def get_message_by_idx(self, idx: int) -> Message:
        return self.msgs[idx]

    def get_messages_num(self, role: Role = None) -> int:
        if isinstance(role, str):
            role = Role.get_by_rolename(role)
        if role is None:
            return len(self.msgs)
        cnt = 0
        for msg in self.msgs:
            if msg.role == role:
                cnt += 1
        return cnt

    @property
    def current_utterance_id(self) -> int:
        return len(self.msgs)

    @property
    def messages(self) -> List[Message]:
        return self.msgs

    def get_last_message(self) -> Message:
        return self.msgs[-1]

    def get_called_apis(self) -> List[str]:
        """collect all API calls in the conversation by BOT"""
        apis = []
        for msg in self.msgs:
            if msg.is_api_calling():
                apis.append(msg.get_api_infos()[0])
        return apis

    @classmethod
    def from_messages(cls, msgs: List[Message]):
        assert len(msgs) > 0, f"Must have at least one message!"
        conv_id = msgs[0].conversation_id
        instance = cls(conversation_id=conv_id)
        instance.msgs = msgs
        return instance

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([m.to_dict() for m in self.msgs])

    @classmethod
    def load_from_json(cls, data: Union[Dict, List[Dict]]):
        conversation_id = data["conversation_id"] if isinstance(data, dict) else "0000"
        conv = data["msgs"] if isinstance(data, dict) else data
        instance = cls(conversation_id=conversation_id)
        for msg in conv:
            _role = Role.get_by_rolename(msg["role"])
            instance.add_message(
                Message(
                    role=_role,
                    content=msg["content"],
                    type=msg.get("type", None),
                    apis=msg.get("apis", None),
                )
            )
        return instance

    @classmethod
    def load_from_str(cls, s: str):
        ins = cls()
        for line in s.split("\n"):
            if not line.strip():
                continue
            if line.startswith("[BOT]"):
                ins.add_message(Message(Role.BOT, line[len("[BOT]") + 1 :]))
            elif line.startswith("[USER]"):
                ins.add_message(Message(Role.USER, line[len("[USER]") + 1 :]))
            elif line.startswith("[SYSTEM]"):
                ins.add_message(Message(Role.SYSTEM, line[len("[SYSTEM]") + 1 :]))
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
        if isinstance(other, list):
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

    def __getitem__(self, index: Union[int, slice]) -> Union[Message, "Conversation"]:
        # different behaviors for conv[0] and conv[:2]
        if isinstance(index, int):
            return self.msgs[index]
        elif isinstance(index, slice):
            new_conversation = Conversation(self.conversation_id)
            new_conversation.msgs = self.msgs[index]
            return new_conversation

    def __iter__(self) -> Iterator[Message]:
        return iter(self.msgs)


class ConversationWithIntention(BaseModel):
    user_intention: str
    conversation: Conversation

    def __str__(self) -> str:
        return f"simulated conversation with {len(self.conversation)} messages.\nUser intention: {self.user_intention}"
