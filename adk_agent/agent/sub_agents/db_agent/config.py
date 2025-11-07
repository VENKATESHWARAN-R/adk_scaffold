"""
Database Agent Configuration Module

This module handles configuration settings for the database sub-agent using Pydantic
for type validation and environment variable management.

Components:
    DbAgentConfig: Configuration class for database agent settings

Environment Variables:
    TOOLBOX_URL: URL for GenAI Toolbox MCP server (default: http://localhost:9000)
    TOOLBOX_TOOLSET: Name of the toolset to load from Toolbox (default: my-toolset)
    DB_AGENT_MODEL_ID: LLM model identifier for db_agent (optional, inherits from base if not set)
    DB_AGENT_NAME: Name of the database agent instance (default: db_agent)

Usage:
    from adk_agent.agent.sub_agents.db_agent.config import db_settings
    print(db_settings.toolbox_url)
"""

from pydantic import Field, AnyHttpUrl
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

from adk_agent.core.base_config import BaseAgentConfig
from .prompts import get_agent_description, get_agent_instruction

# Load environment variables from .env file
load_dotenv()


class DbAgentConfig(BaseAgentConfig):
    """
    Database Agent configuration settings using Pydantic BaseSettings.

    This class automatically loads configuration from environment variables
    and provides type validation, default values, and documentation specific
    to the database sub-agent.

    Inherits common settings from BaseAgentConfig:
        - model_id: LLM model identifier (can be overridden)
        - agent_name: Name of the agent instance (can be overridden)

    Attributes:
        toolbox_url: URL for GenAI Toolbox MCP server
        toolbox_toolset: Name of the toolset to load from Toolbox

    Properties:
        agent_description: Returns the agent's description from prompts
        agent_instruction: Returns the agent's instruction with context
    """

    # --> MCP Toolbox Settings
    toolbox_url: str = Field(
        default="http://localhost:5000",
        description="URL for GenAI Toolbox MCP server",
    )

    toolbox_toolset: str = Field(
        default="my-toolset", description="Name of the toolset to load from Toolbox"
    )
    # <-- End of MCP Toolbox Settings

    # --> Override Base Settings for DB Agent
    # Override model_id with db_agent specific default (can still be overridden via env)
    model_id: str = Field(
        default="gemini-2.5-flash-lite", description="LLM model identifier for db_agent"
    )

    # Override agent_name with db_agent specific default
    db_agent_name: str = Field(
        default="db_agent", description="Name of the database agent instance"
    )
    # <-- End of Override Base Settings

    # Agent prompt and description
    @property
    def agent_description(self) -> str:
        """
        Returns the database agent description prompt.

        The description is loaded from the prompts module and can be
        overridden via the DB_AGENT_DESCRIPTION environment variable.

        Returns:
            str: Brief description of the database agent's purpose and capabilities
        """
        return get_agent_description()

    @staticmethod
    def agent_instruction(context: ReadonlyContext) -> str:
        """
        Returns the database agent instruction prompt with runtime context.

        The instruction is loaded from the prompts module and includes
        dynamic context such as user information and current date/time.
        Can be overridden via the DB_AGENT_INSTRUCTION environment variable.

        Args:
            context: Runtime context containing state and user information

        Returns:
            str: Complete system instruction for the database agent
        """
        return get_agent_instruction(context)


# Global configuration instance for database agent
# Import this in db_agent module: from .config import db_settings
db_settings = DbAgentConfig()
