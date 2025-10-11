"""
Server for managing and interacting with AI agents.

This production-grade FastAPI server provides:
- Agent execution via Google ADK
- Optional Langfuse observability integration
- API key authentication
- Health checks and monitoring
- Web interface for agent interaction

Configuration is managed through environment variables - see .env.template for details.
"""

import base64
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from langfuse import Langfuse, get_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# =============================================================================
# CONFIGURATION
# =============================================================================

# Langfuse Configuration (Optional - for observability)
LANGFUSE_ENABLED = os.environ.get("LANGFUSE_ENABLED", "true").lower() in (
    "true",
    "1",
    "yes",
)
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "http://localhost:4317")

# API Authentication Configuration (Optional)
ADK_API_KEYS = os.environ.get("ADK_API_KEYS", "")
API_KEYS = [key.strip() for key in ADK_API_KEYS.split(",") if key.strip()]

# Server Configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

# Service Configuration
ARTIFACT_SERVICE_URI = os.environ.get("ARTIFACT_SERVICE_URI")
MEMORY_SERVICE_URI = os.environ.get("MEMORY_SERVICE_URI")

# Web Configuration
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
SERVE_WEB_INTERFACE = os.environ.get("SERVE_WEB_INTERFACE", "true").lower() in (
    "true",
    "1",
    "yes",
)
TRACE_TO_CLOUD = os.environ.get("TRACE_TO_CLOUD", "false").lower() in (
    "true",
    "1",
    "yes",
)


# =============================================================================
# LANGFUSE SETUP (OBSERVABILITY)
# =============================================================================


def setup_langfuse() -> Optional[Langfuse]:
    """
    Initialize Langfuse observability if enabled and configured.

    This function sets up OTEL tracing to Langfuse for complete observability
    of agent interactions, tool usage, and performance metrics.

    Returns:
        Langfuse client if successful, None otherwise.

    Environment Variables:
        LANGFUSE_ENABLED: Enable/disable Langfuse (default: true)
        LANGFUSE_PUBLIC_KEY: Your Langfuse public key (required if enabled)
        LANGFUSE_SECRET_KEY: Your Langfuse secret key (required if enabled)
        LANGFUSE_HOST: Langfuse host URL (default: http://localhost:4317)
    """
    if not LANGFUSE_ENABLED:
        print("ℹ️  Langfuse observability is disabled")
        return None

    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        print("⚠️  Langfuse is enabled but credentials are missing")
        print(
            "   Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables"
        )
        print("   Or set LANGFUSE_ENABLED=false to disable")
        return None

    try:
        # Setup OTEL environment for Langfuse
        langfuse_auth = base64.b64encode(
            f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()
        ).decode()

        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{LANGFUSE_HOST}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
            f"Authorization=Basic {langfuse_auth}"
        )

        # Initialize Langfuse client
        langfuse_client = get_client()

        # Verify authentication
        if not langfuse_client.auth_check():
            print("❌ Langfuse authentication failed")
            print("   Please check your credentials and host configuration")
            return None

        # Instrument Google ADK
        GoogleADKInstrumentor().instrument()
        print("✅ Langfuse observability initialized successfully")
        return langfuse_client

    except Exception as e:
        print(f"❌ Failed to initialize Langfuse: {str(e)}")
        print("   Application will continue without observability")
        return None


# Initialize Langfuse (optional)
langfuse = setup_langfuse()


# =============================================================================
# STARTUP VALIDATION & INFO
# =============================================================================

print("\n" + "=" * 60)
print("ADK Agent Server - Configuration")
print("=" * 60)
print(f"Base Directory:     {BASE_DIR}")
print(f"Host:               {HOST}:{PORT}")
print(f"Web Interface:      {'Enabled' if SERVE_WEB_INTERFACE else 'Disabled'}")
print(f"API Authentication: {'Enabled' if API_KEYS else 'Disabled'}")
print(f"Langfuse:           {'Active' if langfuse else 'Disabled'}")
print(f"Trace to Cloud:     {'Enabled' if TRACE_TO_CLOUD else 'Disabled'}")
print(f"API Keys available: {len(API_KEYS)} key(s) configured")
print("=" * 60 + "\n")


# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================

# Create the ADK FastAPI app
app: FastAPI = get_fast_api_app(
    agents_dir=BASE_DIR,
    session_service_uri=DATABASE_URL,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    memory_service_uri=MEMORY_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint - no authentication required.

    Returns basic server status and configuration information.
    Useful for monitoring, load balancers, and orchestration systems.
    """
    return JSONResponse(
        content={"status": "ok", "message": "Server is running"}, status_code=200
    )


# =============================================================================
# API KEY AUTHENTICATION MIDDLEWARE
# =============================================================================


@app.middleware("http")
async def enforce_api_key(request, call_next):
    """
    Middleware to enforce API key authentication for protected endpoints.

    Public endpoints (docs, health checks) are exempt from authentication.
    All other endpoints require a valid API key in the X-API-KEY header.

    Environment Variables:
        ADK_API_KEYS: Comma-separated list of valid API keys

    Usage:
        curl -H "X-API-KEY: your-api-key" http://localhost:8080/endpoint
    """
    # List of paths that don't require authentication
    public_paths = ["/docs", "/redoc", "/openapi.json", "/health"]

    # Check if authentication is required
    if API_KEYS and request.url.path not in public_paths:
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing API Key. Provide 'X-API-KEY' header."},
            )

        if api_key not in API_KEYS:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key."},
            )

    response = await call_next(request)
    return response


# =============================================================================
# OPENAPI SCHEMA CUSTOMIZATION (for API key auth)
# =============================================================================


def custom_openapi():
    """
    Customize OpenAPI schema to add API key authentication.

    This function modifies the OpenAPI schema to include security definitions
    and apply them to all endpoints except public ones.
    """
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme definition if API keys are configured
    if API_KEYS:
        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-KEY",
                "description": "API Key authentication using X-API-KEY header",
            }
        }

        # Apply security to all endpoints except public ones
        for path, path_item in openapi_schema["paths"].items():
            # Skip security for docs and health endpoints
            if path not in ["/docs", "/redoc", "/openapi.json", "/health"]:
                for method in path_item.values():
                    if isinstance(method, dict) and "security" not in method:
                        method["security"] = [{"APIKeyHeader": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override the OpenAPI schema if API keys are configured
if API_KEYS:
    app.openapi = custom_openapi


# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    print(f"🚀 Starting server on {HOST}:{PORT}\n")
    uvicorn.run(app, host=HOST, port=PORT)
