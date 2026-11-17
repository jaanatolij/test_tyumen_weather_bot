# Утренняя погода Тюмени в Telegram

Каждое утро около **07:00** (Тюмень, UTC+5) GitHub Actions запрашивает прогноз [Open-Meteo](https://open-meteo.com/) и отправляет короткое сообщение в Telegram.

## Что нужно один раз

### 1. Создать бота

1. Открой [@BotFather](https://t.me/BotFather) в Telegram.
2. Команда `/newbot` → имя и username бота.
3. Сохрани **token** (вид `123456:ABC-DEF...`).

### 2. Написать боту

С аккаунта **jaanatolij** открой своего бота и нажми **Start** / отправь `/start`.  
Без этого бот не сможет прислать первое сообщение.

### 3. Узнать `chat_id`

Вариант А: напиши [@userinfobot](https://t.me/userinfobot) — он покажет твой Id.

Вариант Б: после `/start` боту открой в браузере:

```text
https://api.telegram.org/bot<TOKEN>/getUpdates
```

В ответе найди `"chat":{"id": ...}` — это `TELEGRAM_CHAT_ID`.

### 4. Secrets в GitHub

Репозиторий → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret | Значение |
|--------|----------|
| `TELEGRAM_BOT_TOKEN` | token от BotFather |
| `TELEGRAM_CHAT_ID` | числовой id чата |

Локальные подсказки по именам — в [`.env.example`](.env.example). Реальный `.env` с токенами не коммить.

### 5. Проверка

**Actions** → workflow **Morning weather** → **Run workflow**.  
Если secrets верные, в Telegram придёт сообщение вида:

```text
Доброе утро, Тюмень
Сейчас: −5°, пасмурно
Днём: −2° … ночью −8°
Ветер 3 м/с, влажность 78%
```

Расписание: cron `0 2 * * *` (07:00 по Тюмени). GitHub может сдвинуть scheduled run на несколько минут.

## Локальный запуск

```powershell
$env:TELEGRAM_BOT_TOKEN="..."
$env:TELEGRAM_CHAT_ID="..."
python weather.py
```

Зависимостей нет — только стандартная библиотека Python 3.
