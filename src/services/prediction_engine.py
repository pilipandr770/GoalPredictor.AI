"""AI prediction engine for football matches."""

import logging
from typing import List, Dict, Any

from src.models.match import Match
from src.models.prediction import Prediction, PredictionExplanation
from src.services.football_data import FootballDataService

logger = logging.getLogger(__name__)


class PredictionEngine:
    """AI engine for generating football match predictions."""
    
    def __init__(self, football_service: FootballDataService):
        """Initialize prediction engine.
        
        Args:
            football_service: Service for fetching football data
        """
        self.football_service = football_service
        self.model_version = "1.0.0"
    
    async def predict_over_2_5_goals(self, match: Match) -> Prediction:
        """Predict if match will have over 2.5 goals.
        
        Args:
            match: Match to predict
            
        Returns:
            Prediction with explanations
        """
        # Fetch team statistics
        home_stats = await self.football_service.get_team_statistics(
            match.home_team, last_n_matches=10
        )
        away_stats = await self.football_service.get_team_statistics(
            match.away_team, last_n_matches=10
        )
        h2h_stats = await self.football_service.get_head_to_head(
            match.home_team, match.away_team, last_n_matches=5
        )
        
        # Calculate prediction
        prediction = Prediction(
            match_id=match.id or 0,
            prediction_type="over_2.5",
            predicted_outcome="",
            confidence=0.0,
            model_version=self.model_version
        )
        
        # Analyze factors
        total_score = 0
        max_score = 0
        
        # Factor 1: Recent goals scored by both teams
        home_over_rate = (home_stats["over_2_5_goals"] / home_stats["matches_analyzed"]) * 100
        away_over_rate = (away_stats["over_2_5_goals"] / away_stats["matches_analyzed"]) * 100
        avg_over_rate = (home_over_rate + away_over_rate) / 2
        
        goals_factor_score = min(avg_over_rate / 10, 10)  # 0-10 scale
        total_score += goals_factor_score
        max_score += 10
        
        prediction.add_explanation(
            factor="Recent Goal-Scoring Form",
            description=(
                f"{match.home_team} scored over 2.5 goals in {home_over_rate:.0f}% "
                f"of their last 10 matches, while {match.away_team} did so in "
                f"{away_over_rate:.0f}% of matches. Combined average: {avg_over_rate:.0f}%."
            ),
            confidence=goals_factor_score / 10
        )
        
        # Factor 2: Head-to-head history
        if h2h_stats["matches_played"] > 0:
            h2h_over_rate = (h2h_stats["over_2_5_goals"] / h2h_stats["matches_played"]) * 100
            h2h_score = min(h2h_over_rate / 10, 10)
            total_score += h2h_score
            max_score += 10
            
            prediction.add_explanation(
                factor="Head-to-Head History",
                description=(
                    f"In the last {h2h_stats['matches_played']} meetings between these teams, "
                    f"{h2h_over_rate:.0f}% of matches had over 2.5 goals "
                    f"(average {h2h_stats['avg_goals_per_match']:.1f} goals per match)."
                ),
                confidence=h2h_score / 10
            )
        
        # Factor 3: Combined attacking strength
        combined_attack = home_stats["goals_scored_avg"] + away_stats["goals_scored_avg"]
        attack_score = min(combined_attack * 2, 10)  # 0-10 scale
        total_score += attack_score
        max_score += 10
        
        prediction.add_explanation(
            factor="Attacking Strength",
            description=(
                f"{match.home_team} averages {home_stats['goals_scored_avg']:.1f} goals per match, "
                f"while {match.away_team} averages {away_stats['goals_scored_avg']:.1f} goals. "
                f"Combined attack strength suggests high-scoring potential."
            ),
            confidence=attack_score / 10
        )
        
        # Calculate final confidence
        final_confidence = total_score / max_score if max_score > 0 else 0.5
        prediction.confidence = final_confidence
        
        # Determine predicted outcome
        if final_confidence >= 0.6:
            prediction.predicted_outcome = "Yes"
        else:
            prediction.predicted_outcome = "No"
        
        logger.info(
            f"Predicted over 2.5 goals for {match.home_team} vs {match.away_team}: "
            f"{prediction.predicted_outcome} (confidence: {final_confidence:.2%})"
        )
        
        return prediction
    
    async def predict_btts(self, match: Match) -> Prediction:
        """Predict Both Teams To Score (BTTS).
        
        Args:
            match: Match to predict
            
        Returns:
            Prediction with explanations
        """
        home_stats = await self.football_service.get_team_statistics(
            match.home_team, last_n_matches=10
        )
        away_stats = await self.football_service.get_team_statistics(
            match.away_team, last_n_matches=10
        )
        h2h_stats = await self.football_service.get_head_to_head(
            match.home_team, match.away_team, last_n_matches=5
        )
        
        prediction = Prediction(
            match_id=match.id or 0,
            prediction_type="btts",
            predicted_outcome="",
            confidence=0.0,
            model_version=self.model_version
        )
        
        total_score = 0
        max_score = 0
        
        # Factor 1: Recent BTTS occurrences
        home_btts_rate = (home_stats["btts"] / home_stats["matches_analyzed"]) * 100
        away_btts_rate = (away_stats["btts"] / away_stats["matches_analyzed"]) * 100
        avg_btts_rate = (home_btts_rate + away_btts_rate) / 2
        
        btts_factor_score = min(avg_btts_rate / 10, 10)
        total_score += btts_factor_score
        max_score += 10
        
        prediction.add_explanation(
            factor="Recent BTTS Form",
            description=(
                f"Both teams scored in {home_btts_rate:.0f}% of {match.home_team}'s "
                f"last 10 matches and {away_btts_rate:.0f}% of {match.away_team}'s matches. "
                f"Average: {avg_btts_rate:.0f}%."
            ),
            confidence=btts_factor_score / 10
        )
        
        # Factor 2: Defensive weaknesses
        home_def_weakness = home_stats["goals_conceded_avg"]
        away_def_weakness = away_stats["goals_conceded_avg"]
        combined_def_weakness = (home_def_weakness + away_def_weakness) / 2
        
        def_score = min(combined_def_weakness * 4, 10)
        total_score += def_score
        max_score += 10
        
        prediction.add_explanation(
            factor="Defensive Vulnerability",
            description=(
                f"{match.home_team} concedes an average of {home_def_weakness:.1f} goals, "
                f"while {match.away_team} concedes {away_def_weakness:.1f} goals per match. "
                f"Both defenses show vulnerability."
            ),
            confidence=def_score / 10
        )
        
        # Factor 3: H2H BTTS
        if h2h_stats["matches_played"] > 0:
            h2h_btts_rate = (h2h_stats["btts"] / h2h_stats["matches_played"]) * 100
            h2h_score = min(h2h_btts_rate / 10, 10)
            total_score += h2h_score
            max_score += 10
            
            prediction.add_explanation(
                factor="Head-to-Head BTTS",
                description=(
                    f"Both teams scored in {h2h_btts_rate:.0f}% of their last "
                    f"{h2h_stats['matches_played']} encounters."
                ),
                confidence=h2h_score / 10
            )
        
        final_confidence = total_score / max_score if max_score > 0 else 0.5
        prediction.confidence = final_confidence
        prediction.predicted_outcome = "Yes" if final_confidence >= 0.6 else "No"
        
        return prediction
    
    async def predict_match_winner(self, match: Match) -> Prediction:
        """Predict match winner (Home/Draw/Away).
        
        Args:
            match: Match to predict
            
        Returns:
            Prediction with explanations
        """
        home_stats = await self.football_service.get_team_statistics(
            match.home_team, last_n_matches=10
        )
        away_stats = await self.football_service.get_team_statistics(
            match.away_team, last_n_matches=10
        )
        h2h_stats = await self.football_service.get_head_to_head(
            match.home_team, match.away_team
        )
        
        prediction = Prediction(
            match_id=match.id or 0,
            prediction_type="match_winner",
            predicted_outcome="",
            confidence=0.0,
            model_version=self.model_version
        )
        
        # Calculate form scores
        home_form = (home_stats["wins"] * 3 + home_stats["draws"]) / (home_stats["matches_analyzed"] * 3)
        away_form = (away_stats["wins"] * 3 + away_stats["draws"]) / (away_stats["matches_analyzed"] * 3)
        
        # Home advantage factor
        home_advantage = 0.1  # 10% boost for home team
        
        home_score = home_form + home_advantage
        away_score = away_form
        
        prediction.add_explanation(
            factor="Recent Form",
            description=(
                f"{match.home_team} won {home_stats['wins']} of their last 10 matches, "
                f"while {match.away_team} won {away_stats['wins']}. "
                f"Form advantage: {'Home' if home_score > away_score else 'Away'}."
            ),
            confidence=abs(home_score - away_score)
        )
        
        prediction.add_explanation(
            factor="Home Advantage",
            description=f"{match.home_team} benefits from playing at home (10% advantage factor).",
            confidence=0.7
        )
        
        # Determine outcome
        score_diff = abs(home_score - away_score)
        if score_diff < 0.15:
            prediction.predicted_outcome = "Draw"
            prediction.confidence = 0.55
        elif home_score > away_score:
            prediction.predicted_outcome = "Home"
            prediction.confidence = min(0.5 + score_diff, 0.9)
        else:
            prediction.predicted_outcome = "Away"
            prediction.confidence = min(0.5 + score_diff, 0.9)
        
        return prediction
