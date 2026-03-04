from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User, Role
from schemas import LoginRequest, Token, UserOut
from auth import create_access_token, verify_password, get_password_hash, REVOKED

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        # seed default waiter if not exists and provided creds match default
        if payload.username == "waiter1" and payload.password == "password":
            user = User(username="waiter1", password_hash=get_password_hash("password"), role=Role.waiter)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return Token(access_token=token)

@router.post("/logout")
def logout(token: Token):
    REVOKED.add(token.access_token)
    return {"status": "logged_out"}

@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), token: Token | None = None):
    # Prototype endpoint; in real code use get_current_user
    return UserOut(id=1, username="waiter1", role="waiter")
