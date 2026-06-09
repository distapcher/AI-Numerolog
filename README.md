# AI-Numerolog

Telegram-бот нумеролога: квадрат Пифагора + расшифровка через DeepSeek.

## Возможности

- Полный нумерологический профиль через сервис `numerolog-calc` на VPS
- Дополнительные числа через RapidAPI Numerology API4 (destiny, soul urge и др.)
- Глубокий ИИ-анализ по 20 разделам (промпт `numerolog_encryption_ext.txt`)

## Архитектура на VPS

На сервере работают **два Docker-контейнера** в одной сети:

```
Telegram → ai-numerolog (бот)
              ├→ numerolog-calc:8791  (расчёты, внутри VPS)
              ├→ numerology-api4      (RapidAPI, интернет)
              └→ DeepSeek API         (расшифровка, интернет)
```

`127.0.0.1` в продакшене **не используется**. Бот обращается к сервису расчёта по имени `http://numerolog-calc:8791` — это внутренний адрес Docker на VPS, не ваш компьютер.

Локальная машина нужна только для разработки и `git push`. Продакшен — только VPS.

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
| `CALC_SERVICE_URL` | URL сервиса расчёта (на VPS в Docker: `http://numerolog-calc:8791`, задаётся в compose) |
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
