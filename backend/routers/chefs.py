from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import OrderItem, ItemStatus
from utils import log_event

router = APIRouter(prefix="/chefs", tags=["chefs"])

@router.post("/items/{item_id}/accept")
def accept_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ItemStatus.accepted
    db.commit()
    log_event(db, actor="chef", action="accept_item", entity="order_item", entity_id=item.id)
    return {"status": "accepted"}

@router.post("/items/{item_id}/reject")
def reject_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ItemStatus.rejected
    db.commit()
    log_event(db, actor="chef", action="reject_item", entity="order_item", entity_id=item.id)
    return {"status": "rejected"}

@router.post("/items/{item_id}/ready")
def ready_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ItemStatus.ready
    db.commit()
    log_event(db, actor="chef", action="ready_item", entity="order_item", entity_id=item.id)
    return {"status": "ready"}
