from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Table, User
from schemas import TableOut
from auth import get_current_user
from utils import log_event

router = APIRouter(prefix="/tables", tags=["tables"])

@router.post("/{table_id}/activate", response_model=TableOut)
def activate_table(table_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    table = db.query(Table).get(table_id)
    if not table:
        table = Table(id=table_id)
        db.add(table)
    table.active = True
    table.assigned_waiter_id = user.id
    db.commit()
    db.refresh(table)
    log_event(db, actor=f"waiter:{user.username}", action="activate_table", entity="table", entity_id=table.id)
    return table

@router.get("/{table_id}", response_model=TableOut)
def get_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(Table).get(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table
