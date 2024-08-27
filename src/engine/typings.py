from typing import List, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class BotActionMeta:
    input_details: Any = None
    output_details: Any = None
    
    action_infos: Dict = None     # action_name
    
    debug_infos: Optional[Dict] = None # for debug