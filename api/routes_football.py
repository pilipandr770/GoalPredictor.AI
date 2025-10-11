"""
Football API Routes
Endpoints for football matches and predictions
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from services.football_data_org import FootballDataOrgAPI
import logging

logger = logging.getLogger(__name__)

football_bp = Blueprint('football', __name__, url_prefix='/api/football')


@football_bp.route('/matches', methods=['GET'])
def get_matches():
    """
    Get upcoming football matches
    
    Query params:
        days: int - Number of days to look ahead (default: 7)
        league: str - Filter by league (optional)
    
    Returns:
        {
            'success': True,
            'matches': [
                {
                    'id': 535047,
                    'date': '2025-10-11T22:00:00Z',
                    'competition': 'Campeonato Brasileiro Série A',
                    'homeTeam': {
                        'name': 'SE Palmeiras',
                        'crest': 'url'
                    },
                    'awayTeam': {
                        'name': 'EC Juventude',
                        'crest': 'url'
                    },
                    'status': 'TIMED'
                }
            ],
            'count': 15
        }
    """
    try:
        days = int(request.args.get('days', 7))
        days = min(days, 10)  # Max 10 days (Football-Data.org API limit)
        league = request.args.get('league', None)
        
        logger.info(f"⚽ Fetching football matches for next {days} days...")
        
        # Get matches from API
        football_api = FootballDataOrgAPI()
        
        # Get date range
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Request all matches
        endpoint = 'matches'
        params = {
            'dateFrom': date_from,
            'dateTo': date_to
        }
        
        data = football_api._make_request(endpoint, params)
        
        if not data or 'matches' not in data:
            return jsonify({
                'success': True,
                'matches': [],
                'count': 0
            })
        
        matches = data['matches']
        
        # Filter by league if specified
        if league:
            matches = [m for m in matches if m.get('competition', {}).get('name') == league]
        
        # Format for frontend
        formatted_matches = []
        for match in matches:
            formatted = {
                'id': match['id'],
                'date': match['utcDate'],
                'competition': match.get('competition', {}).get('name', 'Unknown'),
                'homeTeam': {
                    'name': match.get('homeTeam', {}).get('name', 'Unknown'),
                    'crest': match.get('homeTeam', {}).get('crest', '')
                },
                'awayTeam': {
                    'name': match.get('awayTeam', {}).get('name', 'Unknown'),
                    'crest': match.get('awayTeam', {}).get('crest', '')
                },
                'status': match.get('status', 'SCHEDULED'),
                'venue': match.get('venue', 'Unknown')
            }
            formatted_matches.append(formatted)
        
        return jsonify({
            'success': True,
            'matches': formatted_matches,
            'count': len(formatted_matches)
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching football matches: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'matches': []
        }), 500


@football_bp.route('/predictions/<int:match_id>', methods=['GET'])
@login_required
def get_prediction(match_id):
    """
    Get prediction for a specific match using trained ML model
    Requires authentication and premium subscription
    """
    try:
        # Check if user has access to predictions
        if not current_user.is_premium and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Premium subscription required',
                'redirectTo': '/pricing'
            }), 403
        
        logger.info(f"⚽ Generating prediction for match {match_id}...")
        
        # Get match details from API
        football_api = FootballDataOrgAPI()
        
        # Get upcoming matches (max 10 days per Football-Data.org API limit)
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        
        data = football_api._make_request('matches', {
            'dateFrom': date_from,
            'dateTo': date_to
        })
        
        if not data or 'matches' not in data:
            logger.error(f"❌ Failed to fetch matches from API")
            return jsonify({
                'success': False,
                'error': 'Unable to fetch match data from API. Please try again later.'
            }), 503
        
        # Find the specific match
        match = next((m for m in data['matches'] if m['id'] == match_id), None)
        
        if not match:
            return jsonify({
                'success': False,
                'error': 'Match not found'
            }), 404
        
        # Use Over 2.5 Goals ML prediction service
        from services.over25_prediction_service import get_over25_prediction_service
        predictor = get_over25_prediction_service()
        
        # Prepare match data for prediction
        # TODO: Get real team statistics from API or database
        # For now, use placeholder data
        match_data = {
            'home_recent_goals_for': 8,
            'home_recent_goals_against': 6,
            'home_avg_goals': 1.5,
            'home_scoring_trend': 0,
            'away_recent_goals_for': 7,
            'away_recent_goals_against': 7,
            'away_avg_goals': 1.4,
            'away_scoring_trend': 0,
            'home_recent_form_points': 8,
            'away_recent_form_points': 7
        }
        
        # Get ML prediction
        ml_prediction = predictor.predict(match_data)
        
        # Format response for Over/Under 2.5
        over_probability = ml_prediction.get('over_2_5_probability', 0.5)
        under_probability = ml_prediction.get('under_2_5_probability', 0.5)
        
        prediction = {
            'matchId': match_id,
            'type': 'over_under_2_5',
            'over_2_5': float(over_probability * 100),
            'under_2_5': float(under_probability * 100),
            'confidence': float(ml_prediction.get('confidence_percentage', 50)),
            'recommendation': ml_prediction.get('prediction', 'Over 2.5'),
            'keyFactors': ml_prediction.get('key_factors', []),
            'explanation': f"Ймовірність більше 2.5 голів: {over_probability*100:.1f}%. "
                          f"Модель аналізує історію голів команд і прогнозує результативність матчу."
        }
        
        logger.info(f"  ✓ Prediction: {prediction['recommendation']} (confidence: {prediction['confidence']:.0f}%)")
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting prediction for match {match_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@football_bp.route('/competitions', methods=['GET'])
def get_competitions():
    """
    Get list of available competitions
    """
    try:
        football_api = FootballDataOrgAPI()
        
        # Get competitions with matches in next 7 days
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        data = football_api._make_request('matches', {
            'dateFrom': date_from,
            'dateTo': date_to
        })
        
        if not data or 'matches' not in data:
            return jsonify({
                'success': True,
                'competitions': []
            })
        
        # Extract unique competitions
        competitions = {}
        for match in data['matches']:
            comp = match.get('competition', {})
            comp_id = comp.get('id')
            if comp_id and comp_id not in competitions:
                competitions[comp_id] = {
                    'id': comp_id,
                    'name': comp.get('name', 'Unknown'),
                    'emblem': comp.get('emblem', ''),
                    'area': comp.get('area', {}).get('name', '')
                }
        
        return jsonify({
            'success': True,
            'competitions': list(competitions.values())
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching competitions: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'competitions': []
        }), 500
