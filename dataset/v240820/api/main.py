from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

# Mock Data
news_data = [
    {"location": "北京", "type": "政治", "time": "今天", "title": "北京政治新闻1"},
    {"location": "上海", "type": "经济", "time": "昨天", "title": "上海经济新闻1"},
    {"location": "广州", "type": "体育", "time": "本周", "title": "广州体育新闻1"},
    {"location": "深圳", "type": "娱乐", "time": "本月", "title": "深圳娱乐新闻1"},
    # Add more mock data as needed
]

# Request Model
class NewsQueryRequest(BaseModel):
    news_location: str
    news_type: str
    news_time: str

# Response Model
class NewsQueryResponse(BaseModel):
    news_list: List[str]

@app.post("/query_news", response_model=NewsQueryResponse)
def query_news(request: NewsQueryRequest):
    filtered_news = [
        news["title"] for news in news_data
        if news["location"] == request.news_location and
           news["type"] == request.news_type and
           news["time"] == request.news_time
    ]
    return NewsQueryResponse(news_list=filtered_news)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9390)