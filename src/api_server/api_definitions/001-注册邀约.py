from typing import List

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


# Request and Response Models
class QueryByAmountRequest(BaseModel):
    amount: float


class QueryByAmountResponse(BaseModel):
    order_links: List[str]


# Mock Data
mock_order_links = {
    100.0: ["order_link_1", "order_link_2"],
    200.0: ["order_link_3", "order_link_4"],
    300.0: ["order_link_5", "order_link_6"],
}


# API Endpoint
@app.post("/query_by_amount", response_model=QueryByAmountResponse)
def query_by_amount(request: QueryByAmountRequest):
    amount = request.amount
    order_links = mock_order_links.get(amount, [])
    return QueryByAmountResponse(order_links=order_links)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
