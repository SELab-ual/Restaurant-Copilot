from sqlalchemy.orm import Session
from models import EventLog

def log_event(db: Session, *, actor: str, action: str, entity: str, entity_id: int | None = None, details: str | None = None):
    ev = EventLog(actor=actor, action=action, entity=entity, entity_id=entity_id, details=details)
    db.add(ev)
    db.commit()
