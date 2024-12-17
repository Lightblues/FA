from typing import List

from pydantic import BaseModel, Field

from ..api_registry import register_api


# Request and Response Models
class CityRequest(BaseModel):
    city: str


class ServicePoint(BaseModel):
    name: str
    address: str
    phone_number: str
    business_hours: str


class ServicePointCityListResponse(BaseModel):
    service_point_cities: List[str]


class ValidateCityResponse(BaseModel):
    # errcode: int
    errcode: int = Field(..., description="200 表示成功，其他表示错误")


class ServicePointInfoResponse(BaseModel):
    # errcode: int
    errcode: int = Field(..., description="200 表示成功，其他表示错误")
    service_points: List[ServicePoint]


register_api(
    "get_service_point_city_list",
    "获取服务网点城市列表",
    None,
    ServicePointCityListResponse,
)
register_api("validate_service_point_city", "校验服务网点城市", CityRequest, ValidateCityResponse)
register_api("get_service_points", "获取服务网点信息", CityRequest, ServicePointInfoResponse)
