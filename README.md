# AI-Numerolog

Telegram-бот нумеролога: квадрат Пифагора + расшифровка через DeepSeek.

## Возможности

- Квадрат Пифагора через сервис расчёта на VPS (`numerolog-calc`, порт 8791)
- Числа через RapidAPI Numerology API4 (destiny, soul urge, personality и др.)
- Глубокий ИИ-анализ по 10 разделам (предназначение, таланты, финансы, дело жизни и др.)

## Быстрый старт (локально)

```bash
cp .env.example .env
# заполните BOT_TOKEN, RAPIDAPI_KEY, OPENAI_API_KEY

python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m bot.main
```

## Docker (VPS)

```bash
cp .env.example .env
# заполните .env
docker compose up -d --build
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram-бота |
| `RAPIDAPI_KEY` | Ключ RapidAPI |
| `RAPIDAPI_HOST` | Хост API (по умолчанию `numerology-api4.p.rapidapi.com`) |
| `CALC_SERVICE_URL` | URL сервиса квадрата Пифагора (`http://127.0.0.1:8791`) |
| `OPENAI_API_KEY` | Ключ DeepSeek |
| `OPENAI_BASE_URL` | `https://api.deepseek.com/v1` |
| `OPENAI_MODEL` | `deepseek-chat` |

## Деплой на VPS

```bash
# Первичная настройка на сервере
REPO_URL=https://github.com/distapcher/AI-Numerolog.git DEPLOY_DIR=/opt/AI-Numerolog bash scripts/server-setup.sh

# Обновление
./scripts/deploy.sh "описание изменений"
```

## Команды бота

- `/start` — приветствие
- `/analyze` — начать нумерологический анализ
- `/help` — справка
