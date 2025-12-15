"""
Rate Limiting and Usage Tracking for Binah-Σ

Features:
- Tier-based rate limiting
- Usage tracking (minute/day/month)
- In-memory storage (replace with Redis/DB for production)
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
from fastapi import HTTPException
from auth import TierLimits


class UsageTracker:
    """Track API usage per customer"""

    def __init__(self):
        # In-memory storage: {customer_id: {period: count}}
        # For production: use Redis or PostgreSQL
        self.usage = defaultdict(lambda: defaultdict(int))
        self.last_request = defaultdict(lambda: defaultdict(datetime))

    def _get_period_key(self, period: str) -> str:
        """Get period key for current time"""
        now = datetime.utcnow()

        if period == "minute":
            return now.strftime("%Y-%m-%d %H:%M")
        elif period == "hour":
            return now.strftime("%Y-%m-%d %H")
        elif period == "day":
            return now.strftime("%Y-%m-%d")
        elif period == "month":
            return now.strftime("%Y-%m")
        else:
            raise ValueError(f"Invalid period: {period}")

    def record_request(self, customer_id: str):
        """Record a request for a customer"""
        periods = ["minute", "day", "month"]

        for period in periods:
            key = f"{period}:{self._get_period_key(period)}"
            self.usage[customer_id][key] += 1

        # Record timestamp
        self.last_request[customer_id]["last"] = datetime.utcnow()

    def get_usage(self, customer_id: str, period: str) -> int:
        """
        Get usage count for a customer in a period.

        Args:
            customer_id: Customer ID
            period: "minute", "day", or "month"

        Returns:
            int: Number of requests in current period
        """
        key = f"{period}:{self._get_period_key(period)}"
        return self.usage[customer_id].get(key, 0)

    def check_limit(self, customer_id: str, tier: str) -> tuple[bool, dict]:
        """
        Check if customer is within tier limits.

        Args:
            customer_id: Customer ID
            tier: Subscription tier

        Returns:
            tuple: (is_within_limit, usage_info)
        """
        usage_info = {
            "minute": self.get_usage(customer_id, "minute"),
            "day": self.get_usage(customer_id, "day"),
            "month": self.get_usage(customer_id, "month"),
            "limits": {
                "minute": TierLimits.get_limit(tier, "requests_per_minute"),
                "day": TierLimits.get_limit(tier, "requests_per_day"),
                "month": TierLimits.get_limit(tier, "requests_per_month")
            }
        }

        # Check each period
        for period in ["minute", "day", "month"]:
            limit = usage_info["limits"][period]
            current = usage_info[period]

            if current >= limit:
                return False, usage_info

        return True, usage_info

    def get_customer_stats(self, customer_id: str) -> dict:
        """Get detailed statistics for a customer"""
        return {
            "current_usage": {
                "minute": self.get_usage(customer_id, "minute"),
                "day": self.get_usage(customer_id, "day"),
                "month": self.get_usage(customer_id, "month")
            },
            "last_request": self.last_request[customer_id].get("last"),
            "total_periods_active": len(self.usage[customer_id])
        }

    def reset_usage(self, customer_id: str, period: str = "all"):
        """Reset usage for a customer (admin function)"""
        if period == "all":
            self.usage[customer_id].clear()
        else:
            key = f"{period}:{self._get_period_key(period)}"
            self.usage[customer_id][key] = 0


# Global instance
usage_tracker = UsageTracker()


class RateLimiter:
    """Rate limiting middleware"""

    def __init__(self, usage_tracker: UsageTracker):
        self.tracker = usage_tracker

    async def check_rate_limit(self, customer_id: str, tier: str) -> dict:
        """
        Check rate limit for a customer.

        Args:
            customer_id: Customer ID
            tier: Subscription tier

        Returns:
            dict: Usage information

        Raises:
            HTTPException: If rate limit exceeded
        """
        within_limit, usage_info = self.tracker.check_limit(customer_id, tier)

        if not within_limit:
            # Determine which limit was exceeded
            exceeded_period = None
            for period in ["minute", "day", "month"]:
                if usage_info[period] >= usage_info["limits"][period]:
                    exceeded_period = period
                    break

            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "period": exceeded_period,
                    "current_usage": usage_info[exceeded_period],
                    "limit": usage_info["limits"][exceeded_period],
                    "tier": tier,
                    "upgrade_message": f"Upgrade to a higher tier for more requests" if tier != "enterprise" else None
                },
                headers={
                    "X-RateLimit-Limit": str(usage_info["limits"][exceeded_period]),
                    "X-RateLimit-Remaining": str(max(0, usage_info["limits"][exceeded_period] - usage_info[exceeded_period])),
                    "X-RateLimit-Reset": self._get_reset_time(exceeded_period)
                }
            )

        return usage_info

    def _get_reset_time(self, period: str) -> str:
        """Get time when rate limit resets"""
        now = datetime.utcnow()

        if period == "minute":
            reset = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        elif period == "day":
            reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif period == "month":
            # Next month
            if now.month == 12:
                reset = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                reset = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            reset = now + timedelta(hours=1)

        return reset.isoformat()


# Global rate limiter
rate_limiter = RateLimiter(usage_tracker)
