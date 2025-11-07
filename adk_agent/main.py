"""
Server for managing and interacting with AI agents.

This server provides:
- Google ADK agent execution endpoints
- A2A (Agent-to-Agent) protocol support (optional)
- API key authentication (optional)
- Langfuse observability (optional)
- Web interface (optional)

Configuration is managed through environment variables - see .env.template for details.
"""

import base64
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.sessions import InMemorySessionService, DatabaseSessionService

from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from ag_ui.core import RunAgentInput

from .agent import root_agent

# Load environment variables from .env file
load_dotenv()

print("Environment variables loaded:" + "*" * 40)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def check_env_var_bool(var_name: str, default: Optional[str] = None) -> bool:
    """
    Check if an environment variable is set to a truthy value.

    Args:
        var_name: Name of the environment variable
        default: Default value if not set (defaults to "false")

    Returns:
        True if the variable is set to "true", "1", or "yes" (case-insensitive)
    """
    _default = default if default is not None else "false"
    return os.environ.get(var_name, _default).lower() in ("true", "1", "yes")


# Utility function for extracting userID for AG-UI from request
def extract_user_id(input_request: RunAgentInput) -> str:
    """
    Extract user ID from the RunAgentInput request.
    This expects the UI which uses AG-UI protocol sends userId in forwarded_props.
    """
    # Extract from forwarded_props
    user_id = getattr(input_request.forwarded_props, "userId", None)
    if user_id:
        return user_id
    return f"thread_user_{input_request.thread_id}"


# =============================================================================
# CONFIGURATION
# =============================================================================

# Server Configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

# A2A Configuration
ENABLE_A2A = check_env_var_bool("ENABLE_A2A", "true")

# Enabling copilotkit integration
ENABLE_AG_UI = check_env_var_bool("ENABLE_AG_UI", "true")

# Auto-convert legacy postgresql:// URL to modern postgresql+psycopg://
# This ensures compatibility with psycopg (v3) installed in the container
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    print("ℹ️  Auto-converted DATABASE_URL to use psycopg driver")

# Service Configuration
ARTIFACT_SERVICE_URI = os.environ.get("ARTIFACT_SERVICE_URI")
MEMORY_SERVICE_URI = os.environ.get("MEMORY_SERVICE_URI")

# Web Configuration
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8000", "*"]
SERVE_WEB_INTERFACE = check_env_var_bool("SERVE_WEB_INTERFACE")
TRACE_TO_CLOUD = check_env_var_bool("TRACE_TO_CLOUD")

# API Authentication Configuration (Optional)
ADK_API_KEYS = os.environ.get("ADK_API_KEYS", "")
API_KEYS = [key.strip() for key in ADK_API_KEYS.split(",") if key.strip()]

# Langfuse Configuration (Optional - for observability)
LANGFUSE_ENABLED = check_env_var_bool("LANGFUSE_ENABLED")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "http://localhost:4317")


# =============================================================================
# LANGFUSE SETUP (OBSERVABILITY)
# =============================================================================


def setup_langfuse() -> Optional[object]:
    """
    Initialize Langfuse observability if enabled and configured.

    Langfuse provides tracing and monitoring for AI agent interactions.
    Set LANGFUSE_ENABLED=true and provide credentials to enable.

    Returns:
        Langfuse client if successful, None otherwise
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
        from langfuse import get_client  # pylint: disable=import-outside-toplevel
        from openinference.instrumentation.google_adk import (  # pylint: disable=import-outside-toplevel
            GoogleADKInstrumentor,
        )

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
# STARTUP INFO
# =============================================================================

print("\n" + "=" * 60)
print("ADK Agent Server - Configuration")
print("=" * 60)
print(f"Base Directory:     {BASE_DIR}")
print(f"Host:               {HOST}:{PORT}")
print(f"Web Interface:      {'Enabled' if SERVE_WEB_INTERFACE else 'Disabled'}")
print(f"A2A Protocol:       {'Enabled' if ENABLE_A2A else 'Disabled'}")
print(f"API Authentication: {'Enabled' if API_KEYS else 'Disabled'}")
print(f"Langfuse:           {'Active' if langfuse else 'Disabled'}")
print(f"Trace to Cloud:     {'Enabled' if TRACE_TO_CLOUD else 'Disabled'}")
print(f"API Keys available: {len(API_KEYS)} key(s) configured")
print("=" * 60 + "\n")


# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================

# Create main FastAPI app
app = FastAPI()

# Create the ADK FastAPI app with A2A protocol support
# - agents_dir: Directory containing agent folders with agent.json files
# - a2a=True: Enables automatic A2A endpoint creation for each agent
#   Creates endpoints at /a2a/{agent_name}/ for each subdirectory with agent.json
adk_app: FastAPI = get_fast_api_app(
    agents_dir=BASE_DIR,
    session_service_uri=DATABASE_URL,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    memory_service_uri=MEMORY_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    a2a=ENABLE_A2A,  # Enable A2A protocol support
)


# Create app for copilotkit integration
adk_copilotkit_agent = ADKAgent(
    adk_agent=root_agent,
    app_name=root_agent.name,
    user_id_extractor=extract_user_id,
    session_timeout_seconds=3600,
    session_service=DatabaseSessionService(DATABASE_URL)
    if DATABASE_URL
    else InMemorySessionService(),
)


# =============================================================================
# CORS MIDDLEWARE
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# CUSTOM ENDPOINTS
# =============================================================================


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns server status without requiring authentication.
    Useful for load balancers and monitoring systems.
    """
    return JSONResponse(
        content={"status": "ok", "message": "Server is running"}, status_code=200
    )


# =============================================================================
# MOUNT ADK APP
# =============================================================================

# Mount the ADK app at root path
# This includes all ADK endpoints and A2A protocol endpoints
# A2A endpoints are automatically created at /a2a/{agent_name}/ for each agent
app.mount("/", adk_app)

# =============================================================================
#  conditional CopilotKit integration
# =============================================================================
if ENABLE_AG_UI:
    print("✅ CopilotKit integration enabled at /copilotkit")
    add_adk_fastapi_endpoint(app, adk_copilotkit_agent, path="/copilotkit")


# =============================================================================
# API KEY AUTHENTICATION MIDDLEWARE
# =============================================================================


@app.middleware("http")
async def enforce_api_key(request, call_next):
    """
    Middleware to enforce API key authentication for protected endpoints.

    Public endpoints (docs, redoc, openapi.json, health) don't require authentication.
    All other endpoints require a valid API key in the X-API-KEY header.

    Enable by setting ADK_API_KEYS environment variable with comma-separated keys.
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
# OPENAPI SCHEMA CUSTOMIZATION
# =============================================================================


def custom_openapi():
    """
    Customize OpenAPI schema to include all endpoints and API key authentication.

    This merges:
    - ADK app endpoints (agent execution, sessions, artifacts, etc.)
    - Main app endpoints (health check)
    - Security schemes (API key authentication if enabled)
    """
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi  # pylint: disable=import-outside-toplevel
    from starlette.routing import Mount  # pylint: disable=import-outside-toplevel

    # Get OpenAPI schema from ADK app (includes all ADK and A2A endpoints)
    adk_openapi = get_openapi(
        title=adk_app.title,
        version=adk_app.version,
        description=adk_app.description,
        routes=adk_app.routes,
    )

    # Get direct routes from main app (like /health) - exclude mounts
    direct_routes = [r for r in app.routes if not isinstance(r, Mount)]
    main_openapi = get_openapi(
        title="Main App",
        version="1.0.0",
        description="Main app routes",
        routes=direct_routes,
    )

    # Start with ADK schema
    openapi_schema = adk_openapi
    openapi_schema["info"]["title"] = f"{adk_app.title} with A2A Protocol"
    openapi_schema["info"]["description"] = (
        f"{adk_app.description}\n\n"
        f"### A2A Protocol Support {'enabled' if ENABLE_A2A else 'disabled'}\n\n"
        f"### CopilotKit Integration {'enabled at /copilotkit' if ENABLE_AG_UI else 'disabled'}\n\n"
        f"#### A2A Agent card will be available for each agent at /a2a/<agent_id>/.well-known/agent-card.json\n\n"
        if ENABLE_A2A
        else ""
    )

    # Merge main app routes (like /health)
    if "paths" in main_openapi:
        for path, path_item in main_openapi["paths"].items():
            openapi_schema["paths"][path] = path_item

    # Add API key security scheme if configured
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
        public_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        for path, path_item in openapi_schema["paths"].items():
            if path not in public_paths:
                for method in path_item.values():
                    if isinstance(method, dict) and "security" not in method:
                        method["security"] = [{"APIKeyHeader": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema
app.openapi = custom_openapi


# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print(f"🚀 Starting server on {HOST}:{PORT}\n")
    uvicorn.run(app, host=HOST, port=PORT)
