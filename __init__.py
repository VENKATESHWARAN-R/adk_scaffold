"""
ADK Agent Package

This package provides a production-ready template for creating ADK-based agents.
It includes all the necessary components for a functional, observable, and
maintainable agent system.

Components:
    agent: Main agent definition and configuration
    config: Centralized configuration management with Pydantic
    prompts: Agent instructions and descriptions
    logging_config: Logging system setup
    main: Production FastAPI server with auth and observability

Features:
    - Pydantic-based configuration management
    - Sensitive field masking in logs
    - Langfuse observability integration
    - API key authentication
    - Health check endpoints
    - Modular tool organization

Usage:
    This package is designed to be used as a template. When scaffolding a new agent:
    1. Copy this directory structure
    2. Replace 'adk_agent' references with your agent name
    3. Customize prompts and configuration for your use case
    4. Add appropriate tools in agent/tools/toolset.py
    5. Update .env.template with your configuration
    6. Run with: python main.py or uvicorn main:app

Entry Point:
    The agent.agent module contains the root_agent that will be discovered and
    executed by the ADK framework.

Configuration:
    All configuration is managed through environment variables and the AgentConfig
    class. Sensitive fields are automatically masked in initialization logs for
    security.
"""

from config import AgentConfig, SENSITIVE_FIELDS
from agent.agent import root_agent

__all__ = ["root_agent"]


def mask_sensitive_part_from_url(url: str) -> str:
    """
    Mask sensitive parts of a URL for safe logging.

    This function identifies credentials in URLs (username:password@host format)
    and masks the password portion while keeping the rest visible for debugging.

    Args:
        url: The URL string to mask

    Returns:
        Masked URL with password replaced by asterisks

    Examples:
        >>> mask_sensitive_part_from_url("redis://user:pass123@localhost:6379")
        'redis://user:****@localhost:6379'

        >>> mask_sensitive_part_from_url("postgresql://admin:secret@db.example.com/mydb")
        'postgresql://admin:****@db.example.com/mydb'

        >>> mask_sensitive_part_from_url("http://api.example.com/endpoint")
        'http://api.example.com/endpoint'
    """
    if not url or not isinstance(url, str):
        return "****"

    if "://" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            # URL has credentials, mask the password part
            userinfo, hostinfo = rest.split("@", 1)
            if ":" in userinfo:
                username, _ = userinfo.split(":", 1)
                masked_userinfo = f"{username}:****"
            else:
                masked_userinfo = f"{userinfo}:****"
            return f"{scheme}://{masked_userinfo}@{hostinfo}"
        else:
            # No credentials in URL, safe to show
            return url
    else:
        # Not a proper URL format, mask it completely
        return "****"


# Initialize and log configuration (with sensitive field masking)
print("\n" + "=" * 60)
print("Initializing ADK Agent with Configuration")
print("=" * 60)

config = AgentConfig()

for key, value in config.model_dump().items():
    if key in SENSITIVE_FIELDS:
        if key.endswith("_url") and value is not None:
            # Convert to string if it's a URL object
            url_str = str(value) if hasattr(value, "__str__") else value
            if isinstance(url_str, str) and url_str:
                masked_value = mask_sensitive_part_from_url(url_str)
                print(f"  {key}: {masked_value} (sensitive)")
            else:
                print(f"  {key}: {'*' * 8} (sensitive)")
        else:
            print(f"  {key}: {'*' * 8} (sensitive)")
    else:
        print(f"  {key}: {value}")

print("=" * 60 + "\n")
