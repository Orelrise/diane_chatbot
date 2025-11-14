"""
Groq API service for communicating with Llama 3.3 70B model.
"""

from typing import Dict, Tuple, Optional
import httpx
from app.config import settings
from app.prompts import DIANE_SYSTEM_PROMPT
from app.utils.logger import logger, mask_sensitive_data


class GroqServiceError(Exception):
    """Custom exception for Groq API errors."""
    pass


class GroqService:
    """Service for interacting with Groq API."""

    def __init__(self):
        """Initialize Groq service with configuration."""
        self.api_url = settings.GROQ_API_URL
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

        # Warn if API key is not configured (but allow service to start)
        if not self.api_key:
            logger.warning("⚠️ GROQ_API_KEY is not configured. API calls will fail until key is added.")

    async def check_connection(self) -> bool:
        """
        Check if Groq API is accessible.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "test"}
                ],
                "max_tokens": 10
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Groq connection check failed: {str(e)}")
            return False

    async def get_response(self, user_message: str) -> Tuple[str, int]:
        """
        Get response from Groq API for a user message.

        Args:
            user_message: User's question

        Returns:
            Tuple of (response_text, tokens_used)

        Raises:
            GroqServiceError: If API call fails
        """
        # Check if API key is configured
        if not self.api_key:
            logger.error("Cannot call Groq API: GROQ_API_KEY is not configured")
            raise GroqServiceError("GROQ_API_KEY is not configured. Please add it to environment variables.")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": DIANE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }

            # Log request (with masked API key)
            logger.info(f"Sending request to Groq API - Model: {self.model}, Temp: {self.temperature}")
            logger.debug(f"User message: {user_message[:100]}...")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )

            # Handle non-200 responses
            if response.status_code != 200:
                error_detail = response.text
                # Mask API key if present in error
                safe_error = mask_sensitive_data(error_detail, self.api_key)
                logger.error(f"Groq API error - Status: {response.status_code}, Detail: {safe_error}")
                raise GroqServiceError(f"API returned status {response.status_code}")

            # Parse response
            data = response.json()

            # Extract response text
            if "choices" not in data or len(data["choices"]) == 0:
                logger.error("Invalid response structure from Groq API")
                raise GroqServiceError("Invalid response structure")

            response_text = data["choices"][0]["message"]["content"]

            # Extract token usage
            tokens_used = 0
            if "usage" in data:
                tokens_used = data["usage"].get("total_tokens", 0)

            logger.info(f"Groq API response received - Tokens used: {tokens_used}")
            logger.debug(f"Response: {response_text[:100]}...")

            return response_text, tokens_used

        except httpx.TimeoutException:
            logger.error("Groq API request timeout")
            raise GroqServiceError("Request timeout")

        except httpx.RequestError as e:
            logger.error(f"Groq API request error: {str(e)}")
            raise GroqServiceError("Network error")

        except Exception as e:
            logger.error(f"Unexpected error in Groq service: {str(e)}")
            raise GroqServiceError(f"Unexpected error: {str(e)}")


# Create singleton instance
groq_service = GroqService()
