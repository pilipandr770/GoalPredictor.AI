"""Match and league models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class League(str, Enum):
    """Top 5 European football leagues."""
    
    PREMIER_LEAGUE = "premier_league"  # England
    LA_LIGA = "la_liga"  # Spain
    BUNDESLIGA = "bundesliga"  # Germany
    SERIE_A = "serie_a"  # Italy
    LIGUE_1 = "ligue_1"  # France


class Match(BaseModel):
    """Football match model."""
    
    id: Optional[int] = None
    external_id: str  # ID from external API
    league: League
    home_team: str
    away_team: str
    match_date: datetime
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "scheduled"  # scheduled, live, finished
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def is_finished(self) -> bool:
        """Check if match is finished."""
        return self.status == "finished"
    
    @property
    def total_goals(self) -> Optional[int]:
        """Get total goals scored in match."""
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score + self.away_score

    class Config:
        from_attributes = True
