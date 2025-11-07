# ADK Agent Scaffold

Production-ready template for Google ADK agents with observability, authentication, and Docker support.

## Features

✅ **Production FastAPI Server** - Auth, observability, health checks  
✅ **Protocol Support** - A2A and AG-UI protocols out of the box  
✅ **CopilotKit Integration** - Frontend-ready with AG-UI protocol  
✅ **Langfuse Integration** - Complete tracing and monitoring  
✅ **Pydantic Config** - Type-safe settings with validation  
✅ **Docker Ready** - Multi-stage builds with uv (optional)  
✅ **CLI Utility** - Quick scaffolding with `adk_scaffold` command  
✅ **Sub-Agent Architecture** - Optional database sub-agent with MCP toolbox

## Quick Start

### Install CLI

```bash
# One-liner install
curl -s https://raw.githubusercontent.com/VENKATESHWARAN-R/adk_scaffold/main/scripts/install.sh | bash

# Or manual
curl -O https://raw.githubusercontent.com/VENKATESHWARAN-R/adk_scaffold/main/scripts/adk_scaffold.sh
chmod +x adk_scaffold.sh
sudo mv adk_scaffold.sh /usr/local/bin/adk_scaffold
```

### Create Agent

```bash
# Create new agent with full Docker support
adk_scaffold my_agent

# Create in specific directory
adk_scaffold my_agent ~/projects/agents/

# Create minimal agent (without Docker files)
adk_scaffold my_agent --minimal

# Get help
adk_scaffold --help
```

#### CLI Options

| Option            | Short | Description                                                                                     |
| ----------------- | ----- | ----------------------------------------------------------------------------------------------- |
| `--help`          | `-h`  | Show detailed usage information                                                                 |
| `--minimal`       | `-m`  | Create minimal setup without Docker files (excludes: Dockerfile, pyproject.toml, .dockerignore) |
| `--with-subagent` | `-s`  | Include database sub-agent example with MCP toolbox integration                                 |

**Examples:**

- `adk_scaffold rag_agent` - Creates a full agent with Docker support
- `adk_scaffold rag_agent --minimal` - Creates agent without Docker files
- `adk_scaffold rag_agent --with-subagent` - Creates agent with database sub-agent
- `adk_scaffold rag_agent -s -m` - Minimal agent with sub-agent
- `adk_scaffold rag_agent ~/projects/` - Creates agent in specific directory
- `adk_scaffold rag_agent ~/projects/ -m` - Minimal agent in specific directory

### Run Agent

```bash
cd my_agent/my_agent
cp .env.template .env
# Edit .env with your settings (MODEL_ID, etc.)

# Install dependencies (from parent directory)
cd ../..
uv sync

```bash
# Run with FastAPI (A2A enabled)
uvicorn my_agent.main:app --host 0.0.0.0 --port 8000

# Or use ADK CLI (from parent directory)
adk web .
adk run .
```

## Protocol Support

This template supports both **A2A** (Agent-to-Agent) and **AG-UI** (CopilotKit) protocols out of the box:

### A2A Protocol
- Enables agent-to-agent communication
- Automatic endpoints at `/a2a/{agent_name}/`
- Agent cards at `/a2a/{agent_name}/.well-known/agent-card.json`

### AG-UI Protocol (CopilotKit)
- Frontend integration ready at `/copilotkit`
- Compatible with CopilotKit framework
- Enable with `ENABLE_AG_UI="true"` in `.env`
- [Learn more about AG-UI integration](https://docs.copilotkit.ai/adk/quickstart?path=exiting-agent)
```

## Project Structure

```
my_agent/
├── __init__.py              # Root package wrapper
├── pyproject.toml           # Project dependencies
├── Dockerfile               # Production Docker build
├── .dockerignore            # Docker ignore patterns
├── README.md                # Agent documentation
└── my_agent/
    ├── __init__.py          # Agent initialization
    ├── main.py              # FastAPI server with A2A
    ├── .env.template        # Environment template
    ├── agent.json           # ADK agent metadata
    ├── core/                # Configuration module
    │   ├── __init__.py
    │   ├── base_config.py   # Base configuration for inheritance
    │   └── logging_config.py
    └── agent/
        ├── __init__.py
        ├── agent.py         # Agent definition
        ├── config.py        # Pydantic settings
        ├── prompts.py       # Agent instructions
        ├── sub_agents/      # Sub-agents (with --with-subagent)
        │   └── db_agent/    # Database sub-agent example
        │       ├── __init__.py
        │       ├── config.py
        │       ├── prompts.py
        │       └── agent.py
        └── tools/
            ├── __init__.py
            └── toolset.py   # Agent tools
```

**Note:** When using `--minimal` flag, Dockerfile, pyproject.toml, and .dockerignore are excluded. When using `--with-subagent` flag, the sub_agents/ directory structure is included.

## Configuration

### Essential Settings (my_agent/.env)

```bash
MODEL_ID="gemini-2.5-flash"
AGENT_NAME="my_agent"
DATABASE_URL="sqlite:///:memory:"
```

### Production Settings

```bash
# API Authentication
ADK_API_KEYS="sk-your-key-here"

# Enable AG-UI Protocol (CopilotKit integration)
ENABLE_AG_UI="true"

# Langfuse Observability
LANGFUSE_ENABLED="true"
LANGFUSE_PUBLIC_KEY="pk-xxx"
LANGFUSE_SECRET_KEY="sk-xxx"
LANGFUSE_HOST="https://cloud.langfuse.com"
```

### LiteLLM Support

```bash
USE_LITELLM_PROXY="True"
MODEL_ID="grok-code-fast-1"  # Any LiteLLM-supported model
LITELLM_PROXY_API_BASE="http://localhost:4000"
LITELLM_API_KEY="your-litellm-api-key"
```

### OpenRouter settings

```bash
USE_LITELLM_PROXY="False"
MODEL_ID="openrouter/x-ai/grok-code-fast-1"
OPENROUTER_API_KEY="your-openrouter-api-key"
LITELLM_PROXY_API_BASE=https://openrouter.ai/api/v1
```

## Customization

### 1. Add Tools

Edit `my_agent/agent/tools/toolset.py`:

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    return results

agent_tools = [search_web]
```

### 2. Configure Settings

Edit `my_agent/agent/config.py`:

```python
class AgentConfig(BaseSettings):
    # Add your fields
    api_endpoint: HttpUrl | None = Field(default=None)
    api_timeout: int = Field(default=30)
```

### 3. Customize Prompts

Edit `my_agent/agent/prompts.py` for agent behavior and instructions.

### 4. Add Sub-Agents (Optional)

If you created your agent with `--with-subagent`, you'll have a database sub-agent example:

**Configure the database sub-agent** in `my_agent/.env`:

```bash
# MCP Toolbox Configuration
TOOLBOX_URL="http://localhost:9000"
TOOLBOX_TOOLSET="my-toolset"

# Optional overrides
DB_AGENT_MODEL_ID="gemini-2.5-flash-lite"
DB_AGENT_NAME="db_agent"
```

**Integrate with root agent** in `my_agent/agent/agent.py`:

```python
from my_agent.agent.sub_agents.db_agent.agent import db_agent

root_agent = LlmAgent(
    # ... existing config ...
    sub_agents=[db_agent],  # Add database sub-agent
)
```

**How sub-agents work:**

- Sub-agents inherit base configuration from `core/base_config.py`
- Each sub-agent has its own `config.py`, `prompts.py`, and `agent.py`
- Sub-agents can have specialized tools (e.g., MCP toolbox for databases)
- The root agent can delegate tasks to sub-agents

**Create additional sub-agents:**

Follow the same pattern as `db_agent`:

```bash
my_agent/agent/sub_agents/
├── db_agent/          # Database operations
├── api_agent/         # API interactions (your custom agent)
└── search_agent/      # Web search (your custom agent)
```

Each sub-agent should inherit from `BaseAgentConfig` for shared settings.

## Docker Deployment

**Note:** Docker files are only included when creating agents without the `--minimal` flag.

```bash
# Build
docker build -t my-agent .

# Run
docker run -p 8080:8080 --env-file my_agent/.env my-agent

# Or with docker-compose
docker-compose up
```

### API Usage

### With Authentication

```bash
curl -H "X-API-KEY: your-key" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}' \
     http://localhost:8080/api/agents/my_agent
```

### AG-UI Endpoint

```bash
# CopilotKit integration endpoint (when ENABLE_AG_UI=true)
POST http://localhost:8080/copilotkit
```

### Health Check

```bash
curl http://localhost:8080/health
```

## Development

```bash
# Install dev dependencies (full mode only)
uv sync --dev

# Code quality
black .
ruff check .
mypy .

```

## ADK CLI Commands

Run these commands from the agent root directory (e.g., `my_agent/`):

```bash
adk web .         # Launch web interface
adk run .         # Run interactively
adk api_server .  # Start API server
```

## Observability

Langfuse provides:

- Complete execution traces
- Performance metrics
- Token usage and costs
- Error tracking

Enable in `my_agent/.env`:

```bash
LANGFUSE_ENABLED="true"
```

## Troubleshooting

**Import Errors:**

```bash
pip install -e .  # Run from agent root directory
```

**Configuration Issues:**

```bash
python -c "from my_agent.config import settings; print(settings.model_dump())"
```

**Langfuse Connection:**

```bash
python -c "from langfuse import Langfuse; print(Langfuse().auth_check())"
```

## Architecture

- **Modular Design** - Clean separation of concerns with `core/` and `agent/` modules
- **Protocol Support** - A2A and AG-UI protocols for multi-agent and frontend integration
- **Configuration Inheritance** - Base configuration shared across main and sub-agents
- **Type Safety** - Pydantic validation throughout
- **Security First** - Credential masking, API auth
- **Production Ready** - Health checks, monitoring, Docker

### Configuration Architecture

```
BaseAgentConfig (core/base_config.py)
├── Common settings: model_id, agent_name
│
├── AgentConfig (agent/config.py)
│   └── Main agent: database_url, tool settings
│
└── DbAgentConfig (agent/sub_agents/db_agent/config.py)
    └── Sub-agent: toolbox_url, toolbox_toolset
```

**Benefits:**

- Shared configuration reduces duplication
- Sub-agents can override inherited settings
- Environment variables provide flexible configuration
- Type-safe with Pydantic validation

## Resources

- [Google ADK Docs](https://google.github.io/adk-docs/)
- [CopilotKit AG-UI Integration](https://docs.copilotkit.ai/adk/quickstart?path=exiting-agent)
- [Langfuse Docs](https://langfuse.com/docs)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## License

MIT License

---

**Quick scaffolding for production-ready ADK agents**
