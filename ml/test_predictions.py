"""
Тестирование обученной модели на реальных данных
"""
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.model import GoalPredictorModel
from ml.train import calculate_team_statistics, load_kaggle_dataset


def test_model_predictions():
    """Тестировать модель на последних матчах"""
    
    print("="*60)
    print("🧪 Тестирование модели GoalPredictor.AI")
    print("="*60)
    
    # Загрузить модель
    print("\n📂 Загрузка модели...")
    model = GoalPredictorModel()
    
    # Найти последнюю модель
    model_files = [f for f in os.listdir('ml/models') if f.endswith('.pkl')]
    if not model_files:
        print("❌ Модель не найдена! Сначала запустите: python ml/train.py")
        return
    
    latest_model = sorted(model_files)[-1]
    model.load_model(latest_model)
    print(f"✅ Загружена модель: {latest_model}")
    
    # Загрузить данные
    print("\n📁 Загрузка данных...")
    dataset_path = os.path.join('data', 'processed', 'football_matches.csv')
    df = load_kaggle_dataset(dataset_path)
    
    # Взять последние 20 матчей для теста
    test_matches = df.tail(20)
    
    print(f"\n🎯 Тестирование на {len(test_matches)} последних матчах...\n")
    
    correct_predictions = 0
    total_predictions = 0
    
    for idx, match in test_matches.iterrows():
        # Получить историю до этого матча
        history = df[df['Date'] < match['Date']]
        
        if len(history) < 50:
            continue
        
        # Статистика команд
        home_stats = calculate_team_statistics(history, match['HomeTeam'], is_home=True)
        away_stats = calculate_team_statistics(history, match['AwayTeam'], is_home=False)
        
        if home_stats is None or away_stats is None:
            continue
        
        if home_stats['total_matches'] < 5 or away_stats['total_matches'] < 5:
            continue
        
        # Создать признаки
        match_info = {
            'date': match['Date'],
            'league': match['League']
        }
        
        features = model.create_features(home_stats, away_stats, match_info)
        
        # Получить предсказание
        prediction = model.predict_from_features(features)
        over_2_5_prob = prediction['over_2_5']
        
        # Фактический результат
        actual_over_2_5 = match['Over2_5']
        predicted_over_2_5 = 1 if over_2_5_prob >= 0.5 else 0
        
        # Проверка точности
        is_correct = (predicted_over_2_5 == actual_over_2_5)
        if is_correct:
            correct_predictions += 1
        total_predictions += 1
        
        # Вывод результата
        result_icon = "✅" if is_correct else "❌"
        actual_goals = int(match['FTHG'] + match['FTAG'])
        
        print(f"{result_icon} {match['HomeTeam'][:20]:20} vs {match['AwayTeam'][:20]:20}")
        print(f"   Счет: {int(match['FTHG'])}-{int(match['FTAG'])} (Голов: {actual_goals})")
        print(f"   Предсказание Over 2.5: {over_2_5_prob:.1%} | Факт: {'ДА' if actual_over_2_5 else 'НЕТ'}")
        print()
    
    # Финальная статистика
    accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    print("="*60)
    print(f"📊 Результаты тестирования:")
    print(f"   Протестировано матчей: {total_predictions}")
    print(f"   Правильных предсказаний: {correct_predictions}")
    print(f"   Точность: {accuracy:.1f}%")
    print("="*60)


if __name__ == '__main__':
    test_model_predictions()
