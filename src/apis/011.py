""" JUST example code! see full list of apis' code in [data] """

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Mock data
mock_orders = [
    {"order_id": "ORD123", "amount": 100.50, "transaction_time": "2024-07-01T10:00:00", "details": "Order details for ORD123"},
    {"order_id": "ORD124", "amount": 200.75, "transaction_time": "2024-07-02T11:30:00", "details": "Order details for ORD124"},
    {"order_id": "ORD125", "amount": 150.00, "transaction_time": "2024-07-01T12:45:00", "details": "Order details for ORD125"},
]

# Request and response models
class QueryByAmountRequest(BaseModel):
    amount: float

class QueryByAmountResponse(BaseModel):
    order_links: List[str]

class QueryByTimeRequest(BaseModel):
    transaction_time: str

class QueryByTimeResponse(BaseModel):
    order_links: List[str]

class QueryByOrderIdRequest(BaseModel):
    order_id: str

class QueryByOrderIdResponse(BaseModel):
    details: str

# API endpoints
@app.post("/query_by_amount", response_model=QueryByAmountResponse)
def query_by_amount(request: QueryByAmountRequest):
    order_links = [f"/orders/{order['order_id']}" for order in mock_orders if order["amount"] == request.amount]
    if not order_links:
        raise HTTPException(status_code=404, detail="No orders found with the specified amount")
    return QueryByAmountResponse(order_links=order_links)

@app.post("/query_by_time", response_model=QueryByTimeResponse)
def query_by_time(request: QueryByTimeRequest):
    order_links = [f"/orders/{order['order_id']}" for order in mock_orders if order["transaction_time"] == request.transaction_time]
    if not order_links:
        raise HTTPException(status_code=404, detail="No orders found with the specified transaction time")
    return QueryByTimeResponse(order_links=order_links)

@app.post("/query_by_order_id", response_model=QueryByOrderIdResponse)
def query_by_order_id(request: QueryByOrderIdRequest):
    order = next((order for order in mock_orders if order["order_id"] == request.order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="No orders found with the specified order ID")
    return QueryByOrderIdResponse(details=order["details"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
