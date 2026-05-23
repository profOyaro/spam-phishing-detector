"""Central configuration for the phishing detection platform."""
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    username: str = os.getenv("APP_USERNAME", "admin")
    password: str = os.getenv("APP_PASSWORD", "admin123")
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/detections.db"))
    enable_whois: bool = os.getenv("ENABLE_WHOIS", "false").lower() == "true"
    virustotal_api_key: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    google_safe_browsing_api_key: str = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
    phishtank_api_key: str = os.getenv("PHISHTANK_API_KEY", "")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

settings = Settings()
