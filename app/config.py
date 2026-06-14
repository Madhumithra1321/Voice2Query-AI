import os
from pathlib import Path


def find_dotenv_file() -> Path | None:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            return env_path
    return None


def load_dotenv_file() -> None:
    env_path = find_dotenv_file()
    if env_path is None:
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not os.getenv(key):
            os.environ[key] = value


load_dotenv_file()


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


DATABASE_URL = get_env(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:M%40dhumithra3677@localhost:5432/voice2query",
)

TEXT_TO_SQL_PROVIDER = get_env("TEXT_TO_SQL_PROVIDER", "ollama").lower()
OLLAMA_URL = get_env("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "llama3:latest")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_MODEL = get_env("OPENAI_MODEL", "gpt-4.1-mini")

SPEECHMATICS_API_KEY = get_env("SPEECHMATICS_API_KEY")
SPEECHMATICS_LANGUAGE = get_env("SPEECHMATICS_LANGUAGE", "en")
SPEECHMATICS_BATCH_URL = get_env(
    "SPEECHMATICS_BATCH_URL",
    "https://asr.api.speechmatics.com/v2",
)
