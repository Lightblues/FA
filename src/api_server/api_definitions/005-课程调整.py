from typing import List

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

# Mocked data
mock_classes = {
    "Alice": ["Math", "Science", "History"],
    "Bob": ["Math", "Art"],
}


# Request and Response models
class CancelClassListRequest(BaseModel):
    name: str


class CancelClassListResponse(BaseModel):
    cancel_class_list: List[str]


class ModifyClassListRequest(BaseModel):
    name: str


class ModifyClassListResponse(BaseModel):
    modify_class_list: List[str]


class CancelClassRequest(BaseModel):
    class_name: str


class CancelClassResponse(BaseModel):
    cancel_status: str


class ModifyClassRequest(BaseModel):
    class_name: str


class ModifyClassResponse(BaseModel):
    modify_status: str


# API Endpoints
@app.post("/get_cancel_class_list", response_model=CancelClassListResponse)
def get_cancel_class_list(request: CancelClassListRequest):
    name = request.name
    cancel_class_list = mock_classes.get(name, [])
    return CancelClassListResponse(cancel_class_list=cancel_class_list)


@app.post("/get_modify_class_list", response_model=ModifyClassListResponse)
def get_modify_class_list(request: ModifyClassListRequest):
    name = request.name
    modify_class_list = mock_classes.get(name, [])
    return ModifyClassListResponse(modify_class_list=modify_class_list)


@app.post("/cancel_class", response_model=CancelClassResponse)
def cancel_class(request: CancelClassRequest):
    class_name = request.class_name
    # Mock the cancellation logic
    cancel_status = "Cancelled" if class_name in sum(mock_classes.values(), []) else "Class not found"
    return CancelClassResponse(cancel_status=cancel_status)


@app.post("/modify_class", response_model=ModifyClassResponse)
def modify_class(request: ModifyClassRequest):
    class_name = request.class_name
    # Mock the modification logic
    modify_status = "Modified" if class_name in sum(mock_classes.values(), []) else "Class not found"
    return ModifyClassResponse(modify_status=modify_status)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
