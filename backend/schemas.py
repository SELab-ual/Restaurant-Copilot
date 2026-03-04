from pydantic import BaseModel, Field
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True

class MenuItem(BaseModel):
    name: str
    price: float

class CreateOrderResponse(BaseModel):
    order_id: int

class AddItemRequest(BaseModel):
    name: str
    price: float = 0.0

class OrderItemOut(BaseModel):
    id: int
    name: str
    price: float
    status: str
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    table_id: int
    status: str
    items: List[OrderItemOut]
    class Config:
        from_attributes = True

class TableOut(BaseModel):
    id: int
    active: bool
    assigned_waiter_id: Optional[int]
    class Config:
        from_attributes = True
