"""
Agent Configuration Module

This module handles all configuration settings for the agent using Pydantic
for type validation and environment variable management.

Components:
    AgentConfig: Main configuration class with all agent settings

Environment Variables:
    DATABASE_URL: Database connection string (optional, default: in-memory SQLite)
    MODEL_ID: LLM model identifier (default: gemma3)
    AGENT_NAME: Name of the agent (default: adk_agent)
    LOG_LEVEL: Logging level (default: INFO)

    # TODO: Add your agent-specific tool configuration variables here
    # Example:
    # EXTERNAL_API_URL: URL for external API integration
    # API_TIMEOUT: Timeout for API calls in seconds
    # CACHE_TTL: Cache time-to-live in seconds

Usage:
    from config import AgentConfig
    settings = AgentConfig()
    print(settings.model_id)
"""

from pydantic import Field, SecretStr
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

from adk_agent.core.base_config import BaseAgentConfig
from adk_agent.agent.prompts import get_agent_description, get_agent_instruction

# Load environment variables from .env file - helpful for local development
load_dotenv()


class AgentConfig(BaseAgentConfig):
    """
    Main Agent configuration settings using Pydantic BaseSettings.

    This class automatically loads configuration from environment variables
    and provides type validation, default values, and documentation.

    Inherits common settings from BaseAgentConfig:
        - model_id: LLM model identifier
        - agent_name: Name of the agent instance

    Attributes:
        database_url: Database connection URL (optional)

    Properties:
        agent_description: Returns the agent's description from prompts
        agent_instruction: Returns the agent's instruction with context

    Configuration Sections:
        - Common Settings: Inherited from BaseAgentConfig
        - Main Agent Settings: Specific to main agent
        - Tool Settings: Configuration for agent tools and integrations
    """

    # --> Main Agent Specific Settings
    # Database configuration (optional for stateless agents)
    database_url: SecretStr = Field(
        default=SecretStr("sqlite:///:memory:"),
        description="Database connection URL for session persistence",
    )

    # Override defaults from BaseAgentConfig for main agent
    model_id: str = Field(
        default="gemini-2.5-flash-lite",
        description="LLM model identifier (e.g., gemini-2.5-flash-lite, gpt-4, claude-3)",
    )

    agent_name: str = Field(
        default="adk_agent", description="Name of the agent instance"
    )
    # <-- End of Main Agent Specific Settings

    # --> Tool Settings
    # TODO: Add your tool-specific configuration here
    # This section should contain configuration for external services,
    # APIs, databases, or other tools your agent uses.
    #
    # Examples:
    # external_api_url: HttpUrl | None = Field(
    #     default=None,
    #     description="URL for external API integration"
    # )
    #
    # api_timeout: int = Field(
    #     default=30,
    #     description="Timeout for API calls in seconds"
    # )
    #
    # cache_ttl: int = Field(
    #     default=3600,
    #     description="Cache time-to-live in seconds"
    # )
    # <-- End of Tool Settings

    # Agent prompt and description
    @property
    def agent_description(self) -> str:
        """
        Returns the agent description prompt.

        The description is loaded from the prompts module and can be
        overridden via the AGENT_DESCRIPTION environment variable.

        Returns:
            str: Brief description of the agent's purpose and capabilities
        """
        return get_agent_description()

    @staticmethod
    def agent_instruction(context: ReadonlyContext) -> str:
        """
        Returns the agent instruction prompt with runtime context.

        The instruction is loaded from the prompts module and includes
        dynamic context such as user information and current date/time.
        Can be overridden via the AGENT_INSTRUCTION environment variable.

        Args:
            context: Runtime context containing state and user information

        Returns:
            str: Complete system instruction for the agent
        """
        return get_agent_instruction(context)


# Global configuration instance
# Import this throughout the codebase: from config import settings
settings = AgentConfig()
