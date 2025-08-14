import httpx
import time
import json
from typing import Dict, Any, Optional
from app.models.provider import Provider
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse

class OllamaAdapter:
    def __init__(self, provider: Provider):
        self.provider = provider
        self.base_url = provider.base_url.rstrip('/')
        self.config = provider.config or {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Ollama is running and accessible"""
        start_time = time.time()
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=10)
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Ollama is accessible",
                    "latency_ms": round(latency, 2)
                }
            else:
                return {
                    "success": False,
                    "message": f"Ollama returned status {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }
    
    async def chat_completion(self, request: ChatCompletionRequest, stream: bool = False) -> Any:
        """Send chat completion request to Ollama"""
        # Convert OpenAI format to Ollama format
        ollama_payload = {
            "model": request.model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ],
            "stream": stream,
            "options": {}
        }
        
        # Map OpenAI parameters to Ollama options
        if request.temperature is not None:
            ollama_payload["options"]["temperature"] = request.temperature
        if request.top_p is not None:
            ollama_payload["options"]["top_p"] = request.top_p
        if request.max_tokens is not None:
            ollama_payload["options"]["num_predict"] = request.max_tokens
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=ollama_payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code} - {response.text}")
            
            if stream:
                return response.aiter_bytes()
            else:
                return self._convert_ollama_response(response.json(), request.model)
    
    def _convert_ollama_response(self, ollama_response: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Convert Ollama response to OpenAI format"""
        # Extract the response content
        content = ""
        if "message" in ollama_response:
            content = ollama_response["message"].get("content", "")
        
        # Create OpenAI-compatible response
        openai_response = {
            "id": f"ollama-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # Ollama doesn't provide token counts
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        return openai_response
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models from Ollama"""
        response = httpx.get(f"{self.base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            # Convert to OpenAI format
            models = []
            for model in models_data.get("models", []):
                models.append({
                    "id": model["name"],
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "ollama"
                })
            return {"data": models}
        else:
            raise Exception(f"Failed to get Ollama models: {response.status_code}")
