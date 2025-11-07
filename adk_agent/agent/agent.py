"""
Agent Module - Core Agent Definition and Configuration

This module defines the main agent instance that will be executed by the ADK framework.
It configures the agent with its model, tools, prompts, and any sub-agents.

Components:
    root_agent: Main LlmAgent instance configured with all necessary components

Configuration:
    - Uses settings from config module for consistent configuration management
    - Supports both direct model usage and LiteLLM proxy for model flexibility
    - Extensible design for adding tools and sub-agents

Usage:
    This module is automatically imported by the ADK framework. The root_agent
    instance serves as the entry point for agent execution.

Environment Variables:
    USE_LITELLM_PROXY: Set to "True" to use LiteLLM proxy instead of direct model access
    MODEL_ID: LLM model identifier (from config)
    AGENT_NAME: Agent instance name (from config)

Example:
    To add tools to your agent:

    from google.adk.tools import FunctionTool
    from agent.tools.toolset import agent_tools

    tools=[FunctionTool(func=tool) for tool in agent_tools]

    To add sub-agents:

    from specialist_agent import specialist

    sub_agents=[specialist]
"""

from google.adk.agents import LlmAgent
# from google.adk.tools import FunctionTool, AgentTool

from adk_agent.core.logging_config import setup_logging

from adk_agent.agent.config import settings
# from adk_agent.agent.tools.toolset import agent_tools

# Import sub-agents here if needed
# from adk_agent.agent.sub_agents.db_agent.agent import db_agent

# Initialize logging
setup_logging()

# Main agent instance configuration
# This agent will be automatically discovered and executed by the ADK framework
root_agent = LlmAgent(
    # Agent identification
    name=settings.agent_name,
    # Model configuration - automatically handles LiteLLM proxy
    # Uses settings.get_model() which checks USE_LITELLM_PROXY and openrouter/ prefix
    model=settings.get_model(),
    # Agent behavior configuration from prompts
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    # Tools and capabilities
    # TODO: Customize based on your agent requirements
    # If Using sub-agents as tools, uncomment the line below
    # tools=[AgentTool(agent=db_agent)],
    # Uncomment the line below when you add tools to toolset.py
    # tools=[FunctionTool(func=tool) for tool in agent_tools],
    tools=[],
    # Sub-agents for multi-agent workflows
    # TODO: Add sub-agents if needed for complex workflows
    # Example:
    # sub_agents=[
    #     research_specialist,
    #     data_analyst,
    #     report_writer,
    # ],
    sub_agents=[],
)
