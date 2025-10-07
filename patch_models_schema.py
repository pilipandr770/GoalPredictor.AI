"""
Патч для добавления __table_args__ со схемой во все модели
Запустить один раз для миграции на schema-aware модели
"""
import os
import re

SCHEMA_NAME = os.getenv('DATABASE_SCHEMA', 'goalpredictor')

models_file = 'models.py'

# Читаем файл
with open(models_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Паттерн для поиска классов моделей
pattern = r'(class \w+\([^)]+\):[\s\S]*?__tablename__ = [\'"](\w+)[\'"])'

def add_table_args(match):
    """Добавить __table_args__ после __tablename__"""
    full_match = match.group(0)
    tablename = match.group(2)
    
    # Проверяем, есть ли уже __table_args__
    if '__table_args__' in full_match:
        return full_match
    
    # Добавляем __table_args__
    replacement = f"{full_match}\n    __table_args__ = {{'schema': '{SCHEMA_NAME}'}}"
    return replacement

# Применяем патч
new_content = re.sub(pattern, add_table_args, content)

# Сохраняем резервную копию
with open(f'{models_file}.backup', 'w', encoding='utf-8') as f:
    f.write(content)

# Записываем новый файл
with open(models_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ Патч применён к {models_file}")
print(f"📦 Backup сохранён в {models_file}.backup")
print(f"📊 Схема: {SCHEMA_NAME}")
