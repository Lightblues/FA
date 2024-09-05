"""
"""
from typing import List

class UserProfile:
    persona: str = ""
    user_details: str = ""
    user_needs: str = ""
    dialogue_style: str = ""
    interation_patterns: str = ""
    profile: dict = None
    
    def __init__(self, persona:str, user_details:str, user_needs:str, dialogue_style:str, interaction_patterns:str):
        self.persona = persona
        self.user_details = user_details
        self.user_needs = user_needs
        self.dialogue_style = dialogue_style
        self.interation_patterns = interaction_patterns
        self.profile = {
            '角色设定': self.persona,
            '用户信息': self.user_details,
            '用户需求': self.user_needs,
            '对话风格': self.dialogue_style,
            '交互模式': self.interation_patterns
        }
    
    @classmethod
    def load_from_dict(
        cls, 
        profile_dict: dict,
        persona_key: str = 'persona',
        details_key: str = 'user_details', 
        needs_key: str = 'user_needs', 
        style_key: str = 'dialogue_style', 
        pattern_key: str = 'interative_pattern'
    ):
        instance = cls(profile_dict[persona_key], profile_dict[details_key], profile_dict[needs_key], profile_dict[style_key], profile_dict[pattern_key])
        return instance
    
    def to_str(self):
        profile_str = ''
        for i, key in enumerate(list(self.profile.keys())):
            profile_str += f"{i + 1}. {key}:\n    "
            profile_str += self.profile[key]
            profile_str += '\n'
        return profile_str

