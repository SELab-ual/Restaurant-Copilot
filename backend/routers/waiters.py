from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User, Table, Order, OrderStatus, OrderItem, ItemStatus
from auth import get_current_user
from utils import log_event

router = APIRouter(prefix="/waiters", tags=["waiters"])

@router.get("/me/tables")
def my_tables(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tables = db.query(Table).filter(Table.assigned_waiter_id == user.id).all()
    return [{"id": t.id, "active": t.active} for t in tables]

@router.get("/tables/{table_id}/orders")
def table_orders(table_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    table = db.query(Table).get(table_id)
    if not table or table.assigned_waiter_id != user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this table")
    orders = db.query(Order).filter(Order.table_id == table_id).all()
    return [{"id": o.id, "status": o.status, "items": [{"id": i.id, "name": i.name, "status": i.status} for i in o.items]} for o in orders]

@router.post("/orders/{order_id}/accept")
def accept_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).get(order_id)
    if not order or order.status != OrderStatus.placed:
        raise HTTPException(status_code=400, detail="Order not placed")
    table = db.query(Table).get(order.table_id)
    if table.assigned_waiter_id != user.id:
        raise HTTPException(status_code=403, detail="Not assigned to table")
    order.status = OrderStatus.approved
    db.commit()
    log_event(db, actor=f"waiter:{user.username}", action="accept_order", entity="order", entity_id=order.id)
    return {"status": "approved"}

@router.post("/orders/{order_id}/reject")
def reject_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).get(order_id)
    if not order or order.status != OrderStatus.placed:
        raise HTTPException(status_code=400, detail="Order not placed")
    table = db.query(Table).get(order.table_id)
    if table.assigned_waiter_id != user.id:
        raise HTTPException(status_code=403, detail="Not assigned to table")
    order.status = OrderStatus.cancelled
    db.commit()
    log_event(db, actor=f"waiter:{user.username}", action="reject_order", entity="order", entity_id=order.id)
    return {"status": "rejected"}

@router.post("/items/{item_id}/delivered")
def mark_delivered(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    table = db.query(Table).get(db.query(Order).get(item.order_id).table_id)
    if table.assigned_waiter_id != user.id:
        raise HTTPException(status_code=403, detail="Not assigned to table")
    item.status = ItemStatus.delivered
    db.commit()
    log_event(db, actor=f"waiter:{user.username}", action="deliver_item", entity="order_item", entity_id=item.id)
    return {"status": "delivered"}
