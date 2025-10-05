"""
Улучшенная генерация признаков (feature engineering) для модели прогнозирования
Использует детальную статистику: удары, корнеры, карточки, форму команд
"""
import pandas as pd
import numpy as np
from datetime import datetime


class AdvancedFeatureEngineering:
    """Продвинутый генератор признаков для модели"""
    
    def __init__(self):
        self.features_count = 0
    
    def load_enhanced_dataset(self, filepath):
        """Загрузить расширенный датасет Premier League"""
        print(f"📁 Загрузка расширенного датасета: {filepath}")
        
        df = pd.read_csv(filepath, low_memory=False)
        
        # Оставить только нужные колонки
        essential_cols = [
            'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR',
            'HTHG', 'HTAG', 'HTR',  # Голы и результат первого тайма
            'HS', 'AS',              # Удары
            'HST', 'AST',            # Удары в створ
            'HF', 'AF',              # Фолы
            'HC', 'AC',              # Корнеры
            'HY', 'AY',              # Желтые карточки
            'HR', 'AR',              # Красные карточки
            # Дополнительные признаки если есть
            'HTGS', 'ATGS',          # Goals Scored
            'HTGC', 'ATGC',          # Goals Conceded
            'HTP', 'ATP',            # Points
            'HTFormPts', 'ATFormPts', # Form Points
            'HTGD', 'ATGD',          # Goal Difference
            'HTWinStreak3', 'ATWinStreak3',
            'HTWinStreak5', 'ATWinStreak5',
            'HTLossStreak3', 'ATLossStreak3',
        ]
        
        # Взять только существующие колонки
        available_cols = [col for col in essential_cols if col in df.columns]
        df = df[available_cols].copy()
        
        # Убрать пустые строки
        df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        
        # Конвертировать дату
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Date'])
        
        # Базовые целевые переменные
        df['FTHG'] = pd.to_numeric(df['FTHG'], errors='coerce')
        df['FTAG'] = pd.to_numeric(df['FTAG'], errors='coerce')
        df['TotalGoals'] = df['FTHG'] + df['FTAG']
        df['Over2_5'] = (df['TotalGoals'] > 2.5).astype(int)
        df['BTTS'] = ((df['FTHG'] > 0) & (df['FTAG'] > 0)).astype(int)
        
        # Сортировка по дате
        df = df.sort_values('Date').reset_index(drop=True)
        
        print(f"✅ Загружено {len(df)} матчей")
        print(f"   Период: {df['Date'].min()} - {df['Date'].max()}")
        print(f"   Доступно колонок: {len(df.columns)}")
        print(f"   Over 2.5: {df['Over2_5'].mean():.1%}")
        
        return df
    
    def calculate_rolling_stats(self, df, team, home=True, windows=[3, 5, 10]):
        """
        Рассчитать скользящие средние для команды
        
        Args:
            df: DataFrame с матчами
            team: Название команды
            home: True для домашних матчей, False для выездных
            windows: Окна для скользящих средних
        """
        # Фильтр матчей команды
        if home:
            team_matches = df[df['HomeTeam'] == team].copy()
            prefix = 'H'
        else:
            team_matches = df[df['AwayTeam'] == team].copy()
            prefix = 'A'
        
        stats = {}
        
        # Если нет матчей, вернуть нули
        if len(team_matches) == 0:
            for window in windows:
                stats[f'goals_scored_last_{window}'] = 0
                stats[f'goals_conceded_last_{window}'] = 0
                stats[f'shots_last_{window}'] = 0
                stats[f'shots_on_target_last_{window}'] = 0
                stats[f'corners_last_{window}'] = 0
                stats[f'fouls_last_{window}'] = 0
                stats[f'yellow_cards_last_{window}'] = 0
            return stats
        
        # Для каждого окна
        for window in windows:
            # Голы забитые
            if f'FT{prefix}G' in team_matches.columns and len(team_matches) > 0:
                goals_scored = team_matches[f'FT{prefix}G'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'goals_scored_last_{window}'] = goals_scored
            else:
                stats[f'goals_scored_last_{window}'] = 0
            
            # Голы пропущенные
            opp_prefix = 'A' if prefix == 'H' else 'H'
            if f'FT{opp_prefix}G' in team_matches.columns and len(team_matches) > 0:
                goals_conceded = team_matches[f'FT{opp_prefix}G'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'goals_conceded_last_{window}'] = goals_conceded
            else:
                stats[f'goals_conceded_last_{window}'] = 0
            
            # Удары
            if f'{prefix}S' in team_matches.columns and len(team_matches) > 0:
                shots = team_matches[f'{prefix}S'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'shots_last_{window}'] = shots
            else:
                stats[f'shots_last_{window}'] = 0
            
            # Удары в створ
            if f'{prefix}ST' in team_matches.columns and len(team_matches) > 0:
                shots_on_target = team_matches[f'{prefix}ST'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'shots_on_target_last_{window}'] = shots_on_target
            else:
                stats[f'shots_on_target_last_{window}'] = 0
            
            # Корнеры
            if f'{prefix}C' in team_matches.columns and len(team_matches) > 0:
                corners = team_matches[f'{prefix}C'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'corners_last_{window}'] = corners
            else:
                stats[f'corners_last_{window}'] = 0
            
            # Фолы
            if f'{prefix}F' in team_matches.columns and len(team_matches) > 0:
                fouls = team_matches[f'{prefix}F'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'fouls_last_{window}'] = fouls
            else:
                stats[f'fouls_last_{window}'] = 0
            
            # Карточки
            if f'{prefix}Y' in team_matches.columns and len(team_matches) > 0:
                yellows = team_matches[f'{prefix}Y'].rolling(window=window, min_periods=1).mean().iloc[-1]
                stats[f'yellow_cards_last_{window}'] = yellows
            else:
                stats[f'yellow_cards_last_{window}'] = 0
        
        return stats
    
    def calculate_head_to_head(self, df, home_team, away_team, last_n=5):
        """Статистика личных встреч"""
        h2h_home = df[(df['HomeTeam'] == home_team) & (df['AwayTeam'] == away_team)]
        h2h_away = df[(df['HomeTeam'] == away_team) & (df['AwayTeam'] == home_team)]
        h2h = pd.concat([h2h_home, h2h_away]).sort_values('Date').tail(last_n)
        
        if len(h2h) == 0:
            return {
                'h2h_matches': 0,
                'h2h_avg_goals': 0,
                'h2h_over_2_5_pct': 0,
            }
        
        stats = {
            'h2h_matches': len(h2h),
            'h2h_avg_goals': h2h['TotalGoals'].mean(),
            'h2h_over_2_5_pct': (h2h['TotalGoals'] > 2.5).mean(),
        }
        
        return stats
    
    def create_advanced_features(self, df, match_idx):
        """
        Создать продвинутые признаки для конкретного матча
        
        Args:
            df: DataFrame со всеми матчами
            match_idx: Индекс текущего матча
        """
        match = df.iloc[match_idx]
        history = df.iloc[:match_idx]  # История до этого матча
        
        if len(history) < 20:  # Минимум 20 матчей для надежной статистики
            return None
        
        features = {}
        
        home_team = match['HomeTeam']
        away_team = match['AwayTeam']
        
        # === 1. БАЗОВЫЕ ПРИЗНАКИ ===
        
        # Голы за последние матчи (3, 5, 10)
        home_rolling = self.calculate_rolling_stats(history, home_team, home=True)
        away_rolling = self.calculate_rolling_stats(history, away_team, home=False)
        
        # Добавить с префиксами
        for key, value in home_rolling.items():
            features[f'home_{key}'] = value
        for key, value in away_rolling.items():
            features[f'away_{key}'] = value
        
        # === 2. HEAD-TO-HEAD ===
        h2h_stats = self.calculate_head_to_head(history, home_team, away_team)
        features.update(h2h_stats)
        
        # === 3. ВРЕМЕННЫЕ ПРИЗНАКИ ===
        match_date = match['Date']
        features['day_of_week'] = match_date.dayofweek  # 0=Monday, 6=Sunday
        features['is_weekend'] = 1 if match_date.dayofweek >= 5 else 0
        features['month'] = match_date.month
        features['is_holiday_season'] = 1 if match_date.month in [12, 1] else 0
        
        # === 4. ФОРМА КОМАНД (из датасета если есть) ===
        if 'HTFormPts' in match and pd.notna(match['HTFormPts']):
            features['home_form_points'] = match['HTFormPts']
        if 'ATFormPts' in match and pd.notna(match['ATFormPts']):
            features['away_form_points'] = match['ATFormPts']
        
        # Серии побед
        if 'HTWinStreak3' in match and pd.notna(match['HTWinStreak3']):
            features['home_win_streak_3'] = match['HTWinStreak3']
        if 'ATWinStreak3' in match and pd.notna(match['ATWinStreak3']):
            features['away_win_streak_3'] = match['ATWinStreak3']
        
        # === 5. РАСЧЕТНЫЕ ПРИЗНАКИ ===
        
        # Ожидаемое количество голов
        if 'home_goals_scored_last_5' in features and 'away_goals_conceded_last_5' in features:
            features['expected_home_goals'] = (
                features['home_goals_scored_last_5'] + features['away_goals_conceded_last_5']
            ) / 2
        
        if 'away_goals_scored_last_5' in features and 'home_goals_conceded_last_5' in features:
            features['expected_away_goals'] = (
                features['away_goals_scored_last_5'] + features['home_goals_conceded_last_5']
            ) / 2
        
        if 'expected_home_goals' in features and 'expected_away_goals' in features:
            features['expected_total_goals'] = features['expected_home_goals'] + features['expected_away_goals']
        
        # Атакующая сила
        if 'home_shots_on_target_last_5' in features and 'away_shots_on_target_last_5' in features:
            features['attacking_strength'] = features['home_shots_on_target_last_5'] + features['away_shots_on_target_last_5']
        
        # Агрессивность (фолы + карточки)
        if 'home_fouls_last_5' in features and 'away_fouls_last_5' in features:
            features['total_aggression'] = features['home_fouls_last_5'] + features['away_fouls_last_5']
        
        # === 6. ЦЕЛЕВЫЕ ПЕРЕМЕННЫЕ ===
        features['over_2_5'] = match['Over2_5']
        features['btts'] = match['BTTS']
        
        return features
    
    def prepare_training_dataset(self, df, min_history=20):
        """Подготовить полный датасет для обучения"""
        print("\n🔄 Генерация продвинутых признаков...")
        
        all_features = []
        
        for idx in range(len(df)):
            if idx % 1000 == 0 and idx > 0:
                print(f"   Обработано {idx}/{len(df)} матчей...")
            
            features = self.create_advanced_features(df, idx)
            if features is not None:
                all_features.append(features)
        
        features_df = pd.DataFrame(all_features)
        
        # Заполнить NaN нулями
        features_df = features_df.fillna(0)
        
        print(f"\n✅ Создано признаков: {len(features_df.columns) - 2}")  # -2 для over_2_5 и btts
        print(f"   Образцов для обучения: {len(features_df)}")
        print(f"   Over 2.5: {features_df['over_2_5'].mean():.1%}")
        
        self.features_count = len(features_df.columns) - 2
        
        return features_df


def main():
    """Тестовая функция"""
    print("="*70)
    print("🚀 ПРОДВИНУТАЯ ГЕНЕРАЦИЯ ПРИЗНАКОВ")
    print("="*70)
    
    # Загрузить датасет
    fe = AdvancedFeatureEngineering()
    df = fe.load_enhanced_dataset('data/raw/premier_league_detailed.csv')
    
    # Использовать все доступные данные
    print(f"\n📅 Используем все данные: {len(df)} матчей")
    
    # Создать признаки
    features_df = fe.prepare_training_dataset(df)
    
    # Сохранить
    output_path = 'data/processed/enhanced_features.csv'
    features_df.to_csv(output_path, index=False)
    print(f"\n💾 Признаки сохранены: {output_path}")
    
    # Показать примеры
    print(f"\n📋 Примеры признаков:")
    print(features_df.head(3))
    
    print(f"\n📊 Статистика признаков:")
    print(features_df.describe())


if __name__ == '__main__':
    main()
