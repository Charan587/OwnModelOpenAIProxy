from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    context_length: Optional[int] = None
    default_flag: bool = False
    meta: Optional[Dict[str, Any]] = None

class ModelCreate(ModelBase):
    provider_id: int

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    context_length: Optional[int] = None
    default_flag: Optional[bool] = None
    meta: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ModelResponse(ModelBase):
    id: int
    provider_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
