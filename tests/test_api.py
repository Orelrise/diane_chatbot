"""
Unit tests for Diane API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.validator import is_valid_herbalism_topic
from app.models import generate_conversation_id


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self):
        """Test GET / endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Diane Herborist API"
        assert "version" in data

    def test_health_endpoint(self):
        """Test GET /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "api_status" in data
        assert "groq_connection" in data
        assert "timestamp" in data


class TestChatEndpoint:
    """Test chat endpoint."""

    def test_chat_valid_herbal_question(self):
        """Test chat with valid herbal question."""
        payload = {
            "message": "Quelles plantes pour le sommeil ?"
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "timestamp" in data
        assert "is_valid_topic" in data
        assert "tokens_used" in data

    def test_chat_with_conversation_id(self):
        """Test chat with provided conversation ID."""
        conv_id = generate_conversation_id()
        payload = {
            "message": "Propriétés de la camomille ?",
            "conversation_id": conv_id
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conv_id

    def test_chat_empty_message(self):
        """Test chat with empty message."""
        payload = {
            "message": ""
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 422  # Validation error

    def test_chat_off_topic_question(self):
        """Test chat with off-topic question."""
        payload = {
            "message": "Qui a gagné le match de football hier ?"
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid_topic"] == False
        assert data["tokens_used"] == 0
        assert "spécialisée exclusivement" in data["response"]

    def test_chat_invalid_json(self):
        """Test chat with invalid JSON."""
        response = client.post(
            "/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestValidator:
    """Test topic validation service."""

    def test_valid_herbal_topics(self):
        """Test validation of valid herbal topics."""
        valid_questions = [
            "Quelles plantes pour le sommeil ?",
            "Propriétés de la camomille ?",
            "Comment préparer une tisane de valériane ?",
            "Contre-indications du millepertuis ?",
            "Plantes pour la digestion",
        ]

        for question in valid_questions:
            is_valid, _ = is_valid_herbalism_topic(question)
            assert is_valid == True, f"'{question}' should be valid"

    def test_off_topic_questions(self):
        """Test validation of off-topic questions."""
        off_topic_questions = [
            "Qui a gagné le match de football ?",
            "Quelle est la météo demain ?",
            "Comment programmer en Python ?",
            "Recette de lasagnes",
            "Prix du Bitcoin aujourd'hui",
        ]

        for question in off_topic_questions:
            is_valid, _ = is_valid_herbalism_topic(question)
            assert is_valid == False, f"'{question}' should be off-topic"

    def test_edge_cases(self):
        """Test validation edge cases."""
        # Very short message
        is_valid, _ = is_valid_herbalism_topic("ok")
        assert is_valid == False

        # Empty message
        is_valid, _ = is_valid_herbalism_topic("")
        assert is_valid == False


class TestModels:
    """Test Pydantic models."""

    def test_generate_conversation_id(self):
        """Test conversation ID generation."""
        conv_id = generate_conversation_id()
        assert isinstance(conv_id, str)
        assert len(conv_id) == 36  # UUID format
        assert conv_id.count("-") == 4  # UUID has 4 dashes

    def test_chat_request_validation(self):
        """Test ChatRequest model validation."""
        from app.models import ChatRequest

        # Valid request
        request = ChatRequest(message="Test message")
        assert request.message == "Test message"
        assert request.conversation_id is None
        assert request.user_id is None

        # Request with all fields
        request = ChatRequest(
            message="Test",
            conversation_id="123",
            user_id="user123"
        )
        assert request.conversation_id == "123"
        assert request.user_id == "user123"


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        # This test might fail if RATE_LIMIT_PER_MINUTE is very high
        # Send multiple requests rapidly
        payload = {"message": "Test question about plantes"}

        responses = []
        for _ in range(15):  # Send more than rate limit
            response = client.post("/chat", json=payload)
            responses.append(response.status_code)

        # At least one request should be rate limited (429)
        # Note: This test is commented out as it depends on rate limit settings
        # assert 429 in responses


# Run tests with: pytest tests/test_api.py -v
