"""
"""
from typing import List
from dataclasses import dataclass

# used for Chinese
COMPONENTS_ZH = {
    'persona': '角色设定',
    'user_details': '用户信息',
    'user_needs': '用户需求',
    'dialogue_style': '对话风格',
    'interactive_pattern': '交互模式'
}

NAME_MAP = dict(
    persona='persona',
    user_details='user_details',
    user_needs='user_needs',
    dialogue_style='dialogue_style',
    interaction_patterns='interactive_pattern'
)

@dataclass
class UserProfile:
    persona: str = ""
    user_details: str = ""
    user_needs: str = ""
    dialogue_style: str = ""
    interaction_patterns: str = ""
    required_apis: List[str] = None
    
    def __init__(
        self, persona:str="", user_details:str="", user_needs:str="", dialogue_style:str="", interaction_patterns:str="", 
        required_apis: List[str] = None,
        **kwargs
    ):
        self.persona = persona
        self.user_details = user_details
        self.user_needs = user_needs
        self.dialogue_style = dialogue_style
        self.interaction_patterns = interaction_patterns
        if required_apis is not None: self.required_apis = required_apis
        if kwargs:
            print(f"Unknown keys: {list(kwargs.items())}")
    
    @property
    def profile(self):
        return {
            'persona': self.persona,
            'user_details': self.user_details,
            'user_needs': self.user_needs,
            'dialogue_style': self.dialogue_style,
            'interaction_patterns': self.interaction_patterns
        }
    
    @classmethod
    def load_from_dict(
        cls, 
        profile_dict: dict,
    ):
        for k,v in NAME_MAP.items():    # rename
            if v in profile_dict:
                profile_dict[k] = profile_dict.pop(v)
        instance = cls(**profile_dict)
        return instance
    
    def to_str(self):
        profile_str = ''
        for i, key in enumerate(list(self.profile.keys())):
            profile_str += f"{i + 1}. {key}:\n    "
            profile_str += self.profile[key]
            profile_str += '\n'
        return profile_str
