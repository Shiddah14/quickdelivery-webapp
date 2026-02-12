
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from enum import Enum
import uuid

app = FastAPI(title="QuickDelivery", description="Deliver groceries and home appliances.", version="1.0")

items_db = []
orders_db = []

class OrderStatus(str, Enum):
    pending = "pending"
    dispatched = "dispatched"
    delivered = "delivered"

class Item(BaseModel):
    id: str
    name: str
    category: str
    price: float

class CreateItemRequest(BaseModel):
    name: str
    category: str
    price: float

class Order(BaseModel):
    id: str
    item_ids: List[str]
    customer_name: str
    address: str
    status: OrderStatus = OrderStatus.pending

class CreateOrderRequest(BaseModel):
    item_ids: List[str]
    customer_name: str
    address: str

@app.post("/items", response_model=Item)
def add_item(item_request: CreateItemRequest):
    item = Item(id=str(uuid.uuid4()), **item_request.dict())
    items_db.append(item)
    return item

@app.get("/items", response_model=List[Item])
def list_items():
    return items_db

@app.post("/orders", response_model=Order)
def create_order(order_request: CreateOrderRequest):
    for item_id in order_request.item_ids:
        if not any(item.id == item_id for item in items_db):
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    order = Order(id=str(uuid.uuid4()), **order_request.dict())
    orders_db.append(order)
    return order

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    for order in orders_db:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found.")

@app.patch("/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, status: OrderStatus):
    for order in orders_db:
        if order.id == order_id:
            order.status = status
            return order
    raise HTTPException(status_code=404, detail="Order not found.")
