from pydantic import BaseModel
from typing import Literal, Union

from api_registry import register_api


# Request and Response Models
class QueryInvoiceMethodRequest(BaseModel):
    order_id: int

class QueryInvoiceMethodResponse(BaseModel):
    invoice_method: Literal["平台开具", "酒店开具"]

class QueryInvoiceProgressRequest(BaseModel):
    name: str

class QueryInvoiceProgressResponse(BaseModel):
    invoice_progress: str

class QueryMemberStatusRequest(BaseModel):
    card_id: Union[str, int]

class QueryMemberStatusResponse(BaseModel):
    card_type: Literal["白金卡", "非白金卡"]

register_api("query_invoice_method", "查询开票方式", QueryInvoiceMethodRequest, QueryInvoiceMethodResponse)
register_api("query_invoice_progress", "查询开票进度", QueryInvoiceProgressRequest, QueryInvoiceProgressResponse)
register_api("query_member_status", "查询会员状态", QueryMemberStatusRequest, QueryMemberStatusResponse)
