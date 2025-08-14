import httpx
import time
from typing import Dict, Any, Optional
from app.models.provider import Provider
from app.core.security import decrypt_secret
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse

class OpenAIAdapter:
    def __init__(self, provider: Provider):
        self.provider = provider
        self.base_url = provider.base_url
        self.api_key = None
        if provider.encrypted_api_key:
            self.api_key = decrypt_secret(provider.encrypted_api_key)
        self.headers = provider.headers or {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the provider is accessible"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            headers.update(self.headers)
            
            response = httpx.get(f"{self.base_url}/models", headers=headers, timeout=10)
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Provider is accessible",
                    "latency_ms": round(latency, 2)
                }
            else:
                return {
                    "success": False,
                    "message": f"Provider returned status {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }
    
    async def chat_completion(self, request: ChatCompletionRequest, stream: bool = False) -> Any:
        """Forward chat completion request to OpenAI provider"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(self.headers)
        
        # Prepare the request payload
        payload = request.dict(exclude_unset=True)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Provider error: {response.status_code} - {response.text}")
            
            if stream:
                return response.aiter_bytes()
            else:
                return response.json()
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models from the provider"""
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        headers.update(self.headers)
        
        response = httpx.get(f"{self.base_url}/models", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get models: {response.status_code}")
