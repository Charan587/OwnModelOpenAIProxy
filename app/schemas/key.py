from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.apikey import KeyStatus

class APIKeyBase(BaseModel):
    name: str
    scopes: List[str] = Field(default=["model:use"])
    rpm: int = 60
    tpm: int = 10000
    daily_cap: int = 100000

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    scopes: Optional[List[str]] = None
    rpm: Optional[int] = None
    tpm: Optional[int] = None
    daily_cap: Optional[int] = None
    status: Optional[KeyStatus] = None

class APIKeyResponse(APIKeyBase):
    id: int
    key_prefix: str
    status: KeyStatus
    workspace_id: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class APIKeyFull(APIKeyResponse):
    full_key: str  # Only returned on creation
