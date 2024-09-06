"""
"""
from typing import List

# used for Chinese
COMPONENTS_ZH = {
    'persona': '角色设定',
    'user_details': '用户信息',
    'user_needs': '用户需求',
    'dialogue_style': '对话风格',
    'interactive_pattern': '交互模式'
}

class UserProfile:
    persona: str = ""
    user_details: str = ""
    user_needs: str = ""
    dialogue_style: str = ""
    interaction_patterns: str = ""
    profile: dict = None
    
    def __init__(self, persona:str, user_details:str, user_needs:str, dialogue_style:str, interaction_patterns:str):
        self.persona = persona
        self.user_details = user_details
        self.user_needs = user_needs
        self.dialogue_style = dialogue_style
        self.interaction_patterns = interaction_patterns
        self.profile = {
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
        persona_key: str = 'persona',
        details_key: str = 'user_details', 
        needs_key: str = 'user_needs', 
        style_key: str = 'dialogue_style', 
        pattern_key: str = 'interactive_pattern'
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

