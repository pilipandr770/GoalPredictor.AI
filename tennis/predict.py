"""
Tennis Prediction Service
Makes predictions for tennis matches using trained ML model
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TennisPredictionService:
    """Generate predictions for tennis matches"""
    
    def __init__(self, model_path='tennis/models/tennis_player1_win_model.pkl',
                 features_path='tennis/models/tennis_feature_columns.pkl'):
        self.model = None
        self.feature_columns = None
        self.historical_data = None
        
        # Load model
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Tennis model loaded successfully")
            logger.info("✓ Tennis model loaded")
        except Exception as e:
            print(f"❌ Failed to load tennis model: {e}")
            logger.error(f"❌ Failed to load model: {e}")
        
        # Load feature columns
        try:
            with open(features_path, 'rb') as f:
                self.feature_columns = pickle.load(f)
            print(f"✅ Tennis feature columns loaded ({len(self.feature_columns)} features)")
            logger.info(f"✓ Feature columns loaded ({len(self.feature_columns)} features)")
        except Exception as e:
            print(f"❌ Failed to load features: {e}")
            logger.error(f"❌ Failed to load features: {e}")
        
        # Load historical data for stats
        try:
            data_path = Path('tennis/data/atp_matches_combined.csv')
            if data_path.exists():
                self.historical_data = pd.read_csv(data_path)
                self.historical_data['tourney_date'] = pd.to_datetime(
                    self.historical_data['tourney_date'], 
                    format='%Y%m%d'
                )
                logger.info(f"✓ Historical data loaded ({len(self.historical_data)} matches)")
        except Exception as e:
            logger.error(f"⚠️  Historical data not available: {e}")
    
    def predict_match(self, player1_name: str, player1_rank: int,
                     player2_name: str, player2_rank: int,
                     surface: str, tournament_level: str = None) -> Dict:
        """
        Predict match outcome
        
        Args:
            player1_name: Name of player 1
            player1_rank: ATP rank of player 1
            player2_name: Name of player 2
            player2_rank: ATP rank of player 2
            surface: 'Hard', 'Clay', or 'Grass'
            tournament_level: 'G' (Grand Slam), 'M' (Masters), etc.
        
        Returns:
            {
                'player1_win_probability': 0.65,
                'player2_win_probability': 0.35,
                'confidence': 'high',
                'predicted_winner': 'Novak Djokovic',
                'factors': [
                    {'factor': 'Ranking Advantage', 'impact': 'high'},
                    {'factor': 'Surface Performance', 'impact': 'medium'}
                ],
                'explanation': 'Player 1 has a strong advantage...'
            }
        """
        if not self.model or not self.feature_columns:
            return self._fallback_prediction(player1_name, player1_rank, player2_name, player2_rank)
        
        logger.info(f"🎾 Predicting: {player1_name} (#{player1_rank}) vs {player2_name} (#{player2_rank}) on {surface}")
        
        # Extract features
        features = self._extract_features(
            player1_name, player1_rank,
            player2_name, player2_rank,
            surface, tournament_level
        )
        
        # Create feature vector
        X = pd.DataFrame([features])[self.feature_columns].fillna(0)
        
        # Make prediction
        try:
            probability = self.model.predict_proba(X)[0]
            player1_prob = float(probability[1])  # Probability of player1 winning
            player2_prob = float(probability[0])  # Probability of player2 winning
            
            # Confidence
            prob_diff = abs(player1_prob - player2_prob)
            if prob_diff > 0.3:
                confidence = 'high'
            elif prob_diff > 0.15:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            # Winner
            predicted_winner = player1_name if player1_prob > player2_prob else player2_name
            
            # Key factors
            factors = self._identify_factors(features, player1_prob, player2_prob)
            
            # Explanation
            explanation = self._generate_explanation(
                player1_name, player1_rank, player1_prob,
                player2_name, player2_rank, player2_prob,
                surface, factors
            )
            
            result = {
                'player1_win_probability': player1_prob,
                'player2_win_probability': player2_prob,
                'confidence': confidence,
                'predicted_winner': predicted_winner,
                'factors': factors,
                'explanation': explanation
            }
            
            logger.info(f"  ✓ Prediction: {predicted_winner} ({max(player1_prob, player2_prob):.0%})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return self._fallback_prediction(player1_name, player1_rank, player2_name, player2_rank)
    
    def _extract_features(self, player1_name: str, player1_rank: int,
                         player2_name: str, player2_rank: int,
                         surface: str, tournament_level: str = None) -> Dict:
        """Extract features for prediction"""
        
        # Basic features
        features = {
            'player1_rank': player1_rank if player1_rank else 999,
            'player2_rank': player2_rank if player2_rank else 999,
            'rank_difference': player1_rank - player2_rank if player1_rank and player2_rank else 0,
        }
        
        # Try to get historical stats
        if self.historical_data is not None:
            # Player 1 form
            p1_form = self._get_player_form(player1_name)
            features['player1_recent_wins'] = p1_form['wins']
            features['player1_recent_losses'] = p1_form['losses']
            features['player1_form_points'] = p1_form['points']
            
            # Player 2 form
            p2_form = self._get_player_form(player2_name)
            features['player2_recent_wins'] = p2_form['wins']
            features['player2_recent_losses'] = p2_form['losses']
            features['player2_form_points'] = p2_form['points']
            
            features['form_difference'] = p1_form['points'] - p2_form['points']
            
            # H2H
            h2h = self._get_h2h(player1_name, player2_name)
            features['h2h_player1_wins'] = h2h['player1_wins']
            features['h2h_player2_wins'] = h2h['player2_wins']
            features['h2h_total'] = h2h['total']
            
            # Surface stats
            p1_surface = self._get_surface_stats(player1_name, surface)
            features['player1_surface_wins'] = p1_surface['wins']
            features['player1_surface_total'] = p1_surface['total']
            features['player1_surface_winrate'] = p1_surface['winrate']
            
            p2_surface = self._get_surface_stats(player2_name, surface)
            features['player2_surface_wins'] = p2_surface['wins']
            features['player2_surface_total'] = p2_surface['total']
            features['player2_surface_winrate'] = p2_surface['winrate']
            
            features['surface_winrate_diff'] = p1_surface['winrate'] - p2_surface['winrate']
        else:
            # Default values if no historical data
            features.update({
                'player1_recent_wins': 5, 'player1_recent_losses': 5, 'player1_form_points': 15,
                'player2_recent_wins': 5, 'player2_recent_losses': 5, 'player2_form_points': 15,
                'form_difference': 0,
                'h2h_player1_wins': 0, 'h2h_player2_wins': 0, 'h2h_total': 0,
                'player1_surface_wins': 10, 'player1_surface_total': 20, 'player1_surface_winrate': 0.5,
                'player2_surface_wins': 10, 'player2_surface_total': 20, 'player2_surface_winrate': 0.5,
                'surface_winrate_diff': 0
            })
        
        # Surface one-hot
        features['is_hard'] = 1 if surface == 'Hard' else 0
        features['is_clay'] = 1 if surface == 'Clay' else 0
        features['is_grass'] = 1 if surface == 'Grass' else 0
        
        # Tournament level
        features['is_grand_slam'] = 1 if tournament_level == 'G' else 0
        features['is_masters'] = 1 if tournament_level == 'M' else 0
        
        return features
    
    def _get_player_form(self, player_name: str, window: int = 10) -> Dict:
        """Get player's recent form"""
        if self.historical_data is None:
            return {'wins': 5, 'losses': 5, 'points': 15}
        
        recent_cutoff = datetime.now() - timedelta(days=180)
        
        player_matches = self.historical_data[
            (self.historical_data['tourney_date'] >= recent_cutoff) &
            ((self.historical_data['winner_name'] == player_name) | 
             (self.historical_data['loser_name'] == player_name))
        ].tail(window)
        
        if len(player_matches) == 0:
            return {'wins': 5, 'losses': 5, 'points': 15}
        
        wins = (player_matches['winner_name'] == player_name).sum()
        losses = len(player_matches) - wins
        points = wins * 3
        
        return {'wins': int(wins), 'losses': int(losses), 'points': int(points)}
    
    def _get_h2h(self, player1_name: str, player2_name: str) -> Dict:
        """Get head-to-head statistics"""
        if self.historical_data is None:
            return {'player1_wins': 0, 'player2_wins': 0, 'total': 0}
        
        h2h_matches = self.historical_data[
            ((self.historical_data['winner_name'] == player1_name) & 
             (self.historical_data['loser_name'] == player2_name)) |
            ((self.historical_data['winner_name'] == player2_name) & 
             (self.historical_data['loser_name'] == player1_name))
        ]
        
        player1_wins = ((h2h_matches['winner_name'] == player1_name)).sum()
        player2_wins = len(h2h_matches) - player1_wins
        
        return {
            'player1_wins': int(player1_wins),
            'player2_wins': int(player2_wins),
            'total': len(h2h_matches)
        }
    
    def _get_surface_stats(self, player_name: str, surface: str) -> Dict:
        """Get player statistics on specific surface"""
        if self.historical_data is None:
            return {'wins': 10, 'total': 20, 'winrate': 0.5}
        
        surface_matches = self.historical_data[
            (self.historical_data['surface'] == surface) &
            ((self.historical_data['winner_name'] == player_name) | 
             (self.historical_data['loser_name'] == player_name))
        ]
        
        if len(surface_matches) == 0:
            return {'wins': 10, 'total': 20, 'winrate': 0.5}
        
        wins = (surface_matches['winner_name'] == player_name).sum()
        total = len(surface_matches)
        winrate = wins / total if total > 0 else 0.5
        
        return {'wins': int(wins), 'total': int(total), 'winrate': float(winrate)}
    
    def _identify_factors(self, features: Dict, p1_prob: float, p2_prob: float) -> list:
        """Identify key factors influencing the prediction"""
        factors = []
        
        # Ranking
        rank_diff = features['rank_difference']
        if abs(rank_diff) > 20:
            factors.append({
                'factor': 'Große Ranking-Differenz',
                'impact': 'high' if abs(rank_diff) > 50 else 'medium',
                'description': f"Rang {abs(rank_diff)} Unterschied"
            })
        
        # Surface
        surface_diff = features.get('surface_winrate_diff', 0)
        if abs(surface_diff) > 0.1:
            factors.append({
                'factor': 'Belagleistung',
                'impact': 'medium',
                'description': f"{abs(surface_diff)*100:.0f}% bessere Leistung auf diesem Belag"
            })
        
        # Form
        form_diff = features.get('form_difference', 0)
        if abs(form_diff) > 10:
            factors.append({
                'factor': 'Aktuelle Form',
                'impact': 'medium',
                'description': f"{abs(form_diff)} Punkte Vorteil in letzten 10 Spielen"
            })
        
        # H2H
        h2h_total = features.get('h2h_total', 0)
        if h2h_total > 3:
            h2h_p1 = features.get('h2h_player1_wins', 0)
            h2h_p2 = features.get('h2h_player2_wins', 0)
            if h2h_p1 > h2h_p2 * 1.5:
                factors.append({
                    'factor': 'Head-to-Head Vorteil',
                    'impact': 'medium',
                    'description': f"{h2h_p1}-{h2h_p2} in direkten Duellen"
                })
        
        return factors[:3]  # Top 3
    
    def _generate_explanation(self, p1_name: str, p1_rank: int, p1_prob: float,
                             p2_name: str, p2_rank: int, p2_prob: float,
                             surface: str, factors: list) -> str:
        """Generate German explanation"""
        winner = p1_name if p1_prob > p2_prob else p2_name
        win_prob = max(p1_prob, p2_prob)
        
        explanation = f"{winner} hat eine {win_prob:.0%} Wahrscheinlichkeit zu gewinnen. "
        
        # Ranking
        if p1_rank < p2_rank:
            explanation += f"{p1_name} ist höher platziert (#{p1_rank} vs #{p2_rank}). "
        elif p2_rank < p1_rank:
            explanation += f"{p2_name} ist höher platziert (#{p2_rank} vs #{p1_rank}). "
        
        # Surface
        explanation += f"Das Spiel findet auf {surface} statt. "
        
        # Key factors
        if factors:
            explanation += "Hauptfaktoren: " + ", ".join([f['factor'] for f in factors]) + "."
        
        return explanation
    
    def _fallback_prediction(self, p1_name: str, p1_rank: int, 
                           p2_name: str, p2_rank: int) -> Dict:
        """Simple fallback based on ranking only"""
        # Simple Elo-like calculation
        rank_diff = p2_rank - p1_rank  # Positive if p1 is better ranked
        
        # Convert rank difference to probability
        # Better ranked player has advantage
        p1_prob = 1 / (1 + 10 ** (-rank_diff / 100))
        p2_prob = 1 - p1_prob
        
        winner = p1_name if p1_prob > p2_prob else p2_name
        
        return {
            'player1_win_probability': p1_prob,
            'player2_win_probability': p2_prob,
            'confidence': 'medium',
            'predicted_winner': winner,
            'factors': [
                {'factor': 'ATP Ranking', 'impact': 'high', 
                 'description': f"#{p1_rank} vs #{p2_rank}"}
            ],
            'explanation': f"{winner} ist favorisiert basierend auf ATP Ranking."
        }


# Global instance
_tennis_prediction_service = None


def get_tennis_prediction_service() -> TennisPredictionService:
    """Get singleton instance"""
    global _tennis_prediction_service
    if _tennis_prediction_service is None:
        _tennis_prediction_service = TennisPredictionService()
    return _tennis_prediction_service
