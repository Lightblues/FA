from typing import Dict, Optional, Any
from pydantic import BaseModel

class BaseResponse(BaseModel):
    error_code: int = 0
    error_msg: str = ""
