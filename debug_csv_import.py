"""
Отладка импорта CSV данных
"""
import requests
import pandas as pd
import io
from datetime import datetime

url = 'https://www.football-data.co.uk/mmz4281/2324/E0.csv'

print("🔍 Отладка импорта CSV\n")

# Загрузить CSV
response = requests.get(url, timeout=30)
df = pd.read_csv(io.StringIO(response.text))

print(f"✅ Загружено строк: {len(df)}")
print(f"✅ Колонки: {list(df.columns[:15])}\n")

# Проверить первую строку
row = df.iloc[0]

print("📋 Первая строка:")
print(f"   Date: {row['Date']}")
print(f"   HomeTeam: {row['HomeTeam']}")
print(f"   AwayTeam: {row['AwayTeam']}")
print(f"   FTHG: {row['FTHG']} (тип: {type(row['FTHG'])})")
print(f"   FTAG: {row['FTAG']} (тип: {type(row['FTAG'])})")
print(f"   FTR: {row['FTR']}")

# Проверить NaN
print(f"\n🔍 Проверка NaN:")
print(f"   FTHG is NaN: {pd.isna(row['FTHG'])}")
print(f"   FTAG is NaN: {pd.isna(row['FTAG'])}")

# Парсинг даты
formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']

print(f"\n📅 Парсинг даты: '{row['Date']}'")
for fmt in formats:
    try:
        date = datetime.strptime(str(row['Date']), fmt)
        print(f"   ✅ Формат {fmt}: {date}")
        break
    except:
        print(f"   ❌ Формат {fmt}: не подошел")

# Подсчет валидных строк
valid_rows = df[(df['FTHG'].notna()) & (df['FTAG'].notna())]
print(f"\n📊 Валидных строк с результатами: {len(valid_rows)}")

# Показать несколько примеров
print(f"\n📝 Примеры данных:")
for i in range(min(5, len(valid_rows))):
    row = valid_rows.iloc[i]
    print(f"   {row['Date']}: {row['HomeTeam']} {row['FTHG']}-{row['FTAG']} {row['AwayTeam']}")
