import redis
import time
from typing import Optional, Tuple
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

class RateLimiter:
    def __init__(self):
        self.redis = redis_client
    
    def check_rate_limit(self, key_id: str, rpm: int, tpm: int, daily_cap: int) -> Tuple[bool, dict]:
        """Check if request is within rate limits"""
        now = int(time.time())
        current_hour = now - (now % 3600)
        current_day = now - (now % 86400)
        
        # Check RPM
        rpm_key = f"rpm:{key_id}:{current_hour}"
        current_rpm = self.redis.get(rpm_key)
        if current_rpm and int(current_rpm) >= rpm:
            return False, {"error": "Rate limit exceeded (RPM)", "retry_after": 3600 - (now % 3600)}
        
        # Check TPM
        tpm_key = f"tpm:{key_id}:{current_hour}"
        current_tpm = self.redis.get(tpm_key)
        if current_tpm and int(current_tpm) >= tpm:
            return False, {"error": "Rate limit exceeded (TPM)", "retry_after": 3600 - (now % 3600)}
        
        # Check daily cap
        daily_key = f"daily:{key_id}:{current_day}"
        current_daily = self.redis.get(daily_key)
        if current_daily and int(current_daily) >= daily_cap:
            return False, {"error": "Daily cap exceeded", "retry_after": 86400 - (now % 86400)}
        
        return True, {}
    
    def increment_usage(self, key_id: str, tokens: int):
        """Increment usage counters"""
        now = int(time.time())
        current_hour = now - (now % 3600)
        current_day = now - (now % 86400)
        
        # Increment RPM
        rpm_key = f"rpm:{key_id}:{current_hour}"
        self.redis.incr(rpm_key)
        self.redis.expire(rpm_key, 3600)
        
        # Increment TPM
        tpm_key = f"tpm:{key_id}:{current_hour}"
        self.redis.incrby(tpm_key, tokens)
        self.redis.expire(tpm_key, 3600)
        
        # Increment daily
        daily_key = f"daily:{key_id}:{current_day}"
        self.redis.incrby(daily_key, tokens)
        self.redis.expire(daily_key, 86400)
    
    def get_usage_stats(self, key_id: str) -> dict:
        """Get current usage statistics"""
        now = int(time.time())
        current_hour = now - (now % 3600)
        current_day = now - (now % 86400)
        
        rpm_key = f"rpm:{key_id}:{current_hour}"
        tpm_key = f"tpm:{key_id}:{current_hour}"
        daily_key = f"daily:{key_id}:{current_day}"
        
        return {
            "current_rpm": int(self.redis.get(rpm_key) or 0),
            "current_tpm": int(self.redis.get(tpm_key) or 0),
            "current_daily": int(self.redis.get(daily_key) or 0)
        }
