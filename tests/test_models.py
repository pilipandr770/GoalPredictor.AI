"""Tests for data models."""

import pytest
from datetime import datetime, timedelta

from src.models.user import User, SubscriptionTier
from src.models.match import Match, League
from src.models.prediction import Prediction, PredictionExplanation


class TestUser:
    """Test User model."""
    
    def test_free_user_has_3_prediction_limit(self):
        """Test that free users have 3 predictions per day."""
        user = User(
            email="test@example.com",
            username="testuser",
            subscription_tier=SubscriptionTier.FREE
        )
        assert user.daily_prediction_limit == 3
    
    def test_premium_user_has_unlimited_predictions(self):
        """Test that premium users have unlimited predictions."""
        user = User(
            email="premium@example.com",
            username="premiumuser",
            subscription_tier=SubscriptionTier.PREMIUM,
            subscription_expires_at=datetime.utcnow() + timedelta(days=30)
        )
        assert user.is_premium is True
    
    def test_expired_premium_is_not_premium(self):
        """Test that expired premium subscription is not active."""
        user = User(
            email="expired@example.com",
            username="expireduser",
            subscription_tier=SubscriptionTier.PREMIUM,
            subscription_expires_at=datetime.utcnow() - timedelta(days=1)
        )
        assert user.is_premium is False
    
    def test_can_access_prediction_when_under_limit(self):
        """Test that user can access prediction when under limit."""
        user = User(
            email="test@example.com",
            username="testuser",
            daily_predictions_used=2
        )
        assert user.can_access_prediction() is True
    
    def test_cannot_access_prediction_when_at_limit(self):
        """Test that free user cannot access prediction when at limit."""
        user = User(
            email="test@example.com",
            username="testuser",
            daily_predictions_used=3
        )
        assert user.can_access_prediction() is False
    
    def test_use_prediction_increments_counter(self):
        """Test that using a prediction increments the counter."""
        user = User(
            email="test@example.com",
            username="testuser",
            daily_predictions_used=0
        )
        assert user.use_prediction() is True
        assert user.daily_predictions_used == 1


class TestMatch:
    """Test Match model."""
    
    def test_match_creation(self):
        """Test creating a match."""
        match = Match(
            external_id="test_123",
            league=League.PREMIER_LEAGUE,
            home_team="Manchester City",
            away_team="Arsenal",
            match_date=datetime.utcnow()
        )
        assert match.league == League.PREMIER_LEAGUE
        assert match.status == "scheduled"
    
    def test_is_finished(self):
        """Test match finished status."""
        match = Match(
            external_id="test_123",
            league=League.PREMIER_LEAGUE,
            home_team="Team A",
            away_team="Team B",
            match_date=datetime.utcnow(),
            status="finished",
            home_score=2,
            away_score=1
        )
        assert match.is_finished is True
        assert match.total_goals == 3


class TestPrediction:
    """Test Prediction model."""
    
    def test_prediction_creation(self):
        """Test creating a prediction."""
        prediction = Prediction(
            match_id=1,
            prediction_type="over_2.5",
            predicted_outcome="Yes",
            confidence=0.75
        )
        assert prediction.confidence == 0.75
        assert prediction.confidence_percentage == 75.0
    
    def test_add_explanation(self):
        """Test adding explanation to prediction."""
        prediction = Prediction(
            match_id=1,
            prediction_type="btts",
            predicted_outcome="Yes",
            confidence=0.80
        )
        prediction.add_explanation(
            factor="Recent Form",
            description="Both teams scored in 70% of recent matches",
            confidence=0.7
        )
        assert len(prediction.explanations) == 1
        assert prediction.explanations[0].factor == "Recent Form"
