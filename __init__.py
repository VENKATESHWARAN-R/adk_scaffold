"""
ADK Agent Scaffold Template

This is a template for creating production-ready ADK agents.
All application code is in the app/ directory.

For ADK CLI Commands:
    Run from this directory:
    - adk web .
    - adk run .
    - adk api_server --host 0.0.0.0 --port 8080 --a2a

For Production Server:
    python -m app.main
    or
    uvicorn app.main:app --host 0.0.0.0 --port 8080
"""

from .adk_agent import root_agent  # pylint: disable=unused-import

__all__ = ["root_agent"]
