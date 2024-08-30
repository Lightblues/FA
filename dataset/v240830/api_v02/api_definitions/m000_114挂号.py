from pydantic import BaseModel, Field
from typing import List, Literal

from api_registry import register_api

class Slot(BaseModel):
    hospital_name: str
    department_name: str
    doctor_name: str
    time_period: str = Field(..., description="时间段, 例如 '09:00-10:00'")
    is_specialist: bool  # 是否为专家号

# Request and Response Models
class HospitalCheckRequest(BaseModel):
    hospital_name: str

class HospitalCheckResponse(BaseModel):
    hospital_exists: bool = Field(..., description="医院是否在以下列表: ['北京301医院', '北京安贞医院', '北京朝阳医院', '北京大学第一医院', '北京大学人民医院', '北京儿童医院', '北京积水潭医院', '北京世纪坛医院', '北京天坛医院', '北京协和医学院附属肿瘤医院', '北京协和医院', '北京宣武医院', '北京友谊医院', '北京中日友好医院', '北京中医药大学东方医院', '北京中医药大学东直门医院']")

class DepartmentCheckRequest(BaseModel):
    department_name: str
    hospital_name: str

class DepartmentCheckResponse(BaseModel):
    department_exists: bool = Field(..., description="医院存在, 并且科室在以下列表中: ['内科', '外科', '妇产科', '儿科', '骨科', '心血管科', '呼吸科', '消化科', '神经科', '泌尿科', '眼科', '耳鼻喉科', '口腔科', '皮肤科', '感染科', '肿瘤科', '精神科', '急诊科']")

class AppointmentQueryRequest(BaseModel):
    hospital_name: str = Field(..., description="医院名称, 要求医院存在")
    department_name: str = Field(..., description="科室名称, 要求科室存在")
    appointment_time: str = Field(..., description="预约时间")

class AppointmentQueryResponse(BaseModel):
    available_slots: int
    available_list: List[Slot]      # 可选列表
    specialist_count: int = Field(..., description="专家号数量")
    general_count: int = Field(..., description="普通号数量")

class OtherHospitalRecommendationRequest(BaseModel):
    department_name: str
    appointment_time: str

class OtherHospitalRecommendationResponse(BaseModel):
    available_slots: int
    available_list: List[Slot]      # 可选列表

class HospitalRegistrationRequest(BaseModel):
    id_number: str
    registration_type: str = Field(..., description="专家号 或 普通号")
    hospital_name: str
    department_name: str
    appointment_time: str

class HospitalRegistrationResponse(BaseModel):
    registration_status: int = Field(..., description="挂号结果, 1: 成功; 0: 失败")

class OtherHospitalRegistrationRequest(BaseModel):
    id_number: str
    hospital_name: str
    doctor_name: str

class OtherHospitalRegistrationResponse(BaseModel):
    registration_status: int = Field(..., description="挂号结果, 1: 成功; 0: 失败")

register_api("check_hospital", "校验挂号医院", HospitalCheckRequest, HospitalCheckResponse)
register_api("check_department", "科室校验", DepartmentCheckRequest, DepartmentCheckResponse)
register_api("query_appointment", "指定时间号源查询", AppointmentQueryRequest, AppointmentQueryResponse)
register_api("recommend_other_hospitals", "其他医院号源推荐", OtherHospitalRecommendationRequest, OtherHospitalRecommendationResponse)
register_api("register_hospital", "本医院挂号执行", HospitalRegistrationRequest, HospitalRegistrationResponse)
register_api("register_other_hospital", "其他医院挂号执行", OtherHospitalRegistrationRequest, OtherHospitalRegistrationResponse)

