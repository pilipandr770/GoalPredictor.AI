# 🔑 Получение API ключа Football-Data.org

## Бесплатный доступ к футбольным данным

Football-Data.org предоставляет **бесплатный** доступ к футбольным данным с лимитами:
- ⏱️ 10 запросов в минуту
- 📅 100 запросов в день
- ⚽ Топ-5 европейских лиг: Премьер-лига, Ла Лига, Бундеслига, Серия A, Лига 1

---

## 🚀 Регистрация (2 минуты)

### Шаг 1: Перейти на сайт
Откройте: [https://www.football-data.org/client/register](https://www.football-data.org/client/register)

### Шаг 2: Заполнить форму регистрации
- **Name**: Ваше имя
- **Email**: Рабочий email
- **Purpose**: `Educational / Personal Project`
- **Description**: `Building a football prediction platform using machine learning`

### Шаг 3: Подтвердить email
После регистрации проверьте почту и подтвердите аккаунт.

### Шаг 4: Получить API ключ
После входа в аккаунт вы увидите ваш **API Token** на главной странице:

```
Your API Token: eaf273a5cb0f4d3fbb03bed03ae814a1
```

---

## ⚙️ Настройка в GoalPredictor.AI

### 1. Добавить в `.env`:

```env
FOOTBALL_API_PROVIDER=football-data-org
FOOTBALL_DATA_ORG_KEY=eaf273a5cb0f4d3fbb03bed03ae814a1
```

### 2. Проверить работу:

```powershell
python -m services.football_api
```

Вы должны увидеть:
```
✅ Используется Football-Data.org API (бесплатный, 10 запросов/мин)
📅 Матчи на сегодня:
   Arsenal vs Chelsea
   ...
```

---

## 📊 Доступные лиги

Система поддерживает следующие лиги:

| Лига | Код | Название |
|------|-----|----------|
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Премьер-лига | `PL` | Premier League |
| 🇪🇸 Ла Лига | `PD` | Primera División |
| 🇩🇪 Бундеслига | `BL1` | Bundesliga |
| 🇮🇹 Серия A | `SA` | Serie A |
| 🇫🇷 Лига 1 | `FL1` | Ligue 1 |

---

## ⚠️ Лимиты бесплатного плана

| Параметр | Лимит |
|----------|-------|
| Запросов/минуту | 10 |
| Запросов/день | 100 |
| Доступных лиг | 5 топовых |
| История данных | 2+ года |

### Рекомендации:
- 🔄 Используйте кеширование для оптимизации запросов
- ⏰ Планируйте автоматические обновления на ночное время (меньше конкуренции)
- 📊 Запрашивайте только необходимые данные

---

## 🔄 Альтернатива: RapidAPI

Если вам нужно больше запросов, вы можете использовать **RapidAPI** (платный):

1. Зарегистрируйтесь на: [https://rapidapi.com/api-sports/api/api-football](https://rapidapi.com/api-sports/api/api-football)
2. Выберите подходящий план ($0-$149/месяц)
3. Настройте `.env`:

```env
FOOTBALL_API_PROVIDER=rapidapi
FOOTBALL_API_KEY=your-rapidapi-key
FOOTBALL_API_HOST=api-football-v1.p.rapidapi.com
```

---

## ❓ FAQ

**Q: Сколько стоит Football-Data.org?**  
A: Бесплатно навсегда! Лимиты: 10 запросов/мин, 100/день.

**Q: Достаточно ли 100 запросов в день?**  
A: Для разработки и тестирования — да! Для production рекомендуется использовать кеширование или платный план.

**Q: Можно ли использовать оба провайдера одновременно?**  
A: Да, просто измените `FOOTBALL_API_PROVIDER` в `.env` для переключения.

**Q: Что делать, если превышен лимит?**  
A: Система автоматически обработает ошибку 429 (Too Many Requests). Подождите 1 минуту и попробуйте снова.

---

## 🛠️ Troubleshooting

### Ошибка 403 Forbidden
- Проверьте правильность API ключа в `.env`
- Убедитесь, что email подтвержден

### Ошибка 429 Too Many Requests
- Превышен лимит 10 запросов/мин
- Подождите 60 секунд

### Нет данных для матчей
- Проверьте формат даты (YYYY-MM-DD)
- Убедитесь, что лига поддерживается

---

## 📚 Полезные ссылки

- [Документация API](https://www.football-data.org/documentation/quickstart)
- [Список доступных лиг](https://www.football-data.org/documentation/api)
- [Примеры запросов](https://www.football-data.org/documentation/examples)

---

**🎉 Готово! Теперь у вас есть бесплатный доступ к футбольным данным!**
