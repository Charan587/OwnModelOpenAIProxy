from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import time
import secrets
from app.core.db import get_db
from app.core.rate_limit import RateLimiter
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.models.model import Model
from app.models.apikey import APIKey
from app.models.provider import Provider
from app.services.provider_manager import ProviderManager
from app.services.usage_tracker import UsageTracker
from app.core.security import verify_token

router = APIRouter(prefix="/v1", tags=["chat"])

def verify_api_key(request: Request, db: Session = Depends(get_db)) -> tuple[int, int]:
    """Verify API key and return workspace_id and key_id"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    api_key = auth_header.split(" ")[1]
    
    # Find the API key in the database
    db_key = db.query(APIKey).filter(
        APIKey.status == "active"
    ).all()
    
    # Check each key (in production, use proper hashing)
    for key in db_key:
        if key.hashed_key == api_key:  # Simplified for MVP
            return key.workspace_id, key.id
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    workspace_id: int, api_key_id: int = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Chat completion endpoint compatible with OpenAI API"""
    start_time = time.time()
    
    # Get the API key details
    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check rate limits
    rate_limiter = RateLimiter()
    can_proceed, error_info = rate_limiter.check_rate_limit(
        str(api_key_id), api_key.rpm, api_key.tpm, api_key.daily_cap
    )
    
    if not can_proceed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_info["error"],
            headers={"Retry-After": str(error_info.get("retry_after", 60))}
        )
    
    # Find the model
    model = db.query(Model).filter(
        Model.name == request.model,
        Model.is_active == True
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{request.model}' not found"
        )
    
    # Get the provider
    provider = db.query(Provider).filter(Provider.id == model.provider_id).first()
    if not provider or not provider.is_active:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model provider is not available"
        )
    
    try:
        # Get the appropriate adapter
        provider_manager = ProviderManager(db)
        adapter = provider_manager.get_adapter(provider)
        
        # Make the request
        if request.stream:
            # Handle streaming
            response_stream = await adapter.chat_completion(request, stream=True)
            
            # For streaming, we need to return a StreamingResponse
            # This is a simplified version - in production you'd want proper SSE handling
            async def generate_stream():
                async for chunk in response_stream:
                    yield chunk
            
            return StreamingResponse(generate_stream(), media_type="text/plain")
        else:
            # Handle non-streaming
            response = await adapter.chat_completion(request, stream=False)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract token counts from response
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # Update rate limiting counters
            rate_limiter.increment_usage(str(api_key_id), total_tokens)
            
            # Log the request
            usage_tracker = UsageTracker(db)
            usage_tracker.log_request(
                workspace_id=workspace_id,
                model_id=model.id,
                api_key_id=api_key_id,
                model_name=request.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                success=True
            )
            
            return response
            
    except Exception as e:
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log the error
        usage_tracker = UsageTracker(db)
        usage_tracker.log_request(
            workspace_id=workspace_id,
            model_id=model.id,
            api_key_id=api_key_id,
            model_name=request.model,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=latency_ms,
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider error: {str(e)}"
        )
