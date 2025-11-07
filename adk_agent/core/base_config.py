"""
Base Agent Configuration Module

This module provides a shared base configuration class that can be inherited
by both the main agent and sub-agents, promoting code reuse and consistency.

Components:
    BaseAgentConfig: Base configuration class with common agent settings

Usage:
    from adk_agent.core.base_config import BaseAgentConfig

    class MyAgentConfig(BaseAgentConfig):
        # Add agent-specific settings here
        custom_setting: str = Field(default="value")
"""

import os
from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseAgentConfig(BaseSettings):
    """
    Base configuration class for all agents (main and sub-agents).

    Provides common settings that are shared across all agents in the system.
    Inherit from this class to create agent-specific configurations.

    Common Settings:
        - model_id: LLM model identifier
        - agent_name: Name of the agent instance

    Example:
        class MyCustomAgent(BaseAgentConfig):
            custom_api_key: str = Field(default="")

        settings = MyCustomAgent()
    """

    # Class variable to track which configs have been logged
    _logged_configs: ClassVar[set] = set()

    # --> Common Agent Settings
    # These settings are typically shared across all agents

    model_id: str = Field(
        default="gemini-2.5-flash-lite",
        description="LLM model identifier (e.g., gemini-2.5-flash-lite, gpt-4, claude-3)",
    )

    agent_name: str = Field(default="agent", description="Name of the agent instance")
    # <-- End of Common Agent Settings

    def log_config(self) -> None:
        """
        Logs the configuration settings in a formatted manner.

        Automatically masks SecretStr fields using Pydantic's built-in masking.
        Only logs once per config class to prevent duplicate output.

        Usage:
            settings = AgentConfig()
            settings.log_config()  # Prints formatted config
            settings.log_config()  # Does nothing (already logged)
        """
        # Use class name as unique identifier
        config_id = f"{self.__class__.__module__}.{self.__class__.__name__}"

        # Skip if already logged
        if config_id in BaseAgentConfig._logged_configs:
            return

        # Mark as logged
        BaseAgentConfig._logged_configs.add(config_id)

        # Print header
        config_name = self.__class__.__name__
        print(f"\n{'=' * 60}")
        print(f"Initializing {config_name}")
        print(f"{'=' * 60}")

        # Get model dump (Pydantic automatically masks SecretStr)
        config_dict = self.model_dump()

        # Print each configuration item
        for key, value in config_dict.items():
            # Format the value
            if value is None:
                display_value = "None"
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long strings
                display_value = f"{value[:97]}..."
            else:
                display_value = str(value)

            print(f"  {key}: {display_value}")

        print(f"{'=' * 60}\n")

    def get_model(self):
        """
        Returns the appropriate model instance based on configuration.

        Automatically determines whether to use LiteLLM proxy based on:
        - USE_LITELLM_PROXY environment variable set to "True"
        - model_id starting with "openrouter/"

        Returns:
            Either a LiteLlm instance or the model_id string directly

        Example:
            >>> agent = LlmAgent(
            ...     name=settings.agent_name,
            ...     model=settings.get_model(),
            ...     # ... other config
            ... )
        """
        from google.adk.models.lite_llm import LiteLlm

        # Check if LiteLLM proxy should be used
        use_litellm = os.getenv("USE_LITELLM_PROXY") == "True"
        is_openrouter = str(self.model_id).startswith("openrouter/")

        if use_litellm or is_openrouter:
            return LiteLlm(self.model_id)
        else:
            return self.model_id

    # Pydantic model configuration
    # Child classes can override this if needed
    model_config = SettingsConfigDict(
        # Loads from .env file in the current directory
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignore extra environment variables not defined in the model
        extra="ignore",
        # Ignore empty environment variables
        env_ignore_empty=True,
        # Allow arbitrary types (needed for AnyUrl, HttpUrl, etc.)
        arbitrary_types_allowed=True,
        # Don't validate default values
        validate_default=False,
        # Case-sensitive environment variables
        case_sensitive=False,
    )
