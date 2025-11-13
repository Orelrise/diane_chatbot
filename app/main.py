"""
Diane Herborist API - Main application module.
FastAPI backend for Diane chatbot specializing in medicinal plants.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.models import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    HealthCheckResponse,
    generate_conversation_id,
    get_current_timestamp
)
from app.services.validator import is_valid_herbalism_topic, get_off_topic_response
from app.services.groq_service import groq_service, GroqServiceError
from app.utils.logger import logger


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST pour Diane, conseillère herboriste virtuelle",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate settings on startup
try:
    settings.validate()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"Using Groq model: {settings.MODEL}")
    logger.info(f"API Key configured: {settings.mask_api_key()}")
except Exception as e:
    logger.error(f"Configuration error: {str(e)}")
    raise


@app.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint - Basic service information.

    Returns:
        Service status and version information
    """
    logger.info("Root endpoint accessed")
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Detailed health check endpoint - Verifies Groq API connection.

    Returns:
        Detailed health status including Groq API connectivity
    """
    logger.info("Health check endpoint accessed")

    # Check Groq API connection
    groq_connection = await groq_service.check_connection()

    return HealthCheckResponse(
        api_status="ok" if groq_connection else "degraded",
        groq_connection=groq_connection,
        timestamp=get_current_timestamp()
    )


@app.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    Main chat endpoint - Process user questions about medicinal plants.

    Args:
        request: FastAPI request object (for rate limiting)
        chat_request: User's chat request

    Returns:
        HTML-formatted response from Diane

    Raises:
        HTTPException: On validation or service errors
    """
    user_message = chat_request.message.strip()
    conversation_id = chat_request.conversation_id or generate_conversation_id()
    user_id = chat_request.user_id or "anonymous"

    logger.info(f"Chat request from user: {user_id}, conversation: {conversation_id}")
    logger.info(f"Message: {user_message[:100]}...")

    try:
        # Validate topic before calling Groq API (save tokens)
        is_valid, validation_reason = is_valid_herbalism_topic(user_message)

        if not is_valid:
            logger.info(f"Off-topic question detected: {validation_reason}")
            return ChatResponse(
                response=get_off_topic_response(),
                conversation_id=conversation_id,
                timestamp=get_current_timestamp(),
                is_valid_topic=False,
                tokens_used=0
            )

        logger.info(f"Topic validation passed: {validation_reason}")

        # Get response from Groq API
        response_text, tokens_used = await groq_service.get_response(user_message)

        logger.info(f"Response generated successfully - Tokens: {tokens_used}")

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=get_current_timestamp(),
            is_valid_topic=True,
            tokens_used=tokens_used
        )

    except GroqServiceError as e:
        logger.error(f"Groq service error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service temporairement indisponible",
                "detail": "Erreur lors de la connexion à l'API Groq"
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erreur serveur inattendue",
                "detail": str(e)
            }
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler for HTTP exceptions.

    Args:
        request: FastAPI request object
        exc: HTTP exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request object
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur serveur inattendue",
            "detail": "Une erreur interne s'est produite"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info(f"{settings.APP_NAME} started successfully")
    logger.info(f"CORS enabled for origins: {settings.ALLOWED_ORIGINS}")
    logger.info(f"Rate limit: {settings.RATE_LIMIT_PER_MINUTE} requests/minute")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info(f"{settings.APP_NAME} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
