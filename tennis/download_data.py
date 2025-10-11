"""
Tennis Data Downloader
Downloads ATP match data from Jeff Sackmann's GitHub repository
"""
import pandas as pd
import os
from pathlib import Path


class TennisDataDownloader:
    """Download ATP tennis data from GitHub"""
    
    BASE_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/"
    
    def __init__(self, output_dir='tennis/data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def download_matches(self, years=None):
        """
        Download ATP matches for specified years
        
        Args:
            years: List of years (e.g. [2020, 2021, 2022, 2023, 2024])
        """
        if years is None:
            years = [2020, 2021, 2022, 2023, 2024]
        
        print("=" * 70)
        print("🎾 ЗАВАНТАЖЕННЯ ATP МАТЧІВ")
        print("=" * 70)
        print()
        
        all_matches = []
        
        for year in years:
            print(f"📥 Завантаження {year}...")
            try:
                url = f"{self.BASE_URL}atp_matches_{year}.csv"
                df = pd.read_csv(url)
                
                print(f"  ✓ {len(df)} матчів завантажено")
                all_matches.append(df)
                
            except Exception as e:
                print(f"  ❌ Помилка: {e}")
        
        if all_matches:
            # Об'єднати всі роки
            combined = pd.concat(all_matches, ignore_index=True)
            
            output_path = self.output_dir / 'atp_matches_combined.csv'
            combined.to_csv(output_path, index=False)
            
            print()
            print(f"✅ Всього матчів: {len(combined)}")
            print(f"💾 Збережено: {output_path}")
            print()
            
            return combined
        
        return None
    
    def download_rankings(self):
        """Download current ATP rankings"""
        print("📥 Завантаження рейтингів ATP...")
        
        try:
            url = f"{self.BASE_URL}atp_rankings_current.csv"
            df = pd.read_csv(url)
            
            output_path = self.output_dir / 'atp_rankings.csv'
            df.to_csv(output_path, index=False)
            
            print(f"  ✓ {len(df)} гравців у рейтингу")
            print(f"  💾 {output_path}")
            print()
            
            return df
            
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
            return None
    
    def download_players(self):
        """Download ATP players database"""
        print("📥 Завантаження бази гравців...")
        
        try:
            url = f"{self.BASE_URL}atp_players.csv"
            df = pd.read_csv(url)
            
            output_path = self.output_dir / 'atp_players.csv'
            df.to_csv(output_path, index=False)
            
            print(f"  ✓ {len(df)} гравців в базі")
            print(f"  💾 {output_path}")
            print()
            
            return df
            
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
            return None
    
    def download_all(self):
        """Download everything"""
        print()
        print("=" * 70)
        print("🎾 ЗАВАНТАЖЕННЯ ВСІХ ATP ДАНИХ")
        print("=" * 70)
        print()
        
        # Matches 2020-2024
        matches = self.download_matches([2020, 2021, 2022, 2023, 2024])
        
        # Rankings
        rankings = self.download_rankings()
        
        # Players
        players = self.download_players()
        
        print("=" * 70)
        print("✅ ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО")
        print("=" * 70)
        print()
        
        if matches is not None:
            print("📊 СТАТИСТИКА:")
            print(f"  • Матчів: {len(matches):,}")
            print(f"  • Турнірів: {matches['tourney_name'].nunique()}")
            print(f"  • Період: {matches['tourney_date'].min()} - {matches['tourney_date'].max()}")
            print()
            
            # Покриття корту
            if 'surface' in matches.columns:
                print("  Покриття:")
                for surface, count in matches['surface'].value_counts().items():
                    print(f"    • {surface}: {count:,} матчів")
            print()
        
        return {
            'matches': matches,
            'rankings': rankings,
            'players': players
        }


def main():
    """Головна функція"""
    downloader = TennisDataDownloader()
    data = downloader.download_all()
    
    print("🚀 Дані готові для підготовки training dataset!")
    print("   Наступний крок: python tennis/prepare_training_data.py")
    print()


if __name__ == '__main__':
    main()
