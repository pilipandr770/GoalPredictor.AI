"""Service for fetching football match data from external APIs."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

import httpx
from src.models.match import Match, League

logger = logging.getLogger(__name__)


class FootballDataService:
    """Service to fetch football data from external APIs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize football data service.
        
        Args:
            api_key: API key for football data provider (e.g., football-data.org)
        """
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {}
        if api_key:
            self.headers["X-Auth-Token"] = api_key
    
    async def get_upcoming_matches(
        self, 
        league: Optional[League] = None,
        days: int = 7
    ) -> List[Match]:
        """Get upcoming matches for specified league(s).
        
        Args:
            league: Specific league to filter by, or None for all leagues
            days: Number of days ahead to fetch matches
            
        Returns:
            List of upcoming matches
        """
        leagues_to_fetch = [league] if league else list(League)
        all_matches = []
        
        for lg in leagues_to_fetch:
            matches = await self._fetch_league_matches(lg, days)
            all_matches.extend(matches)
        
        return all_matches
    
    async def _fetch_league_matches(
        self, 
        league: League, 
        days: int
    ) -> List[Match]:
        """Fetch matches for a specific league.
        
        In production, this would call an external API like:
        - football-data.org
        - API-Football (RapidAPI)
        - TheSportsDB
        
        For now, returns mock data for demonstration.
        """
        # Mock data for demonstration
        logger.info(f"Fetching matches for {league.value}")
        
        # In production, you would make actual API calls:
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{self.base_url}/competitions/{competition_id}/matches",
        #         headers=self.headers
        #     )
        #     data = response.json()
        
        # For now, return sample data
        return self._generate_mock_matches(league, days)
    
    def _generate_mock_matches(self, league: League, days: int) -> List[Match]:
        """Generate mock matches for demonstration."""
        teams_by_league = {
            League.PREMIER_LEAGUE: [
                "Manchester City", "Arsenal", "Liverpool", "Chelsea",
                "Manchester United", "Tottenham", "Newcastle", "Brighton"
            ],
            League.LA_LIGA: [
                "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla",
                "Real Sociedad", "Real Betis", "Villarreal", "Valencia"
            ],
            League.BUNDESLIGA: [
                "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen",
                "Union Berlin", "Freiburg", "Eintracht Frankfurt", "Wolfsburg"
            ],
            League.SERIE_A: [
                "Inter Milan", "AC Milan", "Juventus", "Napoli",
                "Lazio", "Roma", "Atalanta", "Fiorentina"
            ],
            League.LIGUE_1: [
                "PSG", "Monaco", "Marseille", "Lens",
                "Lille", "Lyon", "Nice", "Rennes"
            ],
        }
        
        teams = teams_by_league.get(league, [])
        matches = []
        
        # Generate 4 matches for each league
        for i in range(min(4, len(teams) // 2)):
            match_date = datetime.utcnow() + timedelta(days=i % days)
            home_idx = i * 2
            away_idx = i * 2 + 1
            
            if home_idx < len(teams) and away_idx < len(teams):
                match = Match(
                    external_id=f"{league.value}_{i}_{match_date.strftime('%Y%m%d')}",
                    league=league,
                    home_team=teams[home_idx],
                    away_team=teams[away_idx],
                    match_date=match_date,
                    status="scheduled"
                )
                matches.append(match)
        
        return matches
    
    async def get_team_statistics(
        self, 
        team_name: str, 
        last_n_matches: int = 10
    ) -> Dict[str, Any]:
        """Get statistics for a team's recent matches.
        
        Args:
            team_name: Name of the team
            last_n_matches: Number of recent matches to analyze
            
        Returns:
            Dictionary with team statistics
        """
        # Mock statistics for demonstration
        # In production, fetch from API
        return {
            "team": team_name,
            "matches_analyzed": last_n_matches,
            "goals_scored_avg": 1.8,
            "goals_conceded_avg": 1.2,
            "wins": 6,
            "draws": 2,
            "losses": 2,
            "over_2_5_goals": 7,  # Number of matches with >2.5 goals
            "btts": 5,  # Both teams scored
            "clean_sheets": 3,
        }
    
    async def get_head_to_head(
        self, 
        home_team: str, 
        away_team: str,
        last_n_matches: int = 5
    ) -> Dict[str, Any]:
        """Get head-to-head statistics between two teams.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            last_n_matches: Number of recent h2h matches
            
        Returns:
            Dictionary with h2h statistics
        """
        # Mock h2h data for demonstration
        return {
            "home_team": home_team,
            "away_team": away_team,
            "matches_played": last_n_matches,
            "home_wins": 2,
            "draws": 1,
            "away_wins": 2,
            "avg_goals_per_match": 2.8,
            "over_2_5_goals": 3,
            "btts": 4,
        }
