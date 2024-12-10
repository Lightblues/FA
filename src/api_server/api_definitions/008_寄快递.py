from pydantic import BaseModel
from typing import List
from api_registry import register_api


# Request and Response Models
class ItemsRequest(BaseModel):
    Items: List[str]

class DangerResponse(BaseModel):
    containDander: bool

class OrderRequest(BaseModel):
    Addr: str
    PhoneNumber: str

class OrderResponse(BaseModel):
    orderStatus: str


register_api("check_dangerous_items", "检查危险物品", ItemsRequest, DangerResponse)
register_api("place_order", "下订单", OrderRequest, OrderResponse)