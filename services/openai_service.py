"""
Сервис для работы с OpenAI API
Генерация текстовых объяснений прогнозов
"""
from openai import OpenAI
from config import Config


class OpenAIService:
    """
    Клиент для OpenAI API
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def generate_match_explanation(self, prediction, home_stats, away_stats, match_data):
        """
        Сгенерировать человекочитаемое объяснение прогноза
        
        Args:
            prediction: Результат прогноза от ML модели
            home_stats: Статистика домашней команды
            away_stats: Статистика выездной команды
            match_data: Информация о матче
        
        Returns:
            str: Текстовое объяснение
        """
        # Подготовить контекст для GPT
        prompt = self._build_explanation_prompt(
            prediction,
            home_stats,
            away_stats,
            match_data
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            explanation = response.choices[0].message.content.strip()
            return explanation
            
        except Exception as e:
            print(f"❌ Ошибка OpenAI API: {e}")
            return self._generate_fallback_explanation(prediction, home_stats, away_stats)
    
    def _get_system_prompt(self):
        """
        Системный промпт для настройки поведения GPT
        """
        return """Ты - эксперт по анализу футбольной статистики и прогнозированию.

Твоя задача - объяснять прогнозы на футбольные матчи простым и понятным языком.

ВАЖНЫЕ ПРАВИЛА:
1. Объясняй КРАТКО и ЧЕТКО (максимум 5-6 предложений)
2. Используй КОНКРЕТНЫЕ ЦИФРЫ из статистики
3. НЕ ДАВАЙ финансовых советов и не рекомендуй делать ставки
4. Говори о ВЕРОЯТНОСТИ, а не гарантиях
5. Используй эмодзи для наглядности (⚽🎯📊)
6. Пиши на русском языке

Структура ответа:
1. Краткий вывод (одно предложение)
2. Ключевые факторы (2-3 пункта с цифрами)
3. Дополнительный контекст (форма, личные встречи)
4. Оговорка о неопределенности

Пример хорошего объяснения:
"⚽ Высокая вероятность результативного матча (73%)

🎯 Ключевые факторы:
• Обе команды забивают в среднем по 2+ гола за игру
• В 7 из 10 последних матчей хозяев было >2.5 голов
• Гости пропускают в среднем 1.8 гола в выездных матчах

📊 Обе команды в хорошей форме и играют в атакующий футбол. В личных встречах обычно много голов.

⚠️ Прогноз основан на статистике и не гарантирует результат."
"""
    
    def _build_explanation_prompt(self, prediction, home_stats, away_stats, match_data):
        """
        Построить промпт для генерации объяснения
        """
        prob = prediction['probability']
        confidence = prediction['confidence']
        
        prompt = f"""Объясни прогноз на футбольный матч:

МАТЧ:
{match_data['home_team_name']} vs {match_data['away_team_name']}
Лига: {match_data.get('league', 'Неизвестно')}
Дата: {match_data.get('date', 'Неизвестно')}

ПРОГНОЗ МОДЕЛИ:
Вероятность Over 2.5 голов: {prob:.1%}
Уровень уверенности: {confidence}

СТАТИСТИКА ДОМАШНЕЙ КОМАНДЫ ({match_data['home_team_name']}):
• Средние голы за матч: {home_stats.get('avg_goals_scored', 0):.2f}
• Средние пропущенные: {home_stats.get('avg_goals_conceded', 0):.2f}
• Over 2.5 в их матчах: {home_stats.get('over_2_5_percentage', 0):.0%}
• Последняя форма: {home_stats.get('last_5_form', 'N/A')}
• BTTS процент: {home_stats.get('btts_percentage', 0):.0%}

СТАТИСТИКА ГОСТЕВОЙ КОМАНДЫ ({match_data['away_team_name']}):
• Средние голы за матч: {away_stats.get('avg_goals_scored', 0):.2f}
• Средние пропущенные: {away_stats.get('avg_goals_conceded', 0):.2f}
• Over 2.5 в их матчах: {away_stats.get('over_2_5_percentage', 0):.0%}
• Последняя форма: {away_stats.get('last_5_form', 'N/A')}
• BTTS процент: {away_stats.get('btts_percentage', 0):.0%}

ЗАДАЧА:
Объясни, почему модель дала такую вероятность. Укажи главные факторы, которые влияют на прогноз.
Будь конкретным, используй цифры, но пиши простым языком.
"""
        return prompt
    
    def _generate_fallback_explanation(self, prediction, home_stats, away_stats):
        """
        Резервное объяснение если OpenAI недоступен
        """
        prob = prediction['probability']
        
        explanation = f"⚽ Вероятность Over 2.5 голов: {prob:.1%}\n\n"
        
        explanation += "🎯 Ключевые факторы:\n"
        explanation += f"• Домашняя команда забивает в среднем {home_stats.get('avg_goals_scored', 0):.1f} гола\n"
        explanation += f"• Гостевая команда забивает в среднем {away_stats.get('avg_goals_scored', 0):.1f} гола\n"
        explanation += f"• Over 2.5 в матчах хозяев: {home_stats.get('over_2_5_percentage', 0):.0%}\n"
        explanation += f"• Over 2.5 в матчах гостей: {away_stats.get('over_2_5_percentage', 0):.0%}\n\n"
        
        if prob >= 0.7:
            explanation += "📊 Статистика обеих команд указывает на высокую вероятность результативного матча.\n\n"
        elif prob >= 0.55:
            explanation += "📊 Умеренная вероятность результативного матча на основе статистики команд.\n\n"
        else:
            explanation += "📊 Статистика не дает уверенности в результативном матче.\n\n"
        
        explanation += "⚠️ Прогноз основан на статистических данных и не гарантирует результат."
        
        return explanation
    
    def generate_daily_summary(self, predictions):
        """
        Сгенерировать краткое резюме прогнозов на день
        
        Args:
            predictions: Список прогнозов
        
        Returns:
            str: Текстовое резюме
        """
        if not predictions:
            return "Сегодня нет прогнозов."
        
        # Подготовить данные
        high_confidence = [p for p in predictions if p['confidence'] == 'high']
        total_matches = len(predictions)
        
        prompt = f"""Создай краткое привлекательное резюме футбольных прогнозов на сегодня.

ДАННЫЕ:
Всего прогнозов: {total_matches}
Прогнозов с высокой уверенностью: {len(high_confidence)}

ТОП-5 ПРОГНОЗОВ:
"""
        
        for i, pred in enumerate(predictions[:5], 1):
            match = pred['match_info']
            prompt += f"\n{i}. {match['home_team']} vs {match['away_team']}"
            prompt += f"\n   Вероятность Over 2.5: {pred['probability']:.0%}"
            prompt += f"\n   Уверенность: {pred['confidence']}\n"
        
        prompt += """
ЗАДАЧА:
Создай короткое (3-4 предложения) приветственное сообщение для пользователей с обзором прогнозов на день.
Будь позитивным и информативным. Используй эмодзи.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - ассистент GoalPredictor.AI. Создаешь краткие дружелюбные сообщения для пользователей."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"❌ Ошибка генерации резюме: {e}")
            return f"⚽ Сегодня {total_matches} прогнозов, из них {len(high_confidence)} с высокой уверенностью!"
    
    def explain_model_accuracy(self, correct_predictions, total_predictions):
        """
        Объяснить точность модели пользователю
        """
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        prompt = f"""Объясни пользователю простым языком точность нашей модели прогнозирования:

Правильных прогнозов: {correct_predictions}
Всего прогнозов: {total_predictions}
Точность: {accuracy:.1%}

Задача: Объясни, что означает эта точность, хорошо это или нет для спортивной аналитики.
Будь честным и объективным. 2-3 предложения.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - эксперт по спортивной аналитике."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return f"Наша модель показывает точность {accuracy:.1%}, что является {'хорошим' if accuracy >= 0.6 else 'средним'} результатом для спортивных прогнозов."


# Тестирование
if __name__ == '__main__':
    service = OpenAIService()
    
    # Тестовые данные
    test_prediction = {
        'probability': 0.73,
        'confidence': 'high'
    }
    
    test_home_stats = {
        'avg_goals_scored': 2.1,
        'avg_goals_conceded': 1.2,
        'over_2_5_percentage': 0.65,
        'last_5_form': 'WWDWL',
        'btts_percentage': 0.60
    }
    
    test_away_stats = {
        'avg_goals_scored': 1.8,
        'avg_goals_conceded': 1.5,
        'over_2_5_percentage': 0.70,
        'last_5_form': 'WDLWW',
        'btts_percentage': 0.75
    }
    
    test_match = {
        'home_team_name': 'Manchester United',
        'away_team_name': 'Liverpool',
        'league': 'Premier League',
        'date': '2025-10-05'
    }
    
    print("🤖 Тестирование OpenAI Service\n")
    print("Генерирую объяснение прогноза...\n")
    
    explanation = service.generate_match_explanation(
        test_prediction,
        test_home_stats,
        test_away_stats,
        test_match
    )
    
    print("="*60)
    print(explanation)
    print("="*60)
