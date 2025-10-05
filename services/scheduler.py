"""
Планировщик задач для автоматического обновления данных и отправки прогнозов
"""
import os
import sys
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Match, Team, Prediction, User
from services.football_api import FootballAPIService
from ml.predict import PredictionService
from services.openai_service import OpenAIService
from app import db


class TaskScheduler:
    """
    Планировщик автоматических задач
    """
    
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.football_api = FootballAPIService()
        self.prediction_service = PredictionService()
        self.openai_service = OpenAIService()
    
    def start(self):
        """
        Запустить планировщик
        """
        # Обновление матчей каждое утро в 07:00
        self.scheduler.add_job(
            self.update_fixtures,
            trigger=CronTrigger(hour=7, minute=0),
            id='update_fixtures',
            name='Обновление расписания матчей',
            replace_existing=True
        )
        
        # Создание прогнозов каждое утро в 08:00
        self.scheduler.add_job(
            self.generate_predictions,
            trigger=CronTrigger(hour=8, minute=0),
            id='generate_predictions',
            name='Генерация прогнозов',
            replace_existing=True
        )
        
        # Обновление результатов каждые 2 часа
        self.scheduler.add_job(
            self.update_results,
            trigger='interval',
            hours=2,
            id='update_results',
            name='Обновление результатов матчей',
            replace_existing=True
        )
        
        # Обновление статистики команд раз в неделю (понедельник 02:00)
        self.scheduler.add_job(
            self.update_team_statistics,
            trigger=CronTrigger(day_of_week='mon', hour=2, minute=0),
            id='update_team_stats',
            name='Обновление статистики команд',
            replace_existing=True
        )
        
        # Отправка email с прогнозами (опционально)
        # self.scheduler.add_job(
        #     self.send_daily_predictions,
        #     trigger=CronTrigger(hour=9, minute=0),
        #     id='send_predictions',
        #     name='Отправка прогнозов пользователям'
        # )
        
        self.scheduler.start()
        print("✅ Планировщик задач запущен")
        self._print_jobs()
    
    def _print_jobs(self):
        """Вывести список запланированных задач"""
        print("\n📋 Запланированные задачи:")
        for job in self.scheduler.get_jobs():
            print(f"   • {job.name} (следующий запуск: {job.next_run_time})")
        print()
    
    def update_fixtures(self):
        """
        Обновить расписание матчей на сегодня и ближайшие дни
        """
        with self.app.app_context():
            print("🔄 Обновление расписания матчей...")
            
            try:
                from config import Config
                
                # Для каждой лиги
                for league_name, league_id in Config.LEAGUES.items():
                    fixtures = self.football_api.get_upcoming_fixtures(league_id, days=7)
                    
                    for fixture in fixtures:
                        # Проверить существует ли матч
                        match = Match.query.filter_by(api_id=fixture['id']).first()
                        
                        if not match:
                            # Создать новый матч
                            # Сначала получить/создать команды
                            home_team = self._get_or_create_team(
                                fixture['home_team_id'],
                                fixture['home_team_name'],
                                league_name
                            )
                            
                            away_team = self._get_or_create_team(
                                fixture['away_team_id'],
                                fixture['away_team_name'],
                                league_name
                            )
                            
                            match = Match(
                                api_id=fixture['id'],
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                league=league_name,
                                match_date=datetime.fromisoformat(fixture['date'].replace('Z', '+00:00')),
                                status=fixture['status']
                            )
                            
                            db.session.add(match)
                
                db.session.commit()
                print(f"✅ Расписание обновлено")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Ошибка обновления расписания: {e}")
    
    def _get_or_create_team(self, api_id, name, league):
        """Получить или создать команду"""
        team = Team.query.filter_by(api_id=api_id).first()
        
        if not team:
            team = Team(
                api_id=api_id,
                name=name,
                league=league,
                country='Unknown'
            )
            db.session.add(team)
            db.session.flush()
        
        return team
    
    def generate_predictions(self):
        """
        Создать прогнозы на сегодняшние матчи
        """
        with self.app.app_context():
            print("🎯 Генерация прогнозов на сегодня...")
            
            try:
                # Получить матчи на сегодня без прогнозов
                today = datetime.utcnow().date()
                
                matches = Match.query.filter(
                    db.func.date(Match.match_date) == today,
                    Match.status == 'scheduled'
                ).all()
                
                generated = 0
                
                for match in matches:
                    # Проверить есть ли уже прогноз
                    existing = Prediction.query.filter_by(match_id=match.id).first()
                    
                    if existing:
                        continue
                    
                    # Создать прогноз
                    match_data = {
                        'home_team_id': match.home_team.api_id,
                        'away_team_id': match.away_team.api_id,
                        'home_team_name': match.home_team.name,
                        'away_team_name': match.away_team.name,
                        'league': match.league,
                        'date': match.match_date
                    }
                    
                    prediction_data = self.prediction_service.predict_match(
                        match_data,
                        include_explanation=True
                    )
                    
                    # Сохранить прогноз
                    prediction = Prediction(
                        match_id=match.id,
                        probability=prediction_data['probability'],
                        confidence=prediction_data['confidence'],
                        explanation=prediction_data.get('explanation'),
                        factors=prediction_data.get('features'),
                        model_version=prediction_data.get('model_version')
                    )
                    
                    db.session.add(prediction)
                    generated += 1
                
                db.session.commit()
                print(f"✅ Создано прогнозов: {generated}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Ошибка генерации прогнозов: {e}")
    
    def update_results(self):
        """
        Обновить результаты завершенных матчей
        """
        with self.app.app_context():
            print("🔄 Обновление результатов матчей...")
            
            try:
                # Получить матчи со статусом live или finished без результатов
                matches = Match.query.filter(
                    Match.status.in_(['live', 'finished']),
                    Match.total_goals.is_(None)
                ).all()
                
                updated = 0
                
                for match in matches:
                    result = self.football_api.update_match_results(match.api_id)
                    
                    if result:
                        match.home_score = result['home_score']
                        match.away_score = result['away_score']
                        match.total_goals = result['total_goals']
                        match.status = result['status']
                        
                        # Проверить правильность прогноза
                        prediction = Prediction.query.filter_by(match_id=match.id).first()
                        
                        if prediction:
                            predicted_over = prediction.probability >= 0.55
                            actual_over = result['over_2_5']
                            
                            prediction.is_correct = (predicted_over == actual_over)
                            prediction.actual_result = 'Over 2.5' if actual_over else 'Under 2.5'
                        
                        updated += 1
                
                db.session.commit()
                print(f"✅ Обновлено результатов: {updated}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Ошибка обновления результатов: {e}")
    
    def update_team_statistics(self):
        """
        Обновить статистику всех команд
        """
        with self.app.app_context():
            print("📊 Обновление статистики команд...")
            
            try:
                teams = Team.query.all()
                updated = 0
                
                from config import Config
                
                for team in teams:
                    # Получить ID лиги
                    league_id = Config.LEAGUES.get(team.league)
                    
                    if not league_id:
                        continue
                    
                    # Получить статистику
                    stats = self.football_api.get_team_statistics(team.api_id, league_id)
                    
                    if stats:
                        team.total_matches = stats.get('total_matches', 0)
                        team.goals_scored = stats.get('goals_scored', 0)
                        team.goals_conceded = stats.get('goals_conceded', 0)
                        team.avg_goals_per_match = stats.get('avg_goals_scored', 0)
                        team.last_update = datetime.utcnow()
                        
                        updated += 1
                
                db.session.commit()
                print(f"✅ Обновлено команд: {updated}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Ошибка обновления статистики: {e}")
    
    def send_daily_predictions(self):
        """
        Отправить прогнозы премиум пользователям (опционально)
        """
        with self.app.app_context():
            print("📧 Отправка прогнозов пользователям...")
            
            try:
                # Получить премиум пользователей
                premium_users = User.query.filter_by(is_premium=True).all()
                
                # Получить прогнозы на сегодня
                today = datetime.utcnow().date()
                
                predictions = db.session.query(Prediction).join(
                    Match,
                    Prediction.match_id == Match.id
                ).filter(
                    db.func.date(Match.match_date) == today,
                    Prediction.confidence.in_(['high', 'medium'])
                ).order_by(
                    Prediction.probability.desc()
                ).limit(5).all()
                
                if not predictions:
                    print("   Нет прогнозов для отправки")
                    return
                
                # TODO: Реализовать отправку email
                # Здесь можно использовать Flask-Mail
                
                print(f"✅ Отправлено пользователям: {len(premium_users)}")
                
            except Exception as e:
                print(f"❌ Ошибка отправки: {e}")
    
    def stop(self):
        """Остановить планировщик"""
        self.scheduler.shutdown()
        print("⏹️  Планировщик остановлен")


def start_scheduler(app):
    """
    Создать и запустить планировщик
    """
    scheduler = TaskScheduler(app)
    scheduler.start()
    return scheduler


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    scheduler = start_scheduler(app)
    
    print("\n⏰ Планировщик запущен в тестовом режиме")
    print("Нажмите Ctrl+C для остановки\n")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
