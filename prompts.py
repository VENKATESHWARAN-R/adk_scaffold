"""
Agent Prompts and Descriptions Module

This module defines the system instructions and descriptions for the agent.
Contains template functions for agent configuration that can be customized
for different agent types and use cases.

Functions:
    get_agent_instruction(context): Returns the main system instruction/prompt
    get_agent_description(): Returns a brief description of the agent's purpose
    
Notes:
    - Instructions can be overridden via AGENT_INSTRUCTION environment variable
    - Descriptions can be overridden via AGENT_DESCRIPTION environment variable
    - Templates should be customized based on specific agent requirements
"""

import datetime
import logging
import os
import textwrap as tx

from google.adk.agents.readonly_context import ReadonlyContext

logger = logging.getLogger(__name__)


def get_agent_instruction(context: ReadonlyContext) -> str:
    """
    Returns the system instruction/prompt for the agent.
    
    This function provides the core behavioral template for agents. Customize this
    template based on your specific agent's role, capabilities, and use case.
    
    Args:
        context (ReadonlyContext): Runtime context containing state and user information
        
    Returns:
        str: Complete system instruction for the agent
        
    Environment Variables:
        AGENT_INSTRUCTION: Override default instruction with custom prompt
    """
    # Template for a well-structured agent prompt
    # Customize sections below based on your agent's specific role and tools
    default_instruction = tx.dedent(
        """
        # [AGENT_NAME] - [Agent Role/Specialization]

        ## Core Mission & Identity
        You are a [ROLE_DESCRIPTION] specialized in [PRIMARY_FUNCTION]. Your primary responsibility 
        is to [MAIN_OBJECTIVE] by [KEY_METHODS]. You work [independently/collaboratively] to 
        [EXPECTED_OUTCOMES].

        ## Available Tools & Capabilities
        
        **Primary Tools:**
        - `tool_name(parameters)` - Brief description of when and how to use this tool
        - `another_tool(parameters)` - Purpose and usage guidelines
        
        **Secondary Tools:**
        - `utility_tool(parameters)` - Supporting functionality description

        ## Operational Workflow
        
        ### Step 1: [Initial Action]
        When you receive a request:
        - [Specific action or analysis to perform]
        - [What to identify or extract from the request]
        - [How to prioritize or categorize the work]

        ### Step 2: [Core Processing]
        Execute your main function by:
        - [Primary methodology or approach]
        - [Key strategies or techniques to employ]
        - [Quality checks or validation steps]

        ### Step 3: [Output & Delivery]
        Provide results in this format:
        - [How to structure responses]
        - [What information to include]
        - [Expected format or templates]

        ## Response Templates

        ### Standard Response Format
        ```
        ## [Response Title]
        
        ### [Section 1: Key Findings/Results]
        - **[Key Point]**: [Details]
        - **[Assessment]**: [Analysis]
        
        ### [Section 2: Recommendations/Actions]
        - [Actionable item 1]
        - [Actionable item 2]
        
        ### [Section 3: Additional Information]
        - [Supporting details]
        - [References or sources]
        ```

        ## Tool Usage Guidelines

        **When to use [Primary Tool]:**
        - [Specific scenario 1]
        - [Specific scenario 2]
        - [Trigger conditions]

        **When to use [Secondary Tool]:**
        - [Alternative scenarios]
        - [Fallback conditions]

        **Tool Usage Best Practices:**
        - Always [specific guideline]
        - Never [specific restriction]
        - Prefer [preferred approach] over [alternative approach]

        ## Communication Style & Behavior

        **Interaction Principles:**
        - [Communication style: formal/casual/technical]
        - [Response length: concise/detailed/comprehensive]
        - [Tone: supportive/authoritative/collaborative]

        **Quality Standards:**
        - Prioritize [accuracy/speed/thoroughness]
        - Always verify [specific validation requirements]
        - Include [required elements in responses]

        **Error Handling:**
        - If uncertain about [scenario], ask for clarification
        - When [tool/data] is unavailable, [alternative approach]
        - For [error condition], [specific response protocol]

        ## Do's and Don'ts

        **DO:**
        - [Specific positive behavior 1]
        - [Specific positive behavior 2]
        - [Required action or approach]

        **DON'T:**
        - [Specific restriction or prohibition]
        - [Behavior to avoid]
        - [Common mistake to prevent]

        ## Success Criteria
        Your performance will be measured by:
        - [Primary success metric]
        - [Secondary success metric]
        - [Quality indicator]
        - [User satisfaction measure]

        ## Examples & Use Cases

        **Example 1: [Common Scenario]**
        Input: [Sample input]
        Expected Process: [Step-by-step approach]
        Output: [Expected result format]

        **Example 2: [Edge Case]**
        Input: [Sample edge case]
        Handling: [How to manage this scenario]
        Output: [Expected response]
        """
    )
    configured_instruction = os.getenv("AGENT_INSTRUCTION", default_instruction)

    # Check if user information exists
    user_information = str(context.state.get("user_information"))
    if user_information:
        configured_instruction += "\n\nUser Information:\n" + user_information

    configured_instruction += (
        "\n\n"
        + "The current date and time is: "
        + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        + "\n"
        + "Today is: "
        + str(datetime.date.today().strftime("%A"))
    )
    return configured_instruction


def get_agent_description() -> str:
    """
    Returns a concise description of the agent's purpose and capabilities.
    
    This should be a brief, clear summary that can be used in agent registries,
    documentation, or when the agent introduces itself to other agents.
    
    Returns:
        str: Brief description of the agent's role and capabilities
        
    Environment Variables:
        AGENT_DESCRIPTION: Override default description with custom text
        
    Template Guidelines:
        - Keep to 1-3 sentences
        - Focus on primary function and key capabilities
        - Mention main tools or specializations
        - Use active, descriptive language
    """
    # Template for agent description
    # Customize this based on your agent's specific purpose
    default_description = tx.dedent(
        """
        [Agent Type] specialist that [primary function] using [main tools/methods]. 
        Provides [key outputs/services] to [target users/systems] through [approach/methodology]. 
        Specializes in [domain expertise] with focus on [specific capabilities or outcomes].
        """
    ).strip()
    
    configured_description = os.getenv("AGENT_DESCRIPTION", default_description)
    return configured_description
