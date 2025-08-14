import httpx
import time
import json
from typing import Dict, Any, Optional
from app.models.provider import Provider
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse

class HTTPAdapter:
    def __init__(self, provider: Provider):
        self.provider = provider
        self.base_url = provider.base_url.rstrip('/')
        self.config = provider.config or {}
        self.headers = provider.headers or {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the custom HTTP endpoint is accessible"""
        start_time = time.time()
        try:
            # Use the health check endpoint if configured, otherwise try the base URL
            health_url = self.config.get("health_endpoint", self.base_url)
            response = httpx.get(health_url, headers=self.headers, timeout=10)
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Custom endpoint is accessible",
                    "latency_ms": round(latency, 2)
                }
            else:
                return {
                    "success": False,
                    "message": f"Endpoint returned status {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }
    
    async def chat_completion(self, request: ChatCompletionRequest, stream: bool = False) -> Any:
        """Send chat completion request to custom HTTP endpoint"""
        # Get configuration for request mapping
        request_config = self.config.get("request_mapping", {})
        response_config = self.config.get("response_mapping", {})
        
        # Build the request payload according to configuration
        payload = self._build_request_payload(request, request_config)
        
        # Determine the endpoint
        endpoint = request_config.get("endpoint", "/chat/completions")
        url = f"{self.base_url}{endpoint}"
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        
        # Add any custom headers from config
        if "headers" in request_config:
            headers.update(request_config["headers"])
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Custom endpoint error: {response.status_code} - {response.text}")
            
            if stream:
                return response.aiter_bytes()
            else:
                return self._convert_response(response.json(), request.model, response_config)
    
    def _build_request_payload(self, request: ChatCompletionRequest, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build the request payload according to custom configuration"""
        # Default OpenAI format
        if not config:
            return request.dict(exclude_unset=True)
        
        # Custom mapping
        payload = {}
        
        # Map messages
        if "messages" in config:
            message_mapping = config["messages"]
            payload[message_mapping.get("field", "messages")] = [
                {
                    message_mapping.get("role_field", "role"): msg.role,
                    message_mapping.get("content_field", "content"): msg.content
                }
                for msg in request.messages
            ]
        else:
            payload["messages"] = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Map other fields
        field_mappings = {
            "model": "model",
            "temperature": "temperature",
            "max_tokens": "max_tokens",
            "stream": "stream"
        }
        
        for openai_field, custom_field in field_mappings.items():
            if hasattr(request, openai_field) and getattr(request, openai_field) is not None:
                payload[custom_field] = getattr(request, openai_field)
        
        # Add any additional fields from config
        if "additional_fields" in config:
            payload.update(config["additional_fields"])
        
        return payload
    
    def _convert_response(self, response: Dict[str, Any], model: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert the custom response to OpenAI format"""
        if not config:
            # Try to detect if it's already in OpenAI format
            if "choices" in response and "usage" in response:
                return response
        
        # Custom response mapping
        openai_response = {
            "id": f"custom-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
        
        # Map choices
        choices_field = config.get("choices_field", "choices")
        if choices_field in response:
            choices = response[choices_field]
            if isinstance(choices, list):
                for i, choice in enumerate(choices):
                    message_field = config.get("message_field", "message")
                    content_field = config.get("content_field", "content")
                    
                    if message_field in choice:
                        message = choice[message_field]
                        content = message.get(content_field, "") if isinstance(message, dict) else str(message)
                        
                        openai_response["choices"].append({
                            "index": i,
                            "message": {
                                "role": "assistant",
                                "content": content
                            },
                            "finish_reason": "stop"
                        })
        
        # Map usage if available
        usage_field = config.get("usage_field", "usage")
        if usage_field in response:
            usage = response[usage_field]
            if isinstance(usage, dict):
                openai_response["usage"] = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
        
        return openai_response
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models from custom endpoint"""
        models_endpoint = self.config.get("models_endpoint", "/models")
        url = f"{self.base_url}{models_endpoint}"
        
        response = httpx.get(url, headers=self.headers, timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            # Try to convert to OpenAI format
            if "data" in models_data:
                return models_data
            elif isinstance(models_data, list):
                models = []
                for model in models_data:
                    if isinstance(model, str):
                        models.append({
                            "id": model,
                            "object": "model",
                            "created": int(time.time()),
                            "owned_by": "custom"
                        })
                return {"data": models}
            else:
                return {"data": []}
        else:
            raise Exception(f"Failed to get models: {response.status_code}")
