"""
API маршруты для работы с матчами и прогнозами
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime

from models import Match, Prediction, Team, User
from ml.predict import PredictionService
from services.football_api import FootballAPIService
from app import db

matches_bp = Blueprint('matches', __name__)
prediction_service = PredictionService()
football_api = FootballAPIService()


@matches_bp.route('/today', methods=['GET'])
def get_todays_matches():
    """
    Получить прогнозы на сегодняшние матчи
    """
    try:
        league = request.args.get('league')
        
        # Получить прогнозы
        predictions = prediction_service.predict_todays_matches(league)
        
        # Ограничить для бесплатных пользователей
        if current_user.is_authenticated:
            user = current_user
            if not user.is_premium:
                predictions = predictions[:3]  # Только первые 3
        else:
            predictions = predictions[:1]  # Только 1 для неавторизованных
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@matches_bp.route('/<int:match_id>', methods=['GET'])
@login_required
def get_match_details(match_id):
    """
    Получить детали конкретного матча с прогнозом
    """
    try:
        # Проверить лимит пользователя
        if not current_user.can_view_prediction():
            return jsonify({
                'success': False,
                'error': 'Достигнут дневной лимит прогнозов. Оформите Premium подписку.'
            }), 403
        
        # Получить матч
        match = Match.query.get(match_id)
        
        if not match:
            return jsonify({
                'success': False,
                'error': 'Матч не найден'
            }), 404
        
        # Получить прогноз
        prediction = Prediction.query.filter_by(match_id=match_id).first()
        
        if not prediction:
            # Создать прогноз если его нет
            match_data = {
                'home_team_id': match.home_team_id,
                'away_team_id': match.away_team_id,
                'home_team_name': match.home_team.name,
                'away_team_name': match.away_team.name,
                'league': match.league,
                'date': match.match_date
            }
            
            prediction_data = prediction_service.predict_match(match_data)
            
            # Сохранить прогноз
            prediction = Prediction(
                match_id=match_id,
                probability=prediction_data['probability'],
                confidence=prediction_data['confidence'],
                explanation=prediction_data.get('explanation'),
                factors=prediction_data.get('features'),
                model_version=prediction_data.get('model_version')
            )
            
            db.session.add(prediction)
            db.session.commit()
        
        # Увеличить счетчик просмотров
        current_user.increment_prediction_count()
        
        # Записать просмотр
        from models import UserPrediction
        user_pred = UserPrediction(
            user_id=current_user.id,
            prediction_id=prediction.id
        )
        db.session.add(user_pred)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'match': {
                'id': match.id,
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'league': match.league,
                'date': match.match_date.isoformat(),
                'status': match.status
            },
            'prediction': {
                'probability': prediction.probability,
                'confidence': prediction.confidence,
                'prediction': 'Over 2.5' if prediction.probability >= 0.55 else 'Under 2.5',
                'explanation': prediction.explanation,
                'created_at': prediction.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@matches_bp.route('/league/<league_name>', methods=['GET'])
def get_league_predictions(league_name):
    """
    Получить прогнозы по конкретной лиге
    """
    try:
        # Получить матчи лиги
        matches = Match.query.filter_by(
            league=league_name,
            status='scheduled'
        ).order_by(Match.match_date).limit(20).all()
        
        predictions = []
        
        for match in matches:
            prediction = Prediction.query.filter_by(match_id=match.id).first()
            
            if prediction:
                predictions.append({
                    'match_id': match.id,
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'date': match.match_date.isoformat(),
                    'probability': prediction.probability,
                    'confidence': prediction.confidence
                })
        
        return jsonify({
            'success': True,
            'league': league_name,
            'count': len(predictions),
            'predictions': predictions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@matches_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Получить общую статистику прогнозов
    """
    try:
        # Статистика точности
        total_predictions = Prediction.query.filter(
            Prediction.is_correct.isnot(None)
        ).count()
        
        correct_predictions = Prediction.query.filter_by(
            is_correct=True
        ).count()
        
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        # Статистика по уверенности
        high_confidence = Prediction.query.filter_by(confidence='high').count()
        medium_confidence = Prediction.query.filter_by(confidence='medium').count()
        low_confidence = Prediction.query.filter_by(confidence='low').count()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'accuracy': round(accuracy, 2),
                'confidence_distribution': {
                    'high': high_confidence,
                    'medium': medium_confidence,
                    'low': low_confidence
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@matches_bp.route('/update-results', methods=['POST'])
def update_match_results():
    """
    Обновить результаты завершенных матчей (admin/cron)
    """
    try:
        # TODO: Добавить проверку прав администратора
        
        # Получить завершенные матчи без результатов
        matches = Match.query.filter(
            Match.status == 'finished',
            Match.total_goals.is_(None)
        ).all()
        
        updated = 0
        
        for match in matches:
            result = football_api.update_match_results(match.api_id)
            
            if result:
                match.home_score = result['home_score']
                match.away_score = result['away_score']
                match.total_goals = result['total_goals']
                match.status = result['status']
                
                # Проверить правильность прогноза
                prediction = Prediction.query.filter_by(match_id=match.id).first()
                
                if prediction:
                    prediction.is_correct = result['over_2_5'] == (prediction.probability >= 0.55)
                    prediction.actual_result = 'Over 2.5' if result['over_2_5'] else 'Under 2.5'
                
                updated += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated': updated
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
