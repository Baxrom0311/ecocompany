"""
ECO COMPANY — User Model
Admin foydalanuvchilari (super_admin, editor)
"""
from sqlalchemy import Column, String, Boolean, Integer
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    token_version = Column(Integer, default=0, server_default="0", nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="editor", nullable=False)  # "super_admin" | "editor"
    is_active = Column(Boolean, default=True, nullable=False)
