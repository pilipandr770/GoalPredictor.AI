"""API routes for GoalPredictor.AI."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.models.match import Match, League
from src.models.prediction import Prediction
from src.models.user import User, SubscriptionTier
from src.services.football_data import FootballDataService
from src.services.prediction_engine import PredictionEngine
from src.services.user_service import UserService

router = APIRouter()

# Initialize services (in production, use dependency injection)
football_service = FootballDataService()
prediction_engine = PredictionEngine(football_service)
user_service = UserService()


# Request/Response models
class PredictionRequest(BaseModel):
    """Request for match prediction."""
    match_id: int
    user_id: int
    prediction_types: List[str] = ["over_2.5", "btts", "match_winner"]


class PredictionResponse(BaseModel):
    """Response with predictions."""
    match: Match
    predictions: List[Prediction]
    remaining_daily_predictions: Optional[int] = None


class UserCreateRequest(BaseModel):
    """Request to create user."""
    email: str
    username: str


class SubscriptionUpgradeRequest(BaseModel):
    """Request to upgrade subscription."""
    user_id: int
    duration_months: int = 1


# Endpoints
@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to GoalPredictor.AI",
        "version": "0.1.0",
        "description": "AI-powered football match predictions for top 5 European leagues"
    }


@router.get("/matches", response_model=List[Match])
async def get_matches(
    league: Optional[League] = Query(None, description="Filter by league"),
    days: int = Query(7, ge=1, le=30, description="Number of days ahead")
):
    """Get upcoming matches.
    
    Args:
        league: Optional league filter
        days: Number of days ahead to fetch matches
        
    Returns:
        List of upcoming matches
    """
    matches = await football_service.get_upcoming_matches(league=league, days=days)
    return matches


@router.post("/predictions", response_model=PredictionResponse)
async def get_predictions(request: PredictionRequest):
    """Get AI predictions for a match.
    
    Args:
        request: Prediction request with match_id and user_id
        
    Returns:
        Predictions with explanations
        
    Raises:
        HTTPException: If user limit exceeded or match not found
    """
    # Check user access
    can_access, message = user_service.can_access_prediction(request.user_id)
    if not can_access:
        raise HTTPException(status_code=403, detail=message)
    
    # Get match (in production, fetch from database)
    matches = await football_service.get_upcoming_matches(days=7)
    match = next((m for m in matches if m.id == request.match_id), None)
    
    if not match:
        # For demo purposes, create a mock match if not found
        match = Match(
            id=request.match_id,
            external_id=f"demo_{request.match_id}",
            league=League.PREMIER_LEAGUE,
            home_team="Team A",
            away_team="Team B",
            match_date=datetime.utcnow(),
            status="scheduled"
        )
    
    # Generate predictions
    predictions = []
    for pred_type in request.prediction_types:
        if pred_type == "over_2.5":
            pred = await prediction_engine.predict_over_2_5_goals(match)
        elif pred_type == "btts":
            pred = await prediction_engine.predict_btts(match)
        elif pred_type == "match_winner":
            pred = await prediction_engine.predict_match_winner(match)
        else:
            continue
        predictions.append(pred)
    
    # Record prediction access
    user_service.record_prediction_access(request.user_id)
    
    # Get remaining predictions
    user = user_service.get_user(request.user_id)
    remaining = None if user.is_premium else (3 - user.daily_predictions_used)
    
    return PredictionResponse(
        match=match,
        predictions=predictions,
        remaining_daily_predictions=remaining
    )


@router.post("/users", response_model=User)
async def create_user(request: UserCreateRequest):
    """Create a new user.
    
    Args:
        request: User creation request
        
    Returns:
        Created user
    """
    user = user_service.create_user(
        email=request.email,
        username=request.username
    )
    return user


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/subscription/upgrade")
async def upgrade_subscription(request: SubscriptionUpgradeRequest):
    """Upgrade user to premium subscription.
    
    Args:
        request: Subscription upgrade request
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If upgrade fails
    """
    success = user_service.upgrade_to_premium(
        user_id=request.user_id,
        duration_months=request.duration_months
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to upgrade subscription")
    
    user = user_service.get_user(request.user_id)
    return {
        "message": "Successfully upgraded to premium",
        "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None
    }


@router.get("/leagues")
async def get_leagues():
    """Get list of supported leagues.
    
    Returns:
        List of supported leagues
    """
    return {
        "leagues": [
            {
                "id": league.value,
                "name": league.value.replace("_", " ").title(),
                "country": {
                    League.PREMIER_LEAGUE: "England",
                    League.LA_LIGA: "Spain",
                    League.BUNDESLIGA: "Germany",
                    League.SERIE_A: "Italy",
                    League.LIGUE_1: "France",
                }[league]
            }
            for league in League
        ]
    }
