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
"""

import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from adk_agent.config import settings

# Main agent instance configuration
# This agent will be automatically discovered and executed by the ADK framework
root_agent = LlmAgent(
    # Agent identification
    name="adk_agent",  # TODO: Replace with actual agent name during scaffolding
    
    # Model configuration - supports both direct model and LiteLLM proxy
    model=settings.model_id
    if os.getenv("USE_LITELLM_PROXY") != "True"
    else LiteLlm(settings.model_id),
    
    # Agent behavior configuration
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    
    # Tools and capabilities (customize based on agent requirements)
    tools=[
        # TODO: Add agent-specific tools here
        # Example: google_search_tool, file_operations_tool, etc.
    ],
    
    # Sub-agents (for multi-agent workflows)
    sub_agents=[
        # TODO: Add sub-agents if needed for complex workflows
        # Example: specialist agents for specific tasks
    ]
)
