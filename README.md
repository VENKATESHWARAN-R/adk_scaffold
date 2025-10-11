# ADK Agent Scaffold

Production-ready template for Google ADK agents with observability, authentication, and Docker support.

## Features

✅ **Production FastAPI Server** - Auth, observability, health checks
✅ **Langfuse Integration** - Complete tracing and monitoring
✅ **Pydantic Config** - Type-safe settings with validation
✅ **Docker Ready** - Multi-stage builds with uv
✅ **CLI Utility** - Quick scaffolding with `adk_scaffold` command
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
# Create new agent
adk_scaffold my_agent

# Or specify directory
adk_scaffold my_agent ~/projects/agents/
```

### Run Agent

```bash
cd my_agent
cp app/.env.template app/.env
# Edit app/.env with your settings

# Install dependencies
pip install -e .
# or: uv pip install -e .

# Run with FastAPI
python -m app.main

# Or use ADK CLI
adk web .
adk run .
```

## Project Structure

```
my_agent/
├── __init__.py              # ADK command wrapper
├── Dockerfile               # Production build
├── .dockerignore
├── pyproject.toml
├── README.md
└── app/
    ├── __init__.py         # Config initialization
    ├── main.py             # FastAPI server
    ├── config.py           # Pydantic settings
    ├── prompts.py          # Agent instructions
    ├── logging_config.py
    ├── .env.template       # Config template
    └── agent/
        ├── agent.py        # Agent definition
        └── tools/
            └── toolset.py  # Agent tools
```

## Configuration

### Essential Settings (app/.env)

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

Edit `app/agent/tools/toolset.py`:

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    return results

agent_tools = [search_web]
```

### 2. Configure Settings

Edit `app/config.py`:

```python
class AgentConfig(BaseSettings):
    # Add your fields
    api_endpoint: HttpUrl | None = Field(default=None)
    api_timeout: int = Field(default=30)
```

### 3. Customize Prompts

Edit `app/prompts.py` for agent behavior and instructions.

## Docker Deployment

```bash
# Build
docker build -t my-agent .

# Run
docker run -p 8080:8080 --env-file app/.env my-agent

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
# Install dev dependencies
pip install -e ".[dev]"

# Code quality
black .
ruff check .
mypy .

# Run tests
pytest
```

## ADK CLI Commands

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

Enable in `app/.env`:
```bash
LANGFUSE_ENABLED="true"
```

## Troubleshooting

**Import Errors:**
```bash
pip install -e .
```

**Configuration Issues:**
```bash
python -c "from app.config import settings; print(settings.model_dump())"
```

**Langfuse Connection:**
```bash
python -c "from langfuse import Langfuse; print(Langfuse().auth_check())"
```

## Architecture

- **Modular Design** - Clean separation of concerns
- **Type Safety** - Pydantic validation throughout
- **Security First** - Credential masking, API auth
- **Production Ready** - Health checks, monitoring, Docker

## Resources

- [Google ADK Docs](https://cloud.google.com/vertex-ai/docs/adk)
- [Langfuse Docs](https://langfuse.com/docs)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## License

MIT License

---

**Quick scaffolding for production-ready ADK agents**
