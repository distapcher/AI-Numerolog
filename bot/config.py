from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT_PATH = BASE_DIR / "prompts" / "decryption_ru.txt"


@dataclass(frozen=True)
class Settings:
    bot_token: str
    rapidapi_key: str
    rapidapi_host: str
    calc_service_url: str
    openai_api_key: str | None
    openai_base_url: str
    openai_model: str
    prompt_path: Path
    ai_max_tokens: int


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "").strip()

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set")
    if not rapidapi_key:
        raise ValueError("RAPIDAPI_KEY is not set")

    openai_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    prompt_path = Path(os.getenv("PROMPT_PATH", str(DEFAULT_PROMPT_PATH)))

    return Settings(
        bot_token=bot_token,
        rapidapi_key=rapidapi_key,
        rapidapi_host=os.getenv(
            "RAPIDAPI_HOST", "numerology-api4.p.rapidapi.com"
        ).strip(),
        calc_service_url=os.getenv(
            "CALC_SERVICE_URL", "http://127.0.0.1:8791"
        ).strip().rstrip("/"),
        openai_api_key=openai_key,
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "deepseek-chat").strip(),
        prompt_path=prompt_path,
        ai_max_tokens=int(os.getenv("AI_MAX_TOKENS", "12000")),
    )
