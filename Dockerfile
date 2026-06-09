FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY bot /app/bot
COPY prompts /app/prompts

RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .

CMD ["python", "-m", "bot.main"]
