from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.provider import Provider, ProviderType
from app.schemas.provider import ProviderCreate, ProviderUpdate
from app.core.security import encrypt_secret, decrypt_secret
from app.services.adapter_openai import OpenAIAdapter
from app.services.adapter_ollama import OllamaAdapter
from app.services.adapter_http import HTTPAdapter

class ProviderManager:
    def __init__(self, db: Session):
        self.db = db
    
    def create_provider(self, provider_data: ProviderCreate, workspace_id: int) -> Provider:
        """Create a new provider"""
        encrypted_key = None
        if provider_data.api_key:
            encrypted_key = encrypt_secret(provider_data.api_key)
        
        db_provider = Provider(
            name=provider_data.name,
            type=provider_data.type,
            base_url=str(provider_data.base_url),
            encrypted_api_key=encrypted_key,
            headers=provider_data.headers,
            config=provider_data.config,
            workspace_id=workspace_id
        )
        
        self.db.add(db_provider)
        self.db.commit()
        self.db.refresh(db_provider)
        return db_provider
    
    def get_providers(self, workspace_id: int) -> List[Provider]:
        """Get all providers for a workspace"""
        return self.db.query(Provider).filter(
            Provider.workspace_id == workspace_id,
            Provider.is_active == True
        ).all()
    
    def get_provider(self, provider_id: int, workspace_id: int) -> Optional[Provider]:
        """Get a specific provider"""
        return self.db.query(Provider).filter(
            Provider.id == provider_id,
            Provider.workspace_id == workspace_id
        ).first()
    
    def update_provider(self, provider_id: int, provider_data: ProviderUpdate, workspace_id: int) -> Optional[Provider]:
        """Update a provider"""
        provider = self.get_provider(provider_id, workspace_id)
        if not provider:
            return None
        
        update_data = provider_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)
        
        self.db.commit()
        self.db.refresh(provider)
        return provider
    
    def delete_provider(self, provider_id: int, workspace_id: int) -> bool:
        """Delete a provider"""
        provider = self.get_provider(provider_id, workspace_id)
        if not provider:
            return False
        
        provider.is_active = False
        self.db.commit()
        return True
    
    def get_adapter(self, provider: Provider):
        """Get the appropriate adapter for a provider"""
        if provider.type == ProviderType.OPENAI:
            return OpenAIAdapter(provider)
        elif provider.type == ProviderType.OLLAMA:
            return OllamaAdapter(provider)
        elif provider.type == ProviderType.HTTP:
            return HTTPAdapter(provider)
        else:
            raise ValueError(f"Unsupported provider type: {provider.type}")
    
    def test_provider(self, provider_id: int, workspace_id: int) -> dict:
        """Test a provider's connectivity"""
        provider = self.get_provider(provider_id, workspace_id)
        if not provider:
            return {"success": False, "message": "Provider not found"}
        
        try:
            adapter = self.get_adapter(provider)
            result = adapter.health_check()
            return result
        except Exception as e:
            return {"success": False, "message": str(e), "error": str(e)}
