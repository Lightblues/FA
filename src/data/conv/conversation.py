import copy
import datetime
from typing import Dict, Iterator, List, Optional, Tuple, Union

import pandas as pd
from pydantic import BaseModel, Field

from .message import Message
from .role import Role


class Conversation(BaseModel):
    msgs: List[Message] = Field(default_factory=list)
    conversation_id: Optional[str] = None

    @classmethod
    def create(cls, conversation_id: Optional[str] = None) -> "Conversation":
        if not conversation_id:
            conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return cls(conversation_id=conversation_id)

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
