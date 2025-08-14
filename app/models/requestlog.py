from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from app.core.db import Base

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    
    # Request details
    model_name = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    
    # Performance metrics
    latency_ms = Column(Float, nullable=False)
    cost_usd = Column(Float, nullable=True)
    
    # Status
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="request_logs")
    model = relationship("Model", back_populates="request_logs")
    api_key = relationship("APIKey", back_populates="request_logs")
