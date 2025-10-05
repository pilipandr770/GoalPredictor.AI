"""User service for managing users and subscriptions."""

from datetime import datetime, timedelta
from typing import Optional
import logging

from src.models.user import User, SubscriptionTier

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing users and their subscriptions."""
    
    def __init__(self):
        """Initialize user service."""
        # In production, this would use a database
        self._users = {}  # user_id -> User
    
    def create_user(
        self, 
        email: str, 
        username: str,
        subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    ) -> User:
        """Create a new user.
        
        Args:
            email: User email
            username: Username
            subscription_tier: Subscription tier (default: FREE)
            
        Returns:
            Created user
        """
        user = User(
            id=len(self._users) + 1,
            email=email,
            username=username,
            subscription_tier=subscription_tier
        )
        self._users[user.id] = user
        logger.info(f"Created user: {username} (ID: {user.id})")
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        return self._users.get(user_id)
    
    def upgrade_to_premium(
        self, 
        user_id: int, 
        duration_months: int = 1
    ) -> bool:
        """Upgrade user to premium subscription.
        
        Args:
            user_id: User ID
            duration_months: Subscription duration in months
            
        Returns:
            True if successful, False otherwise
        """
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return False
        
        user.subscription_tier = SubscriptionTier.PREMIUM
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30 * duration_months)
        logger.info(
            f"Upgraded user {user.username} to premium until "
            f"{user.subscription_expires_at.strftime('%Y-%m-%d')}"
        )
        return True
    
    def check_and_reset_daily_limits(self):
        """Reset daily prediction limits for all users (called daily at midnight)."""
        for user in self._users.values():
            user.reset_daily_usage()
        logger.info("Reset daily usage limits for all users")
    
    def can_access_prediction(self, user_id: int) -> tuple[bool, str]:
        """Check if user can access a prediction.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (can_access, message)
        """
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        if user.can_access_prediction():
            return True, "Access granted"
        
        remaining = 3 - user.daily_predictions_used
        return False, (
            f"Daily limit reached. You have used {user.daily_predictions_used}/3 "
            f"free predictions today. Upgrade to premium for unlimited access."
        )
    
    def record_prediction_access(self, user_id: int) -> bool:
        """Record that user accessed a prediction.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        return user.use_prediction()
