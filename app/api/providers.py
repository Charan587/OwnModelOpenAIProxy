from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.auth import get_current_user_with_workspace
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse, ProviderTest
from app.services.provider_manager import ProviderManager

router = APIRouter(prefix="/admin/providers", tags=["providers"])

@router.post("/", response_model=ProviderResponse)
def create_provider(
    provider_data: ProviderCreate,
    current_user, workspace_id, role = Depends(get_current_user_with_workspace),
    db: Session = Depends(get_db)
):
    """Create a new provider"""
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create providers"
        )
    
    provider_manager = ProviderManager(db)
    provider = provider_manager.create_provider(provider_data, workspace_id)
    
    return ProviderResponse(
        id=provider.id,
        name=provider.name,
        type=provider.type,
        base_url=provider.base_url,
        headers=provider.headers,
        config=provider.config,
        is_active=provider.is_active,
        workspace_id=provider.workspace_id,
        created_at=provider.created_at,
        updated_at=provider.updated_at
    )

@router.get("/", response_model=List[ProviderResponse])
def list_providers(
    current_user, workspace_id, role = Depends(get_current_user_with_workspace),
    db: Session = Depends(get_db)
):
    """List all providers for the workspace"""
    provider_manager = ProviderManager(db)
    providers = provider_manager.get_providers(workspace_id)
    
    return [
        ProviderResponse(
            id=provider.id,
            name=provider.name,
            type=provider.type,
            base_url=provider.base_url,
            headers=provider.headers,
            config=provider.config,
            is_active=provider.is_active,
            workspace_id=provider.workspace_id,
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
        for provider in providers
    ]

@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider(
    provider_id: int,
    current_user, workspace_id, role = Depends(get_current_user_with_workspace),
    db: Session = Depends(get_db)
):
    """Get a specific provider"""
    provider_manager = ProviderManager(db)
    provider = provider_manager.get_provider(provider_id, workspace_id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )
    
    return ProviderResponse(
        id=provider.id,
        name=provider.name,
        type=provider.type,
        base_url=provider.base_url,
        headers=provider.headers,
        config=provider.config,
        is_active=provider.is_active,
        workspace_id=provider.workspace_id,
        created_at=provider.created_at,
        updated_at=provider.updated_at
    )

@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    current_user, workspace_id, role = Depends(get_current_user_with_workspace),
    db: Session = Depends(get_db)
):
    """Update a provider"""
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update providers"
        )
    
    provider_manager = ProviderManager(db)
    provider = provider_manager.update_provider(provider_id, provider_data, workspace_id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )
    
    return ProviderResponse(
        id=provider.id,
        name=provider.name,
        type=provider.type,
        base_url=provider.base_url,
        headers=provider.headers,
        config=provider.config,
        is_active=provider.is_active,
        workspace_id=provider.workspace_id,
        created_at=provider.created_at,
        updated_at=provider.updated_at
    )

@router.delete("/{provider_id}")
def delete_provider(
    provider_id: int,
    current_user, workspace_id, role = Depends(get_current_user_with_workspace),
    db: Session = Depends(get_db)
):
    """Delete a provider"""
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete providers"
        )
    
    provider_manager = ProviderManager(db)
    success = provider_manager.delete_provider(provider_id, workspace_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )
    
    return {"message": "Provider deleted successfully"}

@router.post("/{provider_id}/test", response_model=ProviderTest)
def test_provider(
    provider_id: int,
    current_user, workspace_id, role = Depends(get_current_user_with_workspace),
    db: Session = Depends(get_db)
):
    """Test provider connectivity"""
    provider_manager = ProviderManager(db)
    result = provider_manager.test_provider(provider_id, workspace_id)
    
    return ProviderTest(**result)
