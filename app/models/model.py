from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from app.core.db import Base

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    context_length = Column(Integer, nullable=True)
    default_flag = Column(Boolean, default=False)
    meta = Column(JSON, nullable=True)  # Model-specific metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("Provider", back_populates="models")
    request_logs = relationship("RequestLog", back_populates="model")
