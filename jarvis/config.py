"""Environment-backed configuration for JARVIS."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    wake_word: str = os.getenv("WAKE_WORD", "jarvis").strip().lower()
    voice_rate: int = int(os.getenv("VOICE_RATE", "145"))
    voice_volume: float = float(os.getenv("VOICE_VOLUME", "1.0"))
    voice_name: str = os.getenv("VOICE_NAME", "").strip()
    voice_id: str = os.getenv("VOICE_ID", "").strip()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    vosk_model_path: str = os.getenv("VOSK_MODEL_PATH", "").strip()


settings = Settings()
