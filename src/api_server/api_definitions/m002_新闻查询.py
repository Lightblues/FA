from pydantic import BaseModel
from typing import List, Literal

from api_registry import register_api

class NewsQueryRequest(BaseModel):
    news_location: Literal["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "重庆"]
    news_type: Literal["政治", "经济", "体育", "娱乐", "科技", "教育", "健康", "国际"]
    news_time: str

class NewsQueryResponse(BaseModel):
    news_list: List[str]

register_api("query_news", "查询新闻", NewsQueryRequest, NewsQueryResponse)
