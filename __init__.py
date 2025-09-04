"""
Research Agent Package

This package provides a scaffold template for creating ADK-based agents.
It includes all the necessary components for a functional agent that can be
customized for specific use cases.

Components:
    agent: Main agent definition and configuration
    config: Centralized configuration management
    prompts: Agent instructions and descriptions
    logging_config: Logging system setup

Usage:
    This package is designed to be used as a template. When scaffolding a new agent:
    1. Copy this directory structure
    2. Replace 'research_agent' references with your agent name
    3. Customize prompts and configuration for your use case
    4. Add appropriate tools and capabilities

Entry Point:
    The agent module contains the root_agent that will be discovered and executed
    by the ADK framework.
"""

from . import agent

__all__ = ["agent"]
