import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    analyzer: str
    gemini_api_key: str
    gemini_model: str
    gmail_user: str
    gmail_app_password: str
    from_name: str

    @property
    def smtp_host(self) -> str:
        return "smtp.gmail.com"

    @property
    def smtp_port(self) -> int:
        return 587


def _load() -> Settings:
    return Settings(
        analyzer=os.getenv("ANALYZER", "mock").strip().lower(),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        gmail_user=os.getenv("GMAIL_USER", "").strip(),
        gmail_app_password=os.getenv("GMAIL_APP_PASSWORD", "").strip(),
        from_name=os.getenv("FROM_NAME", "MatchTrackr").strip(),
    )


settings = _load()
