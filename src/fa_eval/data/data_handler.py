from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fa_core.common import Config


class FAEvalDataHandler(BaseModel):
    cfg: Config
