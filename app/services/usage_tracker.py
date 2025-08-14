from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.requestlog import RequestLog
from app.models.apikey import APIKey
from app.models.model import Model
from app.models.provider import Provider

class UsageTracker:
    def __init__(self, db: Session):
        self.db = db
    
    def log_request(
        self,
        workspace_id: int,
        model_id: int,
        api_key_id: int,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: float,
        success: bool,
        error_message: Optional[str] = None,
        cost_usd: Optional[float] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RequestLog:
        """Log a completed request"""
        request_log = RequestLog(
            workspace_id=workspace_id,
            model_id=model_id,
            api_key_id=api_key_id,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message,
            cost_usd=cost_usd,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        self.db.add(request_log)
        self.db.commit()
        self.db.refresh(request_log)
        
        # Update API key last used timestamp
        api_key = self.db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if api_key:
            api_key.last_used_at = datetime.utcnow()
            self.db.commit()
        
        return request_log
    
    def get_workspace_usage(
        self,
        workspace_id: int,
        days: int = 30,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """Get usage statistics for a workspace"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if group_by == "day":
            date_format = func.date_trunc('day', RequestLog.created_at)
        elif group_by == "hour":
            date_format = func.date_trunc('hour', RequestLog.created_at)
        else:
            date_format = func.date_trunc('day', RequestLog.created_at)
        
        usage_stats = self.db.query(
            date_format.label('period'),
            func.count(RequestLog.id).label('total_requests'),
            func.sum(RequestLog.total_tokens).label('total_tokens'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.sum(RequestLog.cost_usd).label('total_cost'),
            func.count(RequestLog.id).filter(RequestLog.success == True).label('successful_requests'),
            func.count(RequestLog.id).filter(RequestLog.success == False).label('failed_requests')
        ).filter(
            RequestLog.workspace_id == workspace_id,
            RequestLog.created_at >= start_date,
            RequestLog.created_at <= end_date
        ).group_by(
            date_format
        ).order_by(
            date_format
        ).all()
        
        return [
            {
                "period": stat.period.isoformat() if stat.period else None,
                "total_requests": stat.total_requests or 0,
                "total_tokens": stat.total_tokens or 0,
                "avg_latency": round(stat.avg_latency, 2) if stat.avg_latency else 0,
                "total_cost": stat.total_cost or 0,
                "successful_requests": stat.successful_requests or 0,
                "failed_requests": stat.failed_requests or 0
            }
            for stat in usage_stats
        ]
    
    def get_model_usage(
        self,
        workspace_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get usage statistics by model"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        model_stats = self.db.query(
            RequestLog.model_name,
            func.count(RequestLog.id).label('total_requests'),
            func.sum(RequestLog.total_tokens).label('total_tokens'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.sum(RequestLog.cost_usd).label('total_cost')
        ).filter(
            RequestLog.workspace_id == workspace_id,
            RequestLog.created_at >= start_date,
            RequestLog.created_at <= end_date
        ).group_by(
            RequestLog.model_name
        ).order_by(
            desc(func.sum(RequestLog.total_tokens))
        ).all()
        
        return [
            {
                "model_name": stat.model_name,
                "total_requests": stat.total_requests or 0,
                "total_tokens": stat.total_tokens or 0,
                "avg_latency": round(stat.avg_latency, 2) if stat.avg_latency else 0,
                "total_cost": stat.total_cost or 0
            }
            for stat in model_stats
        ]
    
    def get_api_key_usage(
        self,
        workspace_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get usage statistics by API key"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        key_stats = self.db.query(
            APIKey.name,
            APIKey.key_prefix,
            func.count(RequestLog.id).label('total_requests'),
            func.sum(RequestLog.total_tokens).label('total_tokens'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.sum(RequestLog.cost_usd).label('total_cost')
        ).join(
            RequestLog, APIKey.id == RequestLog.api_key_id
        ).filter(
            RequestLog.workspace_id == workspace_id,
            RequestLog.created_at >= start_date,
            RequestLog.created_at <= end_date
        ).group_by(
            APIKey.id, APIKey.name, APIKey.key_prefix
        ).order_by(
            desc(func.sum(RequestLog.total_tokens))
        ).all()
        
        return [
            {
                "key_name": stat.name,
                "key_prefix": stat.key_prefix,
                "total_requests": stat.total_requests or 0,
                "total_tokens": stat.total_tokens or 0,
                "avg_latency": round(stat.avg_latency, 2) if stat.avg_latency else 0,
                "total_cost": stat.total_cost or 0
            }
            for stat in key_stats
        ]
    
    def get_provider_usage(
        self,
        workspace_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get usage statistics by provider"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        provider_stats = self.db.query(
            Provider.name,
            Provider.type,
            func.count(RequestLog.id).label('total_requests'),
            func.sum(RequestLog.total_tokens).label('total_tokens'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.sum(RequestLog.cost_usd).label('total_cost')
        ).join(
            Model, Provider.id == Model.provider_id
        ).join(
            RequestLog, Model.id == RequestLog.model_id
        ).filter(
            RequestLog.workspace_id == workspace_id,
            RequestLog.created_at >= start_date,
            RequestLog.created_at <= end_date
        ).group_by(
            Provider.id, Provider.name, Provider.type
        ).order_by(
            desc(func.sum(RequestLog.total_tokens))
        ).all()
        
        return [
            {
                "provider_name": stat.name,
                "provider_type": stat.type.value,
                "total_requests": stat.total_requests or 0,
                "total_tokens": stat.total_tokens or 0,
                "avg_latency": round(stat.avg_latency, 2) if stat.avg_latency else 0,
                "total_cost": stat.total_cost or 0
            }
            for stat in provider_stats
        ]
