"""
Загрузка расширенного датасета с Kaggle с детальной статистикой матчей
Датасет содержит удары, корнеры, фолы, владение мячом и многое другое
"""
import kagglehub
import pandas as pd
import os
from pathlib import Path
import shutil


class EnhancedKaggleDataLoader:
    """Загрузчик расширенных датасетов для улучшения точности модели"""
    
    def __init__(self):
        self.data_dir = Path('data')
        self.raw_dir = self.data_dir / 'raw'
        self.processed_dir = self.data_dir / 'processed'
        
        # Создать директории
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def download_european_football_dataset(self):
        """
        Загрузить большой датасет европейского футбола
        Содержит статистику за несколько сезонов с детальными метриками
        """
        print("📥 Загрузка расширенного датасета европейского футбола...")
        print("   Датасет: hugomathien/soccer")
        
        try:
            # Загрузить датасет с Kaggle
            path = kagglehub.dataset_download("hugomathien/soccer")
            print(f"✅ Датасет загружен: {path}")
            
            # Найти файл database.sqlite
            dataset_path = Path(path)
            sqlite_file = None
            
            for file in dataset_path.rglob("*.sqlite"):
                sqlite_file = file
                break
            
            if sqlite_file:
                print(f"📂 Найден файл: {sqlite_file}")
                
                # Скопировать в нашу директорию
                target_path = self.raw_dir / "european_football.sqlite"
                shutil.copy2(sqlite_file, target_path)
                print(f"💾 Сохранено в: {target_path}")
                
                return str(target_path)
            else:
                print("❌ SQLite файл не найден!")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None
    
    def download_football_data_europe(self):
        """
        Загрузить датасет football-data.co.uk с детальной статистикой
        Содержит удары, корнеры, карточки, коэффициенты букмекеров
        """
        print("\n📥 Загрузка датасета Football-Data.co.uk...")
        print("   Датасет: saife245/english-premier-league")
        
        try:
            path = kagglehub.dataset_download("saife245/english-premier-league")
            print(f"✅ Датасет загружен: {path}")
            
            # Найти CSV файлы
            dataset_path = Path(path)
            csv_files = list(dataset_path.rglob("*.csv"))
            
            if csv_files:
                print(f"📂 Найдено CSV файлов: {len(csv_files)}")
                
                # Объединить все CSV в один DataFrame
                all_data = []
                for csv_file in csv_files:
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8')
                        all_data.append(df)
                        print(f"   ✓ Загружено: {csv_file.name} ({len(df)} матчей)")
                    except Exception as e:
                        print(f"   ✗ Ошибка в {csv_file.name}: {e}")
                
                if all_data:
                    combined_df = pd.concat(all_data, ignore_index=True)
                    
                    # Сохранить
                    target_path = self.raw_dir / "premier_league_detailed.csv"
                    combined_df.to_csv(target_path, index=False)
                    print(f"💾 Объединенный датасет сохранен: {target_path}")
                    print(f"   Всего матчей: {len(combined_df)}")
                    print(f"   Колонок: {len(combined_df.columns)}")
                    
                    return str(target_path)
            
            return None
                
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None
    
    def download_all_european_leagues(self):
        """
        Загрузить датасет со всеми европейскими лигами
        Содержит топ-5 лиг за несколько сезонов
        """
        print("\n📥 Загрузка датасета всех европейских лиг...")
        print("   Датасет: sanjeetsinghnaik/most-recent-soccer-scores-stats")
        
        try:
            path = kagglehub.dataset_download("sanjeetsinghnaik/most-recent-soccer-scores-stats")
            print(f"✅ Датасет загружен: {path}")
            
            # Найти CSV файлы
            dataset_path = Path(path)
            csv_files = list(dataset_path.rglob("*.csv"))
            
            if csv_files:
                print(f"📂 Найдено CSV файлов: {len(csv_files)}")
                
                all_data = []
                for csv_file in csv_files:
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8', on_bad_lines='skip')
                        if len(df) > 0:
                            all_data.append(df)
                            print(f"   ✓ {csv_file.name}: {len(df)} матчей")
                    except Exception as e:
                        print(f"   ✗ Ошибка: {e}")
                
                if all_data:
                    combined_df = pd.concat(all_data, ignore_index=True)
                    target_path = self.raw_dir / "all_european_leagues.csv"
                    combined_df.to_csv(target_path, index=False)
                    print(f"💾 Сохранено: {target_path}")
                    print(f"   Всего матчей: {len(combined_df)}")
                    
                    return str(target_path)
            
            return None
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def load_and_analyze_dataset(self, filepath):
        """Загрузить и проанализировать датасет"""
        print(f"\n📊 Анализ датасета: {filepath}")
        
        try:
            df = pd.read_csv(filepath, on_bad_lines='skip')
            
            print(f"\n✅ Загружено успешно:")
            print(f"   Строк: {len(df)}")
            print(f"   Колонок: {len(df.columns)}")
            
            print(f"\n📋 Доступные колонки:")
            for i, col in enumerate(df.columns, 1):
                non_null = df[col].notna().sum()
                percent = (non_null / len(df)) * 100
                print(f"   {i:2}. {col:30} - {non_null:6} значений ({percent:.1f}%)")
            
            print(f"\n📈 Статистика:")
            print(df.describe())
            
            print(f"\n🔍 Первые 3 строки:")
            print(df.head(3))
            
            return df
            
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None


def main():
    """Главная функция для загрузки датасетов"""
    print("="*70)
    print("🚀 ЗАГРУЗКА РАСШИРЕННЫХ ДАТАСЕТОВ ДЛЯ УЛУЧШЕНИЯ МОДЕЛИ")
    print("="*70)
    
    loader = EnhancedKaggleDataLoader()
    
    # Попробовать загрузить разные датасеты
    datasets = []
    
    # 1. Premier League с детальной статистикой
    print("\n" + "="*70)
    print("ДАТАСЕТ 1: PREMIER LEAGUE С ДЕТАЛЬНОЙ СТАТИСТИКОЙ")
    print("="*70)
    path1 = loader.download_football_data_europe()
    if path1:
        df1 = loader.load_and_analyze_dataset(path1)
        if df1 is not None:
            datasets.append(('premier_league_detailed', df1))
    
    # 2. Все европейские лиги
    print("\n" + "="*70)
    print("ДАТАСЕТ 2: ВСЕ ЕВРОПЕЙСКИЕ ЛИГИ")
    print("="*70)
    path2 = loader.download_all_european_leagues()
    if path2:
        df2 = loader.load_and_analyze_dataset(path2)
        if df2 is not None:
            datasets.append(('all_european_leagues', df2))
    
    # 3. Европейский футбол (SQLite база)
    print("\n" + "="*70)
    print("ДАТАСЕТ 3: EUROPEAN FOOTBALL DATABASE")
    print("="*70)
    path3 = loader.download_european_football_dataset()
    if path3:
        print("✅ SQLite база данных загружена!")
        print("   Для работы с ней используйте sqlite3 библиотеку")
    
    # Итоги
    print("\n" + "="*70)
    print("📊 ИТОГИ ЗАГРУЗКИ")
    print("="*70)
    print(f"Успешно загружено датасетов: {len(datasets)}")
    for name, df in datasets:
        print(f"  ✓ {name}: {len(df)} матчей, {len(df.columns)} колонок")
    
    if datasets:
        print("\n✅ Датасеты готовы для обучения улучшенных моделей!")
    else:
        print("\n⚠️  Не удалось загрузить ни один датасет.")
        print("    Будем использовать существующий датасет.")
    
    return datasets


if __name__ == '__main__':
    main()
