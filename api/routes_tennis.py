"""
Tennis API Routes
Endpoints for tennis matches and predictions
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from services.tennis_api import get_tennis_api_service
from tennis.predict import get_tennis_prediction_service
import logging

logger = logging.getLogger(__name__)

tennis_bp = Blueprint('tennis', __name__, url_prefix='/api/tennis')


@tennis_bp.route('/matches', methods=['GET'])
def get_matches():
    """
    Get upcoming tennis matches
    
    Query params:
        days: int - Number of days to look ahead (default: 7)
    
    Returns:
        {
            'success': True,
            'matches': [
                {
                    'id': 'match_123',
                    'date': '2025-10-12T14:00:00',
                    'tournament': 'ATP Paris Masters',
                    'round': 'Quarterfinal',
                    'surface': 'Hard',
                    'player1': {
                        'name': 'Novak Djokovic',
                        'rank': 1,
                        'country': 'SRB'
                    },
                    'player2': {
                        'name': 'Carlos Alcaraz',
                        'rank': 2,
                        'country': 'ESP'
                    }
                }
            ],
            'count': 10
        }
    """
    try:
        days = int(request.args.get('days', 7))
        days = min(days, 14)  # Max 14 days
        
        logger.info(f"🎾 Fetching tennis matches for next {days} days...")
        
        # Get matches from API
        tennis_api = get_tennis_api_service()
        matches = tennis_api.get_upcoming_matches(days=days)
        
        # Format for frontend
        formatted_matches = []
        for match in matches:
            formatted = {
                'id': match['id'],
                'date': match['date'].isoformat(),
                'tournament': match['tournament'],
                'round': match['round'],
                'surface': match['surface'],
                'status': match.get('status', 'Scheduled'),
                'player1': {
                    'name': match['player1']['name'],
                    'rank': match['player1']['rank'],
                    'country': match['player1'].get('country', '')
                },
                'player2': {
                    'name': match['player2']['name'],
                    'rank': match['player2']['rank'],
                    'country': match['player2'].get('country', '')
                }
            }
            formatted_matches.append(formatted)
        
        # Sort by date
        formatted_matches.sort(key=lambda x: x['date'])
        
        logger.info(f"  ✓ Returning {len(formatted_matches)} matches")
        
        return jsonify({
            'success': True,
            'matches': formatted_matches,
            'count': len(formatted_matches)
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching matches: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tennis_bp.route('/predictions/<match_id>', methods=['GET'])
@login_required
def get_prediction(match_id):
    """
    Get prediction for a specific match
    
    Path params:
        match_id: str - Match ID
    
    Returns:
        {
            'success': True,
            'prediction': {
                'match_id': 'match_123',
                'player1_win_probability': 0.65,
                'player2_win_probability': 0.35,
                'predicted_winner': 'Novak Djokovic',
                'confidence': 'high',
                'explanation': 'Djokovic hat einen Vorteil...',
                'factors': [
                    {
                        'factor': 'Ranking Advantage',
                        'impact': 'high',
                        'description': 'Rang 50 Unterschied'
                    }
                ]
            },
            'is_premium': True
        }
    """
    try:
        # Check if user is premium
        if not current_user.is_premium and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Premium subscription required for tennis predictions',
                'requires_premium': True
            }), 403
        
        logger.info(f"🎾 Generating prediction for match {match_id}...")
        
        # Get match details
        tennis_api = get_tennis_api_service()
        matches = tennis_api.get_upcoming_matches(days=14)
        
        match = next((m for m in matches if m['id'] == match_id), None)
        
        if not match:
            return jsonify({
                'success': False,
                'error': 'Match not found'
            }), 404
        
        # Generate prediction
        predictor = get_tennis_prediction_service()
        prediction = predictor.predict_match(
            player1_name=match['player1']['name'],
            player1_rank=match['player1']['rank'],
            player2_name=match['player2']['name'],
            player2_rank=match['player2']['rank'],
            surface=match['surface'],
            tournament_level=None  # Could extract from tournament name
        )
        
        # Add match ID
        prediction['match_id'] = match_id
        
        # Track usage (optional)
        # current_user.increment_tennis_prediction_count()
        
        logger.info(f"  ✓ Prediction generated: {prediction['predicted_winner']} "
                   f"({max(prediction['player1_win_probability'], prediction['player2_win_probability']):.0%})")
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'is_premium': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tennis_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'tennis',
        'version': '1.0.0'
    })
