from pydantic import BaseModel, Field
from typing import Literal, List

from ..api_registry import register_api


# Request and Response Models
class CountryRequest(BaseModel):
    country: str = Field(..., description="目标国家")

class GoodsListResponse(BaseModel):
    goods_list: List[str] = Field(..., description="该国家支持邮寄的物品类别列表, e.g. ['书籍', '服饰', '化妆品', ...]")

class ShippingRequest(BaseModel):
    country: str = Field(..., description="目标国家")
    goods: str = Field(..., description="用户要邮寄的物品")
class ShippingResponse(BaseModel):
    status: int = Field(..., description="200 表示成功，其他表示错误")
    isValid: bool = Field(..., description="true 表示支持邮寄，false 表示不支持邮寄")

register_api("query_goods_list", "查询物品列表", CountryRequest, GoodsListResponse)
register_api("query_shipping_status", "查询物品能否邮寄", ShippingRequest, ShippingResponse)
