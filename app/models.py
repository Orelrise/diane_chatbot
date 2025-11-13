"""
Pydantic models for request and response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""

    message: str = Field(..., min_length=1, max_length=1000, description="User's question")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID (UUID v4 format)"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Optional WordPress user ID"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Quelles plantes pour le sommeil ?",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "wp_user_123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for /chat endpoint."""

    response: str = Field(..., description="HTML-formatted response from Diane")
    conversation_id: str = Field(..., description="Conversation UUID")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    is_valid_topic: bool = Field(..., description="Whether the question was about herbalism")
    tokens_used: int = Field(..., description="Number of tokens used in API call")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "<p>Pour améliorer le sommeil, plusieurs plantes sont efficaces :</p><ul><li><strong>Valériane</strong> : réduit le temps d'endormissement</li></ul>",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-13T14:30:00Z",
                "is_valid_topic": True,
                "tokens_used": 380
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Service temporairement indisponible",
                "detail": "Erreur lors de la connexion à l'API Groq"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Overall status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "Diane Herborist API",
                "version": "1.0.0"
            }
        }


class HealthCheckResponse(BaseModel):
    """Detailed health check response model."""

    api_status: str = Field(..., description="API status")
    groq_connection: bool = Field(..., description="Groq API connection status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "api_status": "ok",
                "groq_connection": True,
                "timestamp": "2025-11-13T14:30:00Z"
            }
        }


def generate_conversation_id() -> str:
    """Generate a new UUID v4 for conversation tracking."""
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat() + "Z"
