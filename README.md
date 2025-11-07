# ADK Agent Scaffold

Production-ready template for Google ADK agents with observability, authentication, and Docker support.

## Features

✅ **Production FastAPI Server** - Auth, observability, health checks, A2A support  
✅ **Langfuse Integration** - Complete tracing and monitoring  
✅ **Pydantic Config** - Type-safe settings with validation  
✅ **Docker Ready** - Multi-stage builds with uv (optional)  
✅ **CLI Utility** - Quick scaffolding with `adk_scaffold` command  
✅ **Flexible Setup** - Full or minimal mode with `--minimal` flag  
✅ **Sub-Agent Architecture** - Optional database sub-agent with MCP toolbox  
✅ **Sensitive Data Masking** - Automatic credential protection

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
cd ..
pip install -e .
# or: uv pip install -e .

# Run with FastAPI (A2A enabled)
python -m my_agent.main

# Or use ADK CLI (from parent directory)
adk web .
adk run .
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
    │   ├── config.py        # Pydantic settings
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

# Langfuse Observability
LANGFUSE_ENABLED="true"
LANGFUSE_PUBLIC_KEY="pk-xxx"
LANGFUSE_SECRET_KEY="sk-xxx"
LANGFUSE_HOST="https://cloud.langfuse.com"
```

### LiteLLM Support

```bash
USE_LITELLM_PROXY="True"
MODEL_ID="gpt-4o-mini"  # Any LiteLLM-supported model
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

Edit `my_agent/config.py`:

```python
class AgentConfig(BaseSettings):
    # Add your fields
    api_endpoint: HttpUrl | None = Field(default=None)
    api_timeout: int = Field(default=30)
```

### 3. Customize Prompts

Edit `my_agent/core/prompts.py` for agent behavior and instructions.

### 4. Add Sub-Agents (Optional)

If you created your agent with `--with-subagent`, you'll have a database sub-agent example:

**Configure the database sub-agent** in `my_agent/.env`:

```bash
# MCP Toolbox Configuration
TOOLBOX_URL="http://localhost:9000"
TOOLBOX_TOOLSET="my-toolset"

# Optional overrides
DB_AGENT_MODEL_ID="gemini-2.0-flash-exp"
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

## API Usage

### With Authentication

```bash
curl -H "X-API-KEY: your-key" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}' \
     http://localhost:8080/api/agents/my_agent
```

### Health Check

```bash
curl http://localhost:8080/health
```

## Development

```bash
# Install dev dependencies (full mode only)
pip install -e ".[dev]"

# Code quality
black .
ruff check .
mypy .

# Run tests
pytest
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
- **Configuration Inheritance** - Base configuration shared across main and sub-agents
- **Type Safety** - Pydantic validation throughout
- **Security First** - Credential masking, API auth
- **Production Ready** - Health checks, monitoring, Docker
- **Multi-Agent Support** - Optional sub-agents for specialized tasks

### Configuration Architecture

```
BaseAgentConfig (core/base_config.py)
├── Common settings: model_id, agent_name
│
├── AgentConfig (core/config.py)
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

- [Google ADK Docs](https://cloud.google.com/vertex-ai/docs/adk)
- [Langfuse Docs](https://langfuse.com/docs)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## License

MIT License

---

**Quick scaffolding for production-ready ADK agents**
