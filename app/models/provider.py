from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import enum
from app.core.db import Base

class ProviderType(str, enum.Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    HTTP = "http"

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ProviderType), nullable=False)
    base_url = Column(String, nullable=False)
    encrypted_api_key = Column(String, nullable=True)  # For OpenAI/HTTP providers
    headers = Column(JSON, nullable=True)  # Additional headers
    config = Column(JSON, nullable=True)  # Provider-specific configuration
    is_active = Column(Boolean, default=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="providers")
    models = relationship("Model", back_populates="provider")
