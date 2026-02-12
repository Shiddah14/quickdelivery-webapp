
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uuid
import os

app = FastAPI(
    title="Maisha Mart Supermarket",
    description="Maisha Mart Supermarket - Online Store API. Quality products at affordable prices in Kakamega, Kenya.",
    version="1.0"
)

# ==================== Static Files ====================
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_homepage():
    return FileResponse(os.path.join(static_dir, "index.html"))


# ==================== Models ====================
class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"


class Category(str, Enum):
    vegetables = "vegetables"
    fruits = "fruits"
    dairy = "dairy"
    meat = "meat"
    bakery = "bakery"
    beverages = "beverages"
    household = "household"
    electronics = "electronics"


class Item(BaseModel):
    id: str
    name: str
    category: str
    price: float
    unit: str = "pc"
    stock: int = 0
    image: str = ""


class CreateItemRequest(BaseModel):
    name: str
    category: str
    price: float
    unit: str = "pc"
    stock: int = 0
    image: str = ""


class CustomerInfo(BaseModel):
    name: str
    phone: str
    area: Optional[str] = None
    address: str
    notes: Optional[str] = None
    payment_method: str = "mpesa"


class Order(BaseModel):
    id: str
    items: List[dict]
    customer: CustomerInfo
    subtotal: float
    delivery_fee: float = 0
    total: float
    status: OrderStatus = OrderStatus.pending
    date: str = ""


class CreateOrderRequest(BaseModel):
    items: List[dict]
    customer: CustomerInfo
    subtotal: float
    delivery_fee: float = 0


class UpdateStatusRequest(BaseModel):
    status: OrderStatus


# ==================== In-Memory Database ====================
items_db: List[Item] = []
orders_db: List[Order] = []


# ==================== Item Endpoints ====================
@app.post("/api/items", response_model=Item)
def add_item(item_request: CreateItemRequest):
    item = Item(id=str(uuid.uuid4()), **item_request.dict())
    items_db.append(item)
    return item


@app.get("/api/items", response_model=List[Item])
def list_items(category: Optional[str] = None):
    if category:
        return [item for item in items_db if item.category == category]
    return items_db


@app.get("/api/items/{item_id}", response_model=Item)
def get_item(item_id: str):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found.")


@app.put("/api/items/{item_id}", response_model=Item)
def update_item(item_id: str, item_request: CreateItemRequest):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            updated = Item(id=item_id, **item_request.dict())
            items_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Item not found.")


@app.delete("/api/items/{item_id}")
def delete_item(item_id: str):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return {"message": "Item deleted successfully."}
    raise HTTPException(status_code=404, detail="Item not found.")


# ==================== Order Endpoints ====================
@app.post("/api/orders", response_model=Order)
def create_order(order_request: CreateOrderRequest):
    from datetime import datetime
    total = order_request.subtotal + order_request.delivery_fee
    order = Order(
        id="MM-" + str(uuid.uuid4())[:8].upper(),
        items=order_request.items,
        customer=order_request.customer,
        subtotal=order_request.subtotal,
        delivery_fee=order_request.delivery_fee,
        total=total,
        date=datetime.utcnow().isoformat()
    )
    orders_db.append(order)
    return order


@app.get("/api/orders", response_model=List[Order])
def list_orders(status: Optional[str] = None):
    if status:
        return [order for order in orders_db if order.status == status]
    return orders_db


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    for order in orders_db:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found.")


@app.patch("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, request: UpdateStatusRequest):
    for order in orders_db:
        if order.id == order_id:
            order.status = request.status
            return order
    raise HTTPException(status_code=404, detail="Order not found.")


@app.delete("/api/orders/{order_id}")
def delete_order(order_id: str):
    for i, order in enumerate(orders_db):
        if order.id == order_id:
            orders_db.pop(i)
            return {"message": "Order deleted successfully."}
    raise HTTPException(status_code=404, detail="Order not found.")
