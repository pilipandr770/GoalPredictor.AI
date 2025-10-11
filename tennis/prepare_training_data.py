"""
Tennis Training Data Preparation
Creates ML-ready dataset with features for player1 win prediction
"""
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta


class TennisTrainingDataPreparator:
    """Prepare tennis training data with features"""
    
    def __init__(self, data_dir='tennis/data'):
        self.data_dir = Path(data_dir)
        self.matches = None
        self.rankings = None
        self.players = None
        
    def load_data(self):
        """Load downloaded data"""
        print("=" * 70)
        print("📂 ЗАВАНТАЖЕННЯ ДАНИХ")
        print("=" * 70)
        print()
        
        # Matches
        matches_path = self.data_dir / 'atp_matches_combined.csv'
        self.matches = pd.read_csv(matches_path)
        print(f"✓ Матчі: {len(self.matches)}")
        
        # Rankings (optional)
        try:
            rankings_path = self.data_dir / 'atp_rankings.csv'
            self.rankings = pd.read_csv(rankings_path)
            print(f"✓ Рейтинги: {len(self.rankings)}")
        except:
            print("⚠️  Рейтинги не завантажено")
        
        # Players (optional)
        try:
            players_path = self.data_dir / 'atp_players.csv'
            self.players = pd.read_csv(players_path, low_memory=False)
            print(f"✓ Гравці: {len(self.players)}")
        except:
            print("⚠️  База гравців не завантажена")
        
        print()
        
    def prepare_matches(self):
        """
        Prepare matches in format: player1 vs player2
        Winner is always player1 (target=1) or player2 (target=0)
        """
        print("=" * 70)
        print("🔧 ПІДГОТОВКА МАТЧІВ")
        print("=" * 70)
        print()
        
        df = self.matches.copy()
        
        # Конвертувати дату
        df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d')
        
        # Сортувати по даті
        df = df.sort_values('tourney_date').reset_index(drop=True)
        
        # Видалити матчі без рейтингу (якщо немає, буде NaN)
        print(f"  Матчів до фільтрації: {len(df)}")
        
        # Базові колонки
        required_cols = ['winner_id', 'loser_id', 'tourney_date', 'surface']
        df = df.dropna(subset=required_cols)
        
        print(f"  Матчів після фільтрації: {len(df)}")
        print()
        
        self.matches = df
        return df
    
    def calculate_player_form(self, matches, player_id, date, window=10):
        """
        Розрахувати форму гравця (останні N матчів до дати)
        
        Returns: (wins, losses, form_points)
        """
        # Матчі гравця до вказаної дати
        player_matches = matches[
            (matches['tourney_date'] < date) &
            ((matches['winner_id'] == player_id) | (matches['loser_id'] == player_id))
        ].tail(window)
        
        if len(player_matches) == 0:
            return 0, 0, 0
        
        wins = (player_matches['winner_id'] == player_id).sum()
        losses = len(player_matches) - wins
        form_points = wins * 3  # 3 points per win
        
        return wins, losses, form_points
    
    def calculate_h2h(self, matches, player1_id, player2_id, date):
        """
        Розрахувати H2H статистику до вказаної дати
        
        Returns: (player1_h2h_wins, player2_h2h_wins)
        """
        h2h_matches = matches[
            (matches['tourney_date'] < date) &
            (
                ((matches['winner_id'] == player1_id) & (matches['loser_id'] == player2_id)) |
                ((matches['winner_id'] == player2_id) & (matches['loser_id'] == player1_id))
            )
        ]
        
        player1_wins = ((h2h_matches['winner_id'] == player1_id)).sum()
        player2_wins = len(h2h_matches) - player1_wins
        
        return player1_wins, player2_wins
    
    def calculate_surface_stats(self, matches, player_id, date, surface):
        """
        Статистика гравця на певному покритті
        
        Returns: (wins, total_matches, win_rate)
        """
        surface_matches = matches[
            (matches['tourney_date'] < date) &
            (matches['surface'] == surface) &
            ((matches['winner_id'] == player_id) | (matches['loser_id'] == player_id))
        ]
        
        if len(surface_matches) == 0:
            return 0, 0, 0.5
        
        wins = (surface_matches['winner_id'] == player_id).sum()
        total = len(surface_matches)
        win_rate = wins / total if total > 0 else 0.5
        
        return wins, total, win_rate
    
    def create_features(self):
        """
        Створити фічі для кожного матчу
        
        ВАЖЛИВО: Використовуємо тільки дані ДО матчу (no leakage!)
        """
        print("=" * 70)
        print("🎯 СТВОРЕННЯ ФІЧ")
        print("=" * 70)
        print()
        
        matches = self.matches.copy()
        features_list = []
        
        total = len(matches)
        
        for idx, match in matches.iterrows():
            if idx % 500 == 0:
                print(f"  Обробка {idx}/{total} матчів...")
            
            # Базова інформація
            winner_id = match['winner_id']
            loser_id = match['loser_id']
            date = match['tourney_date']
            surface = match['surface']
            
            # ВАЖЛИВО: Випадково вибираємо хто player1, хто player2
            # Щоб модель не запам'ятала "winner завжди в колонці 1"
            if np.random.random() > 0.5:
                player1_id = winner_id
                player2_id = loser_id
                target = 1  # player1 виграв
            else:
                player1_id = loser_id
                player2_id = winner_id
                target = 0  # player2 виграв
            
            # Рейтинги
            player1_rank = match.get('winner_rank' if player1_id == winner_id else 'loser_rank', 999)
            player2_rank = match.get('loser_rank' if player1_id == winner_id else 'winner_rank', 999)
            
            # Форма (останні 10 матчів)
            p1_wins, p1_losses, p1_form = self.calculate_player_form(matches, player1_id, date, window=10)
            p2_wins, p2_losses, p2_form = self.calculate_player_form(matches, player2_id, date, window=10)
            
            # H2H
            p1_h2h_wins, p2_h2h_wins = self.calculate_h2h(matches, player1_id, player2_id, date)
            
            # Статистика на покритті
            p1_surf_wins, p1_surf_total, p1_surf_wr = self.calculate_surface_stats(matches, player1_id, date, surface)
            p2_surf_wins, p2_surf_total, p2_surf_wr = self.calculate_surface_stats(matches, player2_id, date, surface)
            
            # Фічі
            features = {
                'match_id': idx,
                'date': date,
                'surface': surface,
                'tourney_name': match.get('tourney_name', ''),
                'tourney_level': match.get('tourney_level', ''),
                
                # Рейтинги
                'player1_rank': player1_rank if pd.notna(player1_rank) else 999,
                'player2_rank': player2_rank if pd.notna(player2_rank) else 999,
                'rank_difference': player1_rank - player2_rank if pd.notna(player1_rank) and pd.notna(player2_rank) else 0,
                
                # Форма
                'player1_recent_wins': p1_wins,
                'player1_recent_losses': p1_losses,
                'player1_form_points': p1_form,
                'player2_recent_wins': p2_wins,
                'player2_recent_losses': p2_losses,
                'player2_form_points': p2_form,
                'form_difference': p1_form - p2_form,
                
                # H2H
                'h2h_player1_wins': p1_h2h_wins,
                'h2h_player2_wins': p2_h2h_wins,
                'h2h_total': p1_h2h_wins + p2_h2h_wins,
                
                # Покриття
                'player1_surface_wins': p1_surf_wins,
                'player1_surface_total': p1_surf_total,
                'player1_surface_winrate': p1_surf_wr,
                'player2_surface_wins': p2_surf_wins,
                'player2_surface_total': p2_surf_total,
                'player2_surface_winrate': p2_surf_wr,
                'surface_winrate_diff': p1_surf_wr - p2_surf_wr,
                
                # One-hot для покриття
                'is_hard': 1 if surface == 'Hard' else 0,
                'is_clay': 1 if surface == 'Clay' else 0,
                'is_grass': 1 if surface == 'Grass' else 0,
                
                # Рівень турніру
                'is_grand_slam': 1 if match.get('tourney_level') == 'G' else 0,
                'is_masters': 1 if match.get('tourney_level') == 'M' else 0,
                
                # TARGET
                'player1_win': target
            }
            
            features_list.append(features)
        
        print(f"  ✓ Оброблено {len(features_list)} матчів")
        print()
        
        df_features = pd.DataFrame(features_list)
        return df_features
    
    def save_training_data(self, df, output_path='tennis/data/tennis_training_data.csv'):
        """Save training data"""
        print("=" * 70)
        print("💾 ЗБЕРЕЖЕННЯ")
        print("=" * 70)
        print()
        
        output_path = Path(output_path)
        df.to_csv(output_path, index=False)
        
        print(f"✓ Збережено: {output_path}")
        print(f"  Записів: {len(df)}")
        print(f"  Колонок: {len(df.columns)}")
        print()
        
        # Статистика
        print("📊 СТАТИСТИКА:")
        print(f"  • Player1 wins: {df['player1_win'].sum()} ({df['player1_win'].mean():.1%})")
        print(f"  • Player2 wins: {(1-df['player1_win']).sum()} ({(1-df['player1_win']).mean():.1%})")
        print()
        
        if 'surface' in df.columns:
            print("  Покриття:")
            for surf in df['surface'].value_counts().items():
                print(f"    • {surf[0]}: {surf[1]:,} матчів")
        print()
        
        return output_path
    
    def run(self):
        """Повний пайплайн"""
        print()
        print("=" * 70)
        print("🎾 ПІДГОТОВКА TENNIS TRAINING DATA")
        print("=" * 70)
        print()
        
        # 1. Завантажити
        self.load_data()
        
        # 2. Підготувати матчі
        self.prepare_matches()
        
        # 3. Створити фічі
        df_features = self.create_features()
        
        # 4. Зберегти
        output_path = self.save_training_data(df_features)
        
        print("=" * 70)
        print("✅ ГОТОВО!")
        print("=" * 70)
        print()
        print("НАСТУПНИЙ КРОК:")
        print("  python tennis/train_model.py")
        print()
        
        return df_features


def main():
    preparator = TennisTrainingDataPreparator()
    preparator.run()


if __name__ == '__main__':
    main()
