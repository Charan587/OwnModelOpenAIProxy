from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import enum
from app.core.db import Base

class KeyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hashed_key = Column(String, nullable=False)  # Argon2 hash of the full key
    key_prefix = Column(String, nullable=False)  # First 8 chars for identification
    scopes = Column(JSON, nullable=False)  # List of scopes
    rpm = Column(Integer, default=60)  # Requests per minute
    tpm = Column(Integer, default=10000)  # Tokens per minute
    daily_cap = Column(Integer, default=100000)  # Daily token cap
    status = Column(Enum(KeyStatus), default=KeyStatus.ACTIVE)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="api_keys")
    request_logs = relationship("RequestLog", back_populates="api_key")
