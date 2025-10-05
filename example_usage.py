"""Example usage of GoalPredictor.AI API."""

import asyncio
from datetime import datetime

from src.models.match import Match, League
from src.services.football_data import FootballDataService
from src.services.prediction_engine import PredictionEngine
from src.services.user_service import UserService


async def main():
    """Demonstrate GoalPredictor.AI functionality."""
    print("=" * 60)
    print("GoalPredictor.AI - Example Usage")
    print("=" * 60)
    
    # Initialize services
    football_service = FootballDataService()
    prediction_engine = PredictionEngine(football_service)
    user_service = UserService()
    
    # Create a user
    print("\n1. Creating a new user...")
    user = user_service.create_user(
        email="demo@goalpredictor.ai",
        username="demo_user"
    )
    print(f"   ✓ User created: {user.username}")
    print(f"   - Subscription: {user.subscription_tier.value}")
    print(f"   - Daily limit: {user.daily_prediction_limit} predictions")
    
    # Get upcoming matches
    print("\n2. Fetching upcoming matches...")
    matches = await football_service.get_upcoming_matches(
        league=League.PREMIER_LEAGUE,
        days=7
    )
    print(f"   ✓ Found {len(matches)} upcoming matches")
    
    if matches:
        match = matches[0]
        match.id = 1  # Assign ID for demo
        print(f"\n3. Selected match for prediction:")
        print(f"   {match.home_team} vs {match.away_team}")
        print(f"   League: {match.league.value}")
        print(f"   Date: {match.match_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Check user access
        print("\n4. Checking user access...")
        can_access, message = user_service.can_access_prediction(user.id)
        if can_access:
            print(f"   ✓ {message}")
        else:
            print(f"   ✗ {message}")
            return
        
        # Generate predictions
        print("\n5. Generating AI predictions...")
        
        # Over 2.5 Goals
        print("\n   a) Over 2.5 Goals Prediction:")
        over_pred = await prediction_engine.predict_over_2_5_goals(match)
        print(f"      Prediction: {over_pred.predicted_outcome}")
        print(f"      Confidence: {over_pred.confidence_percentage:.1f}%")
        print(f"      Explanations:")
        for exp in over_pred.explanations:
            print(f"        • {exp.factor}: {exp.description[:80]}...")
        
        # BTTS
        print("\n   b) Both Teams To Score (BTTS):")
        btts_pred = await prediction_engine.predict_btts(match)
        print(f"      Prediction: {btts_pred.predicted_outcome}")
        print(f"      Confidence: {btts_pred.confidence_percentage:.1f}%")
        print(f"      Explanations:")
        for exp in btts_pred.explanations:
            print(f"        • {exp.factor}: {exp.description[:80]}...")
        
        # Match Winner
        print("\n   c) Match Winner:")
        winner_pred = await prediction_engine.predict_match_winner(match)
        print(f"      Prediction: {winner_pred.predicted_outcome}")
        print(f"      Confidence: {winner_pred.confidence_percentage:.1f}%")
        print(f"      Explanations:")
        for exp in winner_pred.explanations:
            print(f"        • {exp.factor}: {exp.description[:80]}...")
        
        # Record prediction access
        user_service.record_prediction_access(user.id)
        updated_user = user_service.get_user(user.id)
        remaining = 3 - updated_user.daily_predictions_used
        print(f"\n6. Prediction recorded!")
        print(f"   Remaining daily predictions: {remaining}/3")
        
        # Demonstrate premium upgrade
        print("\n7. Upgrading to Premium...")
        success = user_service.upgrade_to_premium(user.id, duration_months=1)
        if success:
            premium_user = user_service.get_user(user.id)
            print(f"   ✓ Successfully upgraded to Premium!")
            print(f"   - Expires: {premium_user.subscription_expires_at.strftime('%Y-%m-%d')}")
            print(f"   - Daily limit: Unlimited")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
