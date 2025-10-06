from extensions import db
from app import create_app
from models import Team, Match

app = create_app()

with app.app_context():
    print(f'Teams: {Team.query.count()}')
    print(f'Finished matches: {Match.query.filter_by(status="FINISHED").count()}')
    print(f'All matches: {Match.query.count()}')
    
    teams = Team.query.limit(5).all()
    print('\nSample teams:')
    for t in teams:
        print(f'  {t.name} ({t.league})')
    
    # Проверим есть ли Burnley
    burnley = Team.query.filter_by(name='Burnley', league='PL').first()
    print(f'\nBurnley exists: {burnley is not None}')
    
    if burnley:
        matches = Match.query.filter_by(home_team_id=burnley.id, status='FINISHED').count()
        print(f'Burnley finished home matches: {matches}')
