from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from db import Base
import enum
from datetime import datetime

class Role(str, enum.Enum):
    waiter = "waiter"
    supervisor = "supervisor"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.waiter)

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=False)
    assigned_waiter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_waiter = relationship("User")

class OrderStatus(str, enum.Enum):
    pending = "pending"
    placed = "placed"
    approved = "approved"  # accepted by waiter
    cancelled = "cancelled"

class ItemStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"  # by chef
    rejected = "rejected"  # by chef
    ready = "ready"
    delivered = "delivered"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    table = relationship("Table")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, default=0.0)
    status = Column(Enum(ItemStatus), default=ItemStatus.pending, nullable=False)
    order = relationship("Order", back_populates="items")

class EventLog(Base):
    __tablename__ = "event_log"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
