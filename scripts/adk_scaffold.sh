#!/bin/bash

# ADK Agent Scaffold Script
# Creates a new ADK agent from the scaffold template

set -e  # Exit on error

# Color codes for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Show help/usage
show_help() {
    cat << 'EOF'
ADK Agent Scaffold - Quick scaffolding for production-ready ADK agents

USAGE:
    adk_scaffold <agent_name> [target_directory] [OPTIONS]

ARGUMENTS:
    agent_name          Name of the agent to create (required)
    target_directory    Directory where agent will be created (default: current directory)

OPTIONS:
    -h, --help         Show this help message
    -m, --minimal      Create minimal setup without Docker files
                       (skips: Dockerfile, pyproject.toml, .dockerignore)
    -s, --with-subagent
                       Include database sub-agent example with MCP toolbox integration
                       (creates: agent/sub_agents/db_agent/ structure)

EXAMPLES:
    # Create full agent setup with Docker support
    adk_scaffold rag_agent

    # Create agent in specific directory
    adk_scaffold rag_agent ~/projects/agents/

    # Create minimal agent without Docker files
    adk_scaffold rag_agent --minimal
    adk_scaffold rag_agent -m

    # Create agent with database sub-agent example
    adk_scaffold rag_agent --with-subagent
    adk_scaffold rag_agent -s

    # Combine options: minimal setup with sub-agent
    adk_scaffold rag_agent --minimal --with-subagent

    # Minimal agent in specific directory
    adk_scaffold rag_agent ~/projects/ --minimal

STRUCTURE CREATED:
    agent_name/
    ├── __init__.py              # Root package init
    ├── pyproject.toml           # Project dependencies (full mode only)
    ├── Dockerfile               # Docker build config (full mode only)
    ├── .dockerignore            # Docker ignore patterns (full mode only)
    ├── README.md                # Agent documentation
    └── agent_name/
        ├── __init__.py          # Agent package init
        ├── main.py              # FastAPI server with A2A support
        ├── .env.template        # Environment variables template
        ├── agent.json           # ADK agent metadata
        ├── core/                # Configuration module
        │   ├── __init__.py
        │   ├── base_config.py   # Base configuration for inheritance
        │   ├── config.py        # Main agent configuration
        │   ├── prompts.py       # Agent instructions
        │   └── logging_config.py
        └── agent/
            ├── __init__.py
            ├── agent.py         # Agent definition
            ├── sub_agents/      # Sub-agents (with --with-subagent)
            │   └── db_agent/    # Database sub-agent example
            │       ├── __init__.py
            │       ├── config.py
            │       ├── prompts.py
            │       └── agent.py
            └── tools/
                ├── __init__.py
                └── toolset.py   # Agent tools

All 'adk_agent' references are automatically replaced with your agent name.

EOF
}

# Main function
adk_scaffold() {
    local agent_name=""
    local target_dir="."
    local minimal_mode=false
    local with_subagent=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                return 0
                ;;
            -m|--minimal)
                minimal_mode=true
                shift
                ;;
            -s|--with-subagent)
                with_subagent=true
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                return 1
                ;;
            *)
                if [ -z "$agent_name" ]; then
                    agent_name="$1"
                elif [ "$target_dir" = "." ]; then
                    target_dir="$1"
                else
                    print_error "Too many arguments"
                    echo "Use --help for usage information"
                    return 1
                fi
                shift
                ;;
        esac
    done

    # Validate agent name
    if [ -z "$agent_name" ]; then
        print_error "Agent name is required"
        echo ""
        echo "Usage: adk_scaffold <agent_name> [target_directory] [OPTIONS]"
        echo "Try 'adk_scaffold --help' for more information"
        return 1
    fi

    # Validate agent name format (Python package naming)
    if ! [[ "$agent_name" =~ ^[a-z][a-z0-9_]*$ ]]; then
        print_error "Invalid agent name: '$agent_name'"
        echo "Agent name must:"
        echo "  - Start with a lowercase letter"
        echo "  - Contain only lowercase letters, numbers, and underscores"
        echo "  - Example: my_agent, rag_agent, data_processor"
        return 1
    fi

    # Check if target directory exists or can be created
    if [ ! -d "$target_dir" ]; then
        print_warning "Target directory does not exist: $target_dir"
        read -p "Create it? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Aborted"
            return 1
        fi
        mkdir -p "$target_dir"
    fi

    local agent_root="$target_dir/$agent_name"

    # Check if agent directory already exists
    if [ -d "$agent_root" ]; then
        print_error "Directory already exists: $agent_root"
        return 1
    fi

    # Create temporary directory for cloning
    local temp_dir=$(mktemp -d)

    print_info "Fetching latest scaffold template..."
    if ! git clone https://github.com/VENKATESHWARAN-R/adk_scaffold.git "$temp_dir" --quiet --depth 1; then
        print_error "Failed to clone template repository"
        rm -rf "$temp_dir"
        return 1
    fi

    print_info "Setting up agent: $agent_name"
    if [ "$minimal_mode" = true ]; then
        print_info "Mode: Minimal (without Docker files)"
    else
        print_info "Mode: Full (with Docker support)"
    fi
    
    if [ "$with_subagent" = true ]; then
        print_info "Sub-agents: Enabled (including db_agent example)"
    else
        print_info "Sub-agents: Disabled (use --with-subagent to include)"
    fi

    # Create directory structure
    mkdir -p "$agent_root/$agent_name"

    # Copy template files
    if [ -d "$temp_dir/adk_agent" ]; then
        # Copy all files from adk_agent/ to agent_name/agent_name/
        # Copy all regular files and directories
        cp -r "$temp_dir/adk_agent/"* "$agent_root/$agent_name/" 2>/dev/null || true
        # Copy all hidden files (starting with .)
        cp -r "$temp_dir/adk_agent/".* "$agent_root/$agent_name/" 2>/dev/null || true

        # Remove sub_agents directory if --with-subagent is not specified
        if [ "$with_subagent" = false ]; then
            if [ -d "$agent_root/$agent_name/agent/sub_agents" ]; then
                rm -rf "$agent_root/$agent_name/agent/sub_agents"
                print_info "Skipped sub-agents (use --with-subagent to include)"
            fi
        fi

        # Copy root level files
        cp "$temp_dir/__init__.py" "$agent_root/"

        if [ "$minimal_mode" = false ]; then
            # Copy Docker and build files only in full mode
            [ -f "$temp_dir/Dockerfile" ] && cp "$temp_dir/Dockerfile" "$agent_root/"
            [ -f "$temp_dir/pyproject.toml" ] && cp "$temp_dir/pyproject.toml" "$agent_root/"
            [ -f "$temp_dir/.dockerignore" ] && cp "$temp_dir/.dockerignore" "$agent_root/"
        fi
    else
        print_error "Template structure not found in repository"
        rm -rf "$temp_dir" "$agent_root"
        return 1
    fi

    # Generate custom README for the new agent
    cat > "$agent_root/README.md" << READMEEOF
# $agent_name

Production-ready ADK agent created from the scaffold template.

## Features

✅ **Production FastAPI Server** - Auth, observability, health checks
✅ **Langfuse Integration** - Complete tracing and monitoring
✅ **Pydantic Config** - Type-safe settings with validation
✅ **A2A Protocol Support** - Agent-to-Agent communication
$([ "$with_subagent" = true ] && echo "✅ **Sub-Agent Architecture** - Database sub-agent with MCP toolbox")
$([ "$minimal_mode" = false ] && echo "✅ **Docker Ready** - Multi-stage builds with uv")

## Quick Start

### Setup

1. Navigate to agent directory:
   \`\`\`bash
   cd $agent_name
   \`\`\`

2. Configure environment:
   \`\`\`bash
   cd $agent_name
   cp .env.template .env
   # Edit .env with your configuration (MODEL_ID, etc.)
   \`\`\`

3. Install dependencies:
   \`\`\`bash
$(if [ "$minimal_mode" = false ]; then
    echo "   pip install -e ."
else
    echo "   pip install google-adk[a2a]>=1.16.0 langfuse>=3.6.2 litellm>=1.77.7 pydantic>=2.12.0 pydantic-settings>=2.11.0 python-dotenv>=1.1.1 fastapi>=0.104.0 uvicorn>=0.24.0"
fi)
   \`\`\`

### Run

\`\`\`bash
# Using FastAPI server (with A2A support)
python -m $agent_name.main

# Or using ADK CLI
adk web .
adk run .
\`\`\`

$([ "$minimal_mode" = false ] && cat << 'DOCKEREOF'
### Docker Deployment

\`\`\`bash
# Build
docker build -t ${agent_name} .

# Run
docker run -p 8080:8080 --env-file ${agent_name}/.env ${agent_name}
\`\`\`

DOCKEREOF
)

## Project Structure

\`\`\`
$agent_name/
├── __init__.py              # Root package wrapper
$([ "$minimal_mode" = false ] && echo "├── pyproject.toml           # Project dependencies")
$([ "$minimal_mode" = false ] && echo "├── Dockerfile               # Production Docker build")
$([ "$minimal_mode" = false ] && echo "├── .dockerignore")
└── $agent_name/
    ├── __init__.py          # Agent initialization
    ├── main.py              # FastAPI server with A2A
    ├── .env.template        # Environment template
    ├── agent.json           # ADK agent metadata
    ├── core/                # Configuration module
    │   ├── __init__.py
    │   ├── base_config.py   # Base configuration for inheritance
    │   ├── config.py        # Pydantic settings
    │   ├── prompts.py       # Agent instructions
    │   └── logging_config.py
    └── agent/
        ├── __init__.py
        ├── agent.py         # Agent definition
$([ "$with_subagent" = true ] && cat << 'SUBEOF'
        ├── sub_agents/      # Sub-agent implementations
        │   └── db_agent/    # Database sub-agent (MCP toolbox)
        │       ├── __init__.py
        │       ├── config.py     # DB agent configuration
        │       ├── prompts.py    # DB agent prompts
        │       └── agent.py      # DB agent instance
SUBEOF
)        └── tools/
            ├── __init__.py
            └── toolset.py   # Agent tools
\`\`\`

## Configuration

Essential settings in \`$agent_name/.env\`:

\`\`\`bash
MODEL_ID="gemini-2.5-flash"
AGENT_NAME="$agent_name"
DATABASE_URL="sqlite:///:memory:"
\`\`\`

Optional production settings:

\`\`\`bash
# API Authentication
ADK_API_KEYS="sk-your-key-here"

# Langfuse Observability
LANGFUSE_ENABLED="true"
LANGFUSE_PUBLIC_KEY="pk-xxx"
LANGFUSE_SECRET_KEY="sk-xxx"
LANGFUSE_HOST="https://cloud.langfuse.com"

# A2A Protocol
ENABLE_A2A="true"
\`\`\`

$([ "$with_subagent" = true ] && cat << 'SUBAGENTCONFIGEOF'
### Sub-Agent Configuration (Database Agent)

The database sub-agent uses the MCP (Model Context Protocol) toolbox for data operations:

\`\`\`bash
# MCP Toolbox Configuration
TOOLBOX_URL="http://localhost:9000"
TOOLBOX_TOOLSET="my-toolset"

# Optional: Override model for database sub-agent
DB_AGENT_MODEL_ID="gemini-2.0-flash-exp"
DB_AGENT_NAME="db_agent"
\`\`\`

To integrate the db_agent with your root agent, edit \`$agent_name/agent/agent.py\`:

\`\`\`python
from ${agent_name}.agent.sub_agents.db_agent.agent import db_agent

root_agent = LlmAgent(
    # ... other config ...
    sub_agents=[db_agent],  # Add database sub-agent
)
\`\`\`

SUBAGENTCONFIGEOF
)

## Customization

### 1. Add Tools

Edit \`$agent_name/agent/tools/toolset.py\`:

\`\`\`python
def your_custom_tool(param: str) -> str:
    """Tool description."""
    return result

agent_tools = [your_custom_tool]
\`\`\`

### 2. Configure Settings

Edit \`$agent_name/config.py\`:

\`\`\`python
class AgentConfig(BaseSettings):
    # Add your custom fields
    custom_setting: str = Field(default="value")
\`\`\`

### 3. Customize Prompts

Edit \`$agent_name/prompts.py\` for agent behavior and instructions.

## API Usage

### Health Check
\`\`\`bash
curl http://localhost:8080/health
\`\`\`

### Agent Interaction (with auth)
\`\`\`bash
curl -H "X-API-KEY: your-key" \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Hello"}' \\
     http://localhost:8080/api/agents/$agent_name
\`\`\`

### A2A Endpoint
\`\`\`bash
curl -H "Content-Type: application/json" \\
     -d '{"messages": [{"role": "user", "content": "Hello"}]}' \\
     http://localhost:8080/a2a/$agent_name/
\`\`\`

## Resources

- [ADK Agent Scaffold](https://github.com/VENKATESHWARAN-R/adk_scaffold)
- [Google ADK Docs](https://cloud.google.com/vertex-ai/docs/adk)
- [Langfuse Docs](https://langfuse.com/docs)
- [LiteLLM Docs](https://docs.litellm.ai/)

---

**🚀 Production-ready ADK agent**
READMEEOF

    # Replace all adk_agent references with the new agent name
    print_info "Replacing template references..."

    # Function to replace in file (handles both GNU and BSD sed)
    # Uses | as delimiter to avoid conflicts with / in paths
    replace_in_file() {
        local file="$1"
        local old="$2"
        local new="$3"

        if sed --version >/dev/null 2>&1; then
            # GNU sed
            sed -i "s|${old}|${new}|g" "$file"
        else
            # BSD sed (macOS)
            sed -i '' "s|${old}|${new}|g" "$file"
        fi
    }

    # Replace in Python files
    find "$agent_root" -type f -name "*.py" -print0 | while IFS= read -r -d '' file; do
        replace_in_file "$file" "adk_agent" "$agent_name"
        replace_in_file "$file" "adk-agent" "${agent_name//_/-}"
    done

    # Replace in JSON files (agent.json)
    find "$agent_root" -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
        replace_in_file "$file" "adk_agent" "$agent_name"
    done

    # Replace in .env.template
    if [ -f "$agent_root/$agent_name/.env.template" ]; then
        replace_in_file "$agent_root/$agent_name/.env.template" "adk_agent" "$agent_name"
    fi

    # Replace in pyproject.toml (only in full mode)
    if [ "$minimal_mode" = false ] && [ -f "$agent_root/pyproject.toml" ]; then
        replace_in_file "$agent_root/pyproject.toml" "adk-agent" "${agent_name//_/-}"
        replace_in_file "$agent_root/pyproject.toml" "adk_agent" "$agent_name"
    fi

    # Replace in Dockerfile (only in full mode)
    if [ "$minimal_mode" = false ] && [ -f "$agent_root/Dockerfile" ]; then
        replace_in_file "$agent_root/Dockerfile" "adk_agent" "$agent_name"
        # Replace the app/ reference with agent_name/
        replace_in_file "$agent_root/Dockerfile" "COPY app/" "COPY $agent_name/"
        replace_in_file "$agent_root/Dockerfile" "/app/app/" "/app/$agent_name/"
        replace_in_file "$agent_root/Dockerfile" "uvicorn app.main:app" "uvicorn $agent_name.main:app"
    fi

    # Clean up
    rm -rf "$temp_dir"

    # Success message
    echo ""
    print_success "Agent '$agent_name' created successfully!"
    echo ""
    echo "📁 Created structure:"
    echo "  $agent_name/"
    echo "  ├── __init__.py"
    if [ "$minimal_mode" = false ]; then
        echo "  ├── pyproject.toml"
        echo "  ├── Dockerfile"
        echo "  ├── .dockerignore"
    fi
    echo "  ├── README.md"
    echo "  └── $agent_name/"
    echo "      ├── __init__.py"
    echo "      ├── main.py"
    echo "      ├── .env.template"
    echo "      ├── agent.json"
    echo "      ├── core/"
    echo "      │   ├── __init__.py"
    echo "      │   ├── base_config.py"
    echo "      │   ├── config.py"
    echo "      │   ├── prompts.py"
    echo "      │   └── logging_config.py"
    echo "      └── agent/"
    echo "          ├── __init__.py"
    echo "          ├── agent.py"
    if [ "$with_subagent" = true ]; then
        echo "          ├── sub_agents/"
        echo "          │   └── db_agent/"
        echo "          │       ├── __init__.py"
        echo "          │       ├── config.py"
        echo "          │       ├── prompts.py"
        echo "          │       └── agent.py"
    fi
    echo "          └── tools/"
    echo "              ├── __init__.py"
    echo "              └── toolset.py"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. cd $agent_root/$agent_name"
    echo "  2. cp .env.template .env"
    echo "  3. Edit .env with your MODEL_ID and other settings"
    if [ "$minimal_mode" = false ]; then
        echo "  4. pip install -e .. (from $agent_name directory)"
    else
        echo "  4. Install dependencies (see README.md)"
    fi
    echo "  5. Customize core/prompts.py for your agent's role"
    echo "  6. Add tools to agent/tools/toolset.py"
    if [ "$with_subagent" = true ]; then
        echo "  7. Configure MCP toolbox in .env (TOOLBOX_URL, TOOLBOX_TOOLSET)"
        echo "  8. Integrate db_agent in agent/agent.py (see README)"
        echo "  9. python -m $agent_name.main"
    else
        echo "  7. python -m $agent_name.main"
    fi
    echo ""
    print_success "Happy coding! 🎉"
}

# If script is executed directly (not sourced), run the function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    adk_scaffold "$@"
fi
