"""
Скрипт загрузки данных с Kaggle
Загружает датасет с футбольными матчами топ-5 лиг (2024-2025)
"""
import os
import kagglehub
import pandas as pd
import shutil
from pathlib import Path


class KaggleDataLoader:
    """
    Загрузчик данных с Kaggle
    """
    
    def __init__(self):
        self.dataset_name = "tarekmasryo/football-matches-20242025-top-5-leagues"
        self.data_dir = Path("data")
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Создать директории
        self.data_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
    
    def download_dataset(self):
        """
        Скачать датасет с Kaggle
        """
        print("🔄 Загрузка датасета с Kaggle...")
        print(f"   Датасет: {self.dataset_name}")
        
        try:
            # Скачать датасет
            path = kagglehub.dataset_download(self.dataset_name)
            print(f"✅ Датасет загружен в: {path}")
            
            # Скопировать файлы в data/raw
            self._copy_files(path)
            
            return path
            
        except Exception as e:
            print(f"❌ Ошибка загрузки датасета: {e}")
            print("\n⚠️  Убедитесь, что:")
            print("   1. Установлен kagglehub: pip install kagglehub")
            print("   2. Настроен Kaggle API: https://www.kaggle.com/docs/api")
            print("   3. Файл kaggle.json находится в ~/.kaggle/")
            return None
    
    def _copy_files(self, source_path):
        """
        Скопировать файлы из кеша Kaggle в data/raw
        """
        print("📂 Копирование файлов в data/raw...")
        
        source = Path(source_path)
        
        # Найти все CSV файлы
        csv_files = list(source.glob("*.csv"))
        
        if not csv_files:
            # Попробовать найти в подпапках
            csv_files = list(source.rglob("*.csv"))
        
        if csv_files:
            for csv_file in csv_files:
                dest = self.raw_dir / csv_file.name
                shutil.copy2(csv_file, dest)
                print(f"   ✅ {csv_file.name} → data/raw/")
        else:
            print("   ⚠️  CSV файлы не найдены")
    
    def load_data(self):
        """
        Загрузить данные из CSV файлов
        """
        print("\n📊 Загрузка данных...")
        
        csv_files = list(self.raw_dir.glob("*.csv"))
        
        if not csv_files:
            print("❌ CSV файлы не найдены в data/raw/")
            print("   Запустите download_dataset() сначала")
            return None
        
        # Загрузить все CSV файлы
        dataframes = []
        
        for csv_file in csv_files:
            print(f"   📄 Загрузка {csv_file.name}...")
            try:
                df = pd.read_csv(csv_file)
                dataframes.append(df)
                print(f"      ✅ {len(df)} строк, {len(df.columns)} столбцов")
            except Exception as e:
                print(f"      ❌ Ошибка: {e}")
        
        if not dataframes:
            return None
        
        # Объединить все датафреймы
        if len(dataframes) == 1:
            combined_df = dataframes[0]
        else:
            print("\n🔗 Объединение датафреймов...")
            combined_df = pd.concat(dataframes, ignore_index=True)
        
        print(f"\n✅ Загружено всего: {len(combined_df)} матчей")
        print(f"   Столбцы: {', '.join(combined_df.columns[:10])}...")
        
        return combined_df
    
    def prepare_training_data(self, df):
        """
        Подготовить данные для обучения модели
        """
        print("\n🔧 Подготовка данных для обучения...")
        
        # Базовая информация
        print(f"   Размер датасета: {df.shape}")
        print(f"   Столбцы: {list(df.columns)}")
        
        # Проверить наличие необходимых столбцов
        required_columns = ['Date', 'HomeTeam', 'AwayTeam']
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            print(f"\n⚠️  Отсутствуют столбцы: {missing}")
            print("   Проверяем альтернативные названия...")
            
            # Показать все столбцы для анализа
            print(f"\n   Доступные столбцы:")
            for i, col in enumerate(df.columns, 1):
                print(f"      {i}. {col}")
        
        # Сохранить подготовленные данные
        output_file = self.processed_dir / "football_matches.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ Данные сохранены в: {output_file}")
        
        return df
    
    def get_dataset_info(self, df):
        """
        Получить информацию о датасете
        """
        print("\n📊 Информация о датасете:")
        print(f"   Всего матчей: {len(df)}")
        print(f"   Столбцов: {len(df.columns)}")
        print(f"   Памяти: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Проверить пропущенные значения
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"\n   ⚠️  Пропущенные значения:")
            for col, count in missing[missing > 0].items():
                print(f"      {col}: {count} ({count/len(df)*100:.1f}%)")
        
        # Показать примеры данных
        print(f"\n   Примеры данных:")
        print(df.head(3).to_string())
        
        return df.describe()


def main():
    """
    Основная функция для загрузки и подготовки данных
    """
    print("⚽ GoalPredictor.AI - Загрузка данных с Kaggle\n")
    
    loader = KaggleDataLoader()
    
    # Шаг 1: Загрузить датасет
    path = loader.download_dataset()
    
    if path is None:
        print("\n❌ Загрузка не удалась")
        return
    
    # Шаг 2: Загрузить данные в DataFrame
    df = loader.load_data()
    
    if df is None:
        print("\n❌ Не удалось загрузить данные")
        return
    
    # Шаг 3: Подготовить данные
    df = loader.prepare_training_data(df)
    
    # Шаг 4: Показать информацию
    loader.get_dataset_info(df)
    
    print("\n🎉 Готово! Данные подготовлены для обучения модели")
    print(f"   Файл: data/processed/football_matches.csv")
    print(f"\n   Следующий шаг: python ml/train.py")


if __name__ == "__main__":
    main()
