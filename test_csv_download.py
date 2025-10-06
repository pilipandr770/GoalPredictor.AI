"""
Тестирование загрузки CSV датасета из football-data.co.uk
"""
import requests
import pandas as pd
import io

# Попробуем загрузить один CSV для теста
url = 'https://www.football-data.co.uk/mmz4281/2324/E0.csv'

print("🔍 Тестирование загрузки CSV датасета...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    print(f"✅ Ответ получен: {response.status_code}")
    print(f"📊 Размер: {len(response.content)} байт")
    
    # Прочитать CSV
    df = pd.read_csv(io.StringIO(response.text))
    
    print(f"\n📈 Данные загружены:")
    print(f"   Строк: {len(df)}")
    print(f"   Колонок: {len(df.columns)}")
    
    print(f"\n📋 Первые колонки: {list(df.columns[:10])}")
    
    print(f"\n🔢 Первые 3 строки:")
    print(df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']].head(3))
    
    # Проверить наличие результатов
    finished_matches = df[df['FTHG'].notna() & df['FTAG'].notna()]
    print(f"\n✅ Завершенных матчей: {len(finished_matches)}")
    
except Exception as e:
    print(f"❌ Ошибка: {str(e)}")
    import traceback
    traceback.print_exc()
