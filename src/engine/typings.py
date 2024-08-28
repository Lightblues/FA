from typing import List, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict, field

@dataclass
class APICalling_Info:
    name: str = ""
    # args: List
    kwargs: Dict = field(default_factory=dict)



@dataclass
class BaseActionMeta:
    # detailed infos of LLM for logging
    input_details: Any = None
    output_details: Any = None

@dataclass
class BotActionMeta(BaseActionMeta):
    apicalling_info: APICalling_Info = field(default_factory=APICalling_Info)
    debug_infos: Optional[Dict] = None
    
@dataclass
class UserActionMetas(BaseActionMeta):
    pass

@dataclass
class APIActionMetas(BaseActionMeta):
    apicalling_info_query: APICalling_Info = field(default_factory=APICalling_Info)
    apicalling_info_matched: APICalling_Info = field(default_factory=APICalling_Info)
    entity_linking_log: List[Dict] = field(default_factory=list)

