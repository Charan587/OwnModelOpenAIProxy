from .workspace import Workspace
from .user import User, AuthProvider
from .provider import Provider, ProviderType
from .model import Model
from .apikey import APIKey, KeyStatus
from .requestlog import RequestLog

# Import the missing relationship model
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.db import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class UserWorkspaceRole(Base):
    __tablename__ = "user_workspace_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workspace_roles")
    workspace = relationship("Workspace", back_populates="users")

# Update the imports to include the new model
__all__ = [
    "Workspace", "User", "AuthProvider", "Provider", "ProviderType",
    "Model", "APIKey", "KeyStatus", "RequestLog", "UserWorkspaceRole", "UserRole"
]
