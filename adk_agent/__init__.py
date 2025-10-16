"""
Application Initialization Module

This module initializes the application with configuration logging and
sensitive field masking. It exports the root_agent for use by the ADK framework.
"""

from .config import AgentConfig, SENSITIVE_FIELDS
from .agent.agent import root_agent

__all__ = ["root_agent"]


def mask_sensitive_part_from_url(url: str) -> str:
    """Mask sensitive parts of a URL for safe logging."""
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


print("=== Initializing agents with following settings ===")
for key, value in AgentConfig().model_dump().items():
    if key in SENSITIVE_FIELDS:
        if key.endswith("_url") and value is not None:
            # Convert to string if it's a URL object
            url_str = str(value) if hasattr(value, "__str__") else value
            if isinstance(url_str, str) and url_str:
                masked_value = mask_sensitive_part_from_url(url_str)
                print(f" - {key}: {masked_value} (sensitive)")
            else:
                print(f" - {key}: {'*' * 8} (sensitive)")
        else:
            print(f" - {key}: {'*' * 8} (sensitive)")
    else:
        print(f" - {key}: {value}")
print("===================================================")
