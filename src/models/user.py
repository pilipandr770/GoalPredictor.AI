"""User and subscription models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SubscriptionTier(str, Enum):
    """Subscription tiers for users."""
    
    FREE = "free"
    PREMIUM = "premium"


class User(BaseModel):
    """User model."""
    
    id: Optional[int] = None
    email: EmailStr
    username: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    daily_predictions_used: int = 0
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def daily_prediction_limit(self) -> int:
        """Get daily prediction limit based on subscription tier."""
        if self.subscription_tier == SubscriptionTier.PREMIUM:
            return float('inf')  # Unlimited for premium
        return 3  # Free tier limit
    
    @property
    def is_premium(self) -> bool:
        """Check if user has active premium subscription."""
        if self.subscription_tier != SubscriptionTier.PREMIUM:
            return False
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.utcnow()
    
    def can_access_prediction(self) -> bool:
        """Check if user can access another prediction today."""
        if self.is_premium:
            return True
        return self.daily_predictions_used < 3
    
    def use_prediction(self) -> bool:
        """Record a prediction usage. Returns True if successful."""
        if not self.can_access_prediction():
            return False
        self.daily_predictions_used += 1
        return True
    
    def reset_daily_usage(self):
        """Reset daily prediction counter (called at midnight)."""
        self.daily_predictions_used = 0

    class Config:
        from_attributes = True
