"""Prediction models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PredictionExplanation(BaseModel):
    """Explanation for a prediction."""
    
    factor: str  # e.g., "Recent form", "Head-to-head", "Goals statistics"
    description: str  # Human-readable explanation
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    
    class Config:
        from_attributes = True


class Prediction(BaseModel):
    """Match prediction model."""
    
    id: Optional[int] = None
    match_id: int
    prediction_type: str  # e.g., "over_2.5", "btts", "home_win"
    predicted_outcome: str  # e.g., "Yes", "No", "Home", "Draw", "Away"
    confidence: float = Field(ge=0.0, le=1.0)  # Overall confidence
    explanations: List[PredictionExplanation] = []
    model_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional: actual outcome (filled after match)
    actual_outcome: Optional[str] = None
    is_correct: Optional[bool] = None
    
    @property
    def confidence_percentage(self) -> float:
        """Get confidence as percentage."""
        return self.confidence * 100
    
    def add_explanation(
        self, 
        factor: str, 
        description: str, 
        confidence: float
    ):
        """Add an explanation to the prediction."""
        self.explanations.append(
            PredictionExplanation(
                factor=factor,
                description=description,
                confidence=confidence
            )
        )
    
    class Config:
        from_attributes = True
