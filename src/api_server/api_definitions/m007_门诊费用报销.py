from pydantic import BaseModel
from typing import Literal

from ..api_registry import register_api


class IdentityQueryRequest(BaseModel):
    CardID: str

class IdentityQueryResponse(BaseModel):
    Identity: Literal["退休职工", "在职职工", "城乡居民"]


register_api("query_identity", "查询身份", IdentityQueryRequest, IdentityQueryResponse)