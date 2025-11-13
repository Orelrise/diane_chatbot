"""
Configuration module for Diane API.
Loads environment variables and provides configuration constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Information
    APP_NAME: str = "Diane Herborist API"
    APP_VERSION: str = "1.0.0"

    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    MODEL: str = os.getenv("MODEL", "llama-3.3-70b-versatile")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "800"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # Allow all origins for WordPress widget

    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return True

    @classmethod
    def mask_api_key(cls) -> str:
        """Return masked version of API key for logging."""
        if not cls.GROQ_API_KEY:
            return "NOT_SET"
        return f"{cls.GROQ_API_KEY[:7]}...***{cls.GROQ_API_KEY[-4:]}"


# Create settings instance
settings = Settings()
