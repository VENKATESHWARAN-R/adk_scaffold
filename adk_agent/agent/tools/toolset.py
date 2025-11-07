"""
Agent Tools Module

This module defines all tools available to the agent. Tools are functions
that the agent can call to perform specific actions or retrieve information.

Components:
    agent_tools: List of tool functions available to the agent

Usage:
    Define your tool functions here and add them to the agent_tools list.
    Each tool should be a regular Python function with clear documentation.

Example Tool Definition:
    def search_web(query: str) -> str:
        '''
        Search the web for information.

        Args:
            query: The search query string

        Returns:
            Search results as a formatted string
        '''
        # Tool implementation here
        return search_results

    # Add to agent_tools list
    agent_tools = [search_web, another_tool]

Tool Best Practices:
    - Use clear, descriptive function names
    - Include comprehensive docstrings with Args and Returns
    - Handle errors gracefully with try/except blocks
    - Return structured data when possible
    - Keep tool functions focused and single-purpose
    - Add type hints for better IDE support and validation

Integration with External Services:
    - Use configuration from config.AgentConfig for API keys, URLs, etc.
    - Implement timeout handling for external calls
    - Add appropriate logging for debugging
    - Consider rate limiting and retry logic

Example with External Service:
    import logging
    from config import settings

    logger = logging.getLogger(__name__)

    def fetch_data_from_api(endpoint: str) -> dict:
        '''
        Fetch data from external API.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response as dictionary
        '''
        try:
            # Use configuration from settings
            url = f"{settings.api_base_url}/{endpoint}"
            timeout = settings.api_timeout

            # Make API call with timeout
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            logger.info(f"Successfully fetched data from {endpoint}")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to fetch data: {str(e)}")
            return {"error": str(e)}
"""

from typing import List

# TODO: Import required libraries and utilities
# Examples:
# import requests
# from config import settings
# import logging

# TODO: Define your agent tool functions here
# Each function should be well-documented and handle errors appropriately


# Example tool (remove in production):
def example_calculator(a: int, b: int, operation: str = "add") -> int:
    """
    Perform basic arithmetic operations.

    Args:
        a: First number
        b: Second number
        operation: Operation to perform (add, subtract, multiply, divide)

    Returns:
        Result of the arithmetic operation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else 0,
    }
    return operations.get(operation, operations["add"])(a, b)


# List of all agent tools
# Add your tool functions to this list
agent_tools: List = [
    # TODO: Add your tool functions here
    # Example: example_calculator,
    example_calculator,
]
