from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.provider import ProviderType

class ProviderBase(BaseModel):
    name: str
    type: ProviderType
    base_url: HttpUrl
    headers: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class ProviderCreate(ProviderBase):
    api_key: Optional[str] = None

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    headers: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ProviderResponse(ProviderBase):
    id: int
    is_active: bool
    workspace_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProviderTest(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None
