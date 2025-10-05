"""Tests for services."""

import pytest
from datetime import datetime

from src.models.match import Match, League
from src.models.user import SubscriptionTier
from src.services.football_data import FootballDataService
from src.services.prediction_engine import PredictionEngine
from src.services.user_service import UserService


class TestFootballDataService:
    """Test FootballDataService."""
    
    @pytest.mark.asyncio
    async def test_get_upcoming_matches(self):
        """Test fetching upcoming matches."""
        service = FootballDataService()
        matches = await service.get_upcoming_matches(days=7)
        assert len(matches) > 0
        assert all(isinstance(m, Match) for m in matches)
    
    @pytest.mark.asyncio
    async def test_get_team_statistics(self):
        """Test fetching team statistics."""
        service = FootballDataService()
        stats = await service.get_team_statistics("Manchester City")
        assert "goals_scored_avg" in stats
        assert "goals_conceded_avg" in stats
        assert "wins" in stats


class TestPredictionEngine:
    """Test PredictionEngine."""
    
    @pytest.mark.asyncio
    async def test_predict_over_2_5_goals(self):
        """Test over 2.5 goals prediction."""
        football_service = FootballDataService()
        engine = PredictionEngine(football_service)
        
        match = Match(
            external_id="test_123",
            league=League.PREMIER_LEAGUE,
            home_team="Manchester City",
            away_team="Liverpool",
            match_date=datetime.utcnow()
        )
        
        prediction = await engine.predict_over_2_5_goals(match)
        assert prediction.prediction_type == "over_2.5"
        assert prediction.predicted_outcome in ["Yes", "No"]
        assert 0.0 <= prediction.confidence <= 1.0
        assert len(prediction.explanations) > 0
    
    @pytest.mark.asyncio
    async def test_predict_btts(self):
        """Test BTTS prediction."""
        football_service = FootballDataService()
        engine = PredictionEngine(football_service)
        
        match = Match(
            external_id="test_123",
            league=League.LA_LIGA,
            home_team="Barcelona",
            away_team="Real Madrid",
            match_date=datetime.utcnow()
        )
        
        prediction = await engine.predict_btts(match)
        assert prediction.prediction_type == "btts"
        assert prediction.predicted_outcome in ["Yes", "No"]
        assert len(prediction.explanations) > 0


class TestUserService:
    """Test UserService."""
    
    def test_create_user(self):
        """Test creating a user."""
        service = UserService()
        user = service.create_user(
            email="test@example.com",
            username="testuser"
        )
        assert user.email == "test@example.com"
        assert user.subscription_tier == SubscriptionTier.FREE
    
    def test_upgrade_to_premium(self):
        """Test upgrading user to premium."""
        service = UserService()
        user = service.create_user(
            email="test@example.com",
            username="testuser"
        )
        
        success = service.upgrade_to_premium(user.id, duration_months=1)
        assert success is True
        
        updated_user = service.get_user(user.id)
        assert updated_user.subscription_tier == SubscriptionTier.PREMIUM
        assert updated_user.is_premium is True
    
    def test_can_access_prediction(self):
        """Test checking prediction access."""
        service = UserService()
        user = service.create_user(
            email="test@example.com",
            username="testuser"
        )
        
        can_access, message = service.can_access_prediction(user.id)
        assert can_access is True
        
        # Use all free predictions
        for _ in range(3):
            service.record_prediction_access(user.id)
        
        can_access, message = service.can_access_prediction(user.id)
        assert can_access is False
        assert "limit reached" in message.lower()
