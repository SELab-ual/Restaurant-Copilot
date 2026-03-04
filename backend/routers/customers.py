from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Table, Order, OrderItem, OrderStatus, ItemStatus
from schemas import MenuItem, CreateOrderResponse, AddItemRequest, OrderOut
from utils import log_event

router = APIRouter(prefix="/customers", tags=["customers"])

# Static menu (prototype)
MENU = [
    {"name": "Margherita Pizza", "price": 8.5},
    {"name": "Spaghetti Carbonara", "price": 10.0},
    {"name": "House Salad", "price": 5.0},
    {"name": "Tiramisu", "price": 4.0},
    {"name": "Espresso", "price": 2.2},
]

@router.get("/menu", response_model=list[MenuItem])
def get_menu():
    return MENU

@router.post("/tables/{table_id}/orders", response_model=CreateOrderResponse)
def create_pending_order(table_id: int, db: Session = Depends(get_db)):
    table = db.query(Table).get(table_id)
    if not table or not table.active:
        raise HTTPException(status_code=400, detail="Table not active")
    order = Order(table_id=table_id, status=OrderStatus.pending)
    db.add(order)
    db.commit()
    db.refresh(order)
    log_event(db, actor=f"table:{table_id}", action="create_order", entity="order", entity_id=order.id)
    return {"order_id": order.id}

@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders/{order_id}/items", response_model=OrderOut)
def add_item(order_id: int, payload: AddItemRequest, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order or order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Order not pending")
    item = OrderItem(order_id=order_id, name=payload.name, price=payload.price)
    db.add(item)
    db.commit()
    db.refresh(order)
    log_event(db, actor=f"order:{order_id}", action="add_item", entity="order_item", entity_id=item.id, details=item.name)
    return order

@router.delete("/orders/{order_id}/items/{item_id}", response_model=OrderOut)
def remove_item(order_id: int, item_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order or order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Order not pending")
    item = db.query(OrderItem).get(item_id)
    if not item or item.order_id != order_id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    db.refresh(order)
    log_event(db, actor=f"order:{order_id}", action="remove_item", entity="order_item", entity_id=item_id)
    return order

@router.post("/orders/{order_id}/place", response_model=OrderOut)
def place_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order or len(order.items) == 0:
        raise HTTPException(status_code=400, detail="Order empty or missing")
    order.status = OrderStatus.placed
    db.commit()
    db.refresh(order)
    log_event(db, actor=f"order:{order_id}", action="place_order", entity="order", entity_id=order.id)
    return order

@router.delete("/orders/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order or order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
    order.status = OrderStatus.cancelled
    db.commit()
    log_event(db, actor=f"order:{order_id}", action="cancel_order", entity="order", entity_id=order.id)
    return {"status": "cancelled"}
