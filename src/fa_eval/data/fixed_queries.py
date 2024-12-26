from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fa_core.common import Config


class FixedQueries(BaseModel):
    workflow_dataset: str = None
    workflow_id: str
    user_queries: List[str]

    eval_session_id: str = None
    eval_description: str = None
