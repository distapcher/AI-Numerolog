# AI-Numerolog

Telegram-бот нумеролога: квадрат Пифагора + расшифровка через DeepSeek.

## Возможности

- Нумерологический профиль через RapidAPI [The Numerology API](https://rapidapi.com/dakidarts-dakidarts-default/api/the-numerology-api)
- Квадрат Пифагора (школа Александрова) — локальный расчёт (на RapidAPI нет эндпоинта psychomatrix)
- Глубокий ИИ-анализ по 20 разделам (промпт `numerolog_encryption_ext.txt`)

## Архитектура на VPS

На сервере работает **один Docker-контейнер**:

```
Telegram → ai-numerolog (бот)
              ├→ the-numerology-api.p.rapidapi.com  (числа, RapidAPI)
              └→ DeepSeek API                     (расшифровка)
```

Квадрат Пифагора считается внутри бота (библиотека `numerology_calc`), остальные числа — через RapidAPI.

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
| `RAPIDAPI_HOST` | Хост API (по умолчанию `the-numerology-api.p.rapidapi.com`) |
| `OPENAI_API_KEY` | Ключ DeepSeek |
| `OPENAI_BASE_URL` | `https://api.deepseek.com/v1` |
| `OPENAI_MODEL` | `deepseek-chat` |

## Деплой на VPS

Все изменения сначала попадают в GitHub, затем на сервер — **не копируйте файлы на VPS вручную**.

```bash
# Первичная настройка на сервере (один раз)
REPO_URL=https://github.com/distapcher/AI-Numerolog.git DEPLOY_DIR=/opt/AI-Numerolog bash scripts/server-setup.sh

# Обычное обновление: commit → push → pull на VPS → перезапуск Docker
./scripts/deploy.sh "описание изменений"
```

Скрипт `scripts/deploy.sh` делает `git push` и на сервере `git pull --ff-only` + `docker compose up -d --build`.

## Команды бота

- `/start` — приветствие
- `/analyze` — начать нумерологический анализ
- `/help` — справка
