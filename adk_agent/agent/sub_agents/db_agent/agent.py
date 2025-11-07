"""
Database Agent Module - Specialized Sub-Agent for Database Operations

This module defines the database sub-agent instance that handles database interactions
within the ADK framework using the MCP (Model Context Protocol) toolbox.

Components:
    db_agent: Database specialist DbAgent instance configured with MCP toolbox
    DbAgent: Custom agent class that manages MCP Toolbox lifecycle

Configuration:
    - Uses db_settings from config module for MCP toolbox configuration
    - Can inherit model from main agent or use its own model configuration
    - Integrates with GenAI Toolbox MCP server for database tools

Usage:
    This agent is designed to be used as a sub-agent of the root agent:

    from adk_agent.agent.sub_agents.db_agent.agent import db_agent

    root_agent = LlmAgent(
        # ... other config ...
        sub_agents=[db_agent]
    )

Environment Variables:
    TOOLBOX_URL: URL for GenAI Toolbox MCP server
    TOOLBOX_TOOLSET: Name of the toolset to load from Toolbox
    DB_AGENT_MODEL_ID: Optional model override for db_agent
    USE_LITELLM_PROXY: Set to "True" to use LiteLLM proxy

Example:
    The db_agent can be invoked by the root agent when database operations
    are needed. It will use the MCP toolbox to execute queries and retrieve data.

Implementation Pattern:
    This uses a composition pattern where DbAgent (custom BaseAgent) wraps an
    internal LlmAgent and manages the MCP Toolbox client lifecycle using async
    context managers. This ensures proper connection management and cleanup.
"""

import logging
from typing import AsyncGenerator, Union

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.events.event import Event
from google.adk.tools import FunctionTool
from toolbox_core import ToolboxClient
from typing_extensions import override

from .config import db_settings

# Setup logging
logger = logging.getLogger(__name__)


class DbAgent(BaseAgent):
    """
    Custom Database Agent with MCP Toolbox lifecycle management.

    This agent manages the MCP Toolbox client connection lifecycle and
    dynamically loads database tools for each execution context.

    Architecture:
        Uses composition pattern - wraps an internal LlmAgent and manages
        the MCP Toolbox client lifecycle using async context managers.

    Attributes:
        toolbox_url: URL endpoint for the MCP Toolbox server
        toolbox_toolset: Name of the toolset to load from Toolbox
        model_id: LLM model identifier for the agent
        agent_instruction: Callable that generates instruction with context
        agent_description: Description of the agent's capabilities

    Lifecycle:
        1. _run_async_impl is called when agent is invoked
        2. ToolboxClient connection is established
        3. Tools are loaded from the specified toolset
        4. Inner LlmAgent is created with loaded tools
        5. Execution is delegated to inner agent
        6. Connection is automatically cleaned up via context manager
    """

    # Pydantic field declarations for validation
    toolbox_url: str
    toolbox_toolset: str
    model_id: Union[str, LiteLlm]
    agent_instruction: callable
    agent_description: str

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        toolbox_url: str,
        toolbox_toolset: str,
        model_id: Union[str, LiteLlm],
        agent_instruction: callable,
        agent_description: str,
        **kwargs,
    ):
        """
        Initialize the DbAgent with MCP Toolbox configuration.

        Args:
            name: Name identifier for the agent
            toolbox_url: URL endpoint for MCP Toolbox server
            toolbox_toolset: Toolset name to load from Toolbox
            model_id: LLM model identifier
            agent_instruction: Callable that takes InvocationContext and returns instruction
            agent_description: Brief description of agent capabilities
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            name=name,
            toolbox_url=toolbox_url,
            toolbox_toolset=toolbox_toolset,
            model_id=model_id,
            agent_instruction=agent_instruction,
            agent_description=agent_description,
            sub_agents=[],  # This is a leaf agent - no sub-agents
            **kwargs,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Custom execution logic with MCP Toolbox context management.

        This method implements the composition pattern by:
        1. Establishing MCP Toolbox client connection
        2. Loading tools dynamically from the configured toolset
        3. Creating an inner LlmAgent with the loaded tools
        4. Delegating all execution to the inner agent
        5. Yielding all events from the inner agent

        The async context manager ensures proper connection lifecycle:
        - Connection is established when entering the context
        - Tools are loaded while connection is active
        - Connection is automatically closed when exiting the context

        Args:
            ctx: InvocationContext containing session state and user information

        Yields:
            Event: All events generated by the inner LlmAgent during execution

        Raises:
            Exception: Any exceptions from toolbox connection or tool loading
        """
        logger.info(
            "[%s] Initializing MCP Toolbox connection to %s",
            self.name,
            self.toolbox_url,
        )

        try:
            # Initialize toolbox client within async context manager
            # This ensures proper connection lifecycle and cleanup
            async with ToolboxClient(self.toolbox_url) as toolbox_client:
                logger.info("[%s] Loading toolset: %s", self.name, self.toolbox_toolset)

                # Load tools from the configured toolset
                toolbox_tools = await toolbox_client.load_toolset(self.toolbox_toolset)
                logger.info(
                    "[%s] Loaded %d tools from toolset", self.name, len(toolbox_tools)
                )

                # Create inner LLM agent with dynamically loaded tools
                # This agent handles all LLM interactions and tool execution
                inner_agent = LlmAgent(
                    name=self.name,
                    model=self.model_id,
                    instruction=self.agent_instruction(
                        ctx
                    ),  # Call with context for dynamic instruction
                    description=self.agent_description,
                    tools=[FunctionTool(func=tool) for tool in toolbox_tools],
                    sub_agents=[],
                )

                logger.info("[%s] Starting inner LlmAgent execution", self.name)

                # Delegate execution to the inner agent and yield all events
                # This maintains full event streaming from the LLM agent
                async for event in inner_agent.run_async(ctx):
                    yield event

                logger.info("[%s] Execution completed successfully", self.name)

        except Exception as e:
            logger.error(
                "[%s] Error during execution: %s", self.name, str(e), exc_info=True
            )
            raise

    @override
    async def _run_live_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Live execution mode - delegates to _run_async_impl.

        Args:
            ctx: InvocationContext containing session state and user information

        Yields:
            Event: All events generated during execution
        """
        async for event in self._run_async_impl(ctx):
            yield event


# =============================================================================
# DB AGENT INSTANCE
# =============================================================================

# Create the db_agent instance with MCP Toolbox configuration
# This instance can be imported and used as a sub-agent of the root agent
db_agent = DbAgent(
    name=db_settings.agent_name,
    toolbox_url=db_settings.toolbox_url,  # Extract SecretStr value
    toolbox_toolset=db_settings.toolbox_toolset,
    model_id=db_settings.get_model(),
    agent_instruction=db_settings.agent_instruction,
    agent_description=db_settings.agent_description,
)
