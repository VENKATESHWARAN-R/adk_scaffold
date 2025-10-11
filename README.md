# ADK Agent Scaffold Template

A production-ready scaffold template for creating Google ADK (Agent Development Kit) agents with built-in observability, authentication, and best practices.

## Features

- **Production-Grade FastAPI Server** - Complete HTTP server with authentication and monitoring
- **Langfuse Observability** - Optional tracing and monitoring integration
- **Pydantic Configuration** - Type-safe configuration management with validation
- **API Key Authentication** - Secure your agent endpoints
- **Modular Architecture** - Clean separation of concerns with organized structure
- **Sensitive Data Masking** - Automatic credential masking in logs
- **Tool Organization** - Dedicated module for agent tools
- **Environment-Based Config** - Comprehensive .env.template with all options

## Quick Setup

### Method 1: One-liner Install (Easiest)

```bash
curl -s https://raw.githubusercontent.com/VENKATESHWARAN-R/adk_scaffold/main/install.sh | bash
```

### Method 2: Download the Script

```bash
# Download the script
curl -O https://raw.githubusercontent.com/VENKATESHWARAN-R/adk_scaffold/main/adk_scaffold.sh

# Make it executable
chmod +x adk_scaffold.sh

# Move to a directory in your PATH (optional)
sudo mv adk_scaffold.sh /usr/local/bin/adk_scaffold
```

### Method 3: Clone and Add to PATH

```bash
# Clone the repository
git clone https://github.com/VENKATESHWARAN-R/adk_scaffold.git

# Add to your PATH in ~/.zshrc or ~/.bashrc
echo 'export PATH="$PATH:/path/to/adk_scaffold"' >> ~/.zshrc
source ~/.zshrc
```

## Project Structure

```
adk_agent/
├── main.py                      # Production FastAPI server with auth & observability
├── __init__.py                  # Package initialization with config logging
├── config.py                    # Pydantic-based configuration management
├── prompts.py                   # Agent instructions and descriptions
├── logging_config.py            # Centralized logging setup
├── .env.template                # Environment configuration template
├── pyproject.toml               # Project metadata and dependencies
├── agent/
│   ├── __init__.py
│   ├── agent.py                 # Main agent definition
│   └── tools/
│       ├── __init__.py
│       └── toolset.py           # Agent tools module
└── README.md
```

## Usage

### Creating a New Agent

```bash
# Create in current directory
adk_scaffold my_agent

# Create in specific directory
adk_scaffold my_agent ~/workspace/agents/
```

### Setting Up Your Agent

1. **Configure Environment Variables**
   ```bash
   cd my_agent
   cp .env.template .env
   # Edit .env with your configuration
   ```

2. **Install Dependencies**
   ```bash
   # Using pip
   pip install -e .

   # Using uv (recommended)
   uv pip install -e .
   ```

3. **Run the Agent Server**
   ```bash
   # Development mode
   python main.py

   # Or with uvicorn
   uvicorn main:app --reload
   ```

4. **Access the Web Interface**
   Open http://localhost:8080 in your browser

## Configuration Guide

### Essential Settings (.env)

```bash
# Core Agent Settings
MODEL_ID="gemini-2.5-flash"      # LLM model to use
AGENT_NAME="my_agent"             # Your agent's name
DATABASE_URL="sqlite:///:memory:" # Session storage

# Server Settings
HOST="0.0.0.0"
PORT="8080"
SERVE_WEB_INTERFACE="true"
```

### Production Settings

```bash
# API Authentication (Highly Recommended)
ADK_API_KEYS="sk-prod-key-123,sk-backup-key-456"

# Langfuse Observability
LANGFUSE_ENABLED="true"
LANGFUSE_PUBLIC_KEY="pk-your-key"
LANGFUSE_SECRET_KEY="sk-your-key"
LANGFUSE_HOST="https://cloud.langfuse.com"
```

### Using LiteLLM Proxy

```bash
# Enable LiteLLM for multi-provider support
USE_LITELLM_PROXY="True"
MODEL_ID="gpt-4o-mini"  # Use any LiteLLM-supported model
```

## Customization Guide

### 1. Adding Tools

Edit `agent/tools/toolset.py`:

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    # Your implementation
    return results

def analyze_data(data: dict) -> dict:
    """Analyze provided data."""
    # Your implementation
    return analysis

agent_tools = [search_web, analyze_data]
```

### 2. Customizing Prompts

Edit `prompts.py` to define your agent's behavior, instructions, and personality.

### 3. Adding Configuration

In `config.py`, add tool-specific settings:

```python
class AgentConfig(BaseSettings):
    # Existing fields...

    # Your custom configuration
    api_endpoint: HttpUrl = Field(
        default=None,
        description="External API endpoint"
    )

    api_timeout: int = Field(
        default=30,
        description="API timeout in seconds"
    )
```

Add to `SENSITIVE_FIELDS` if needed:

```python
SENSITIVE_FIELDS: set[str] = {
    "database_url",
    "api_key",  # Add your sensitive fields
}
```

### 4. Sub-Agents (Multi-Agent Workflows)

In `agent/agent.py`:

```python
from specialist_agent import research_agent, data_agent

root_agent = LlmAgent(
    name=settings.agent_name,
    model=settings.model_id,
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    tools=[FunctionTool(func=tool) for tool in agent_tools],
    sub_agents=[research_agent, data_agent],  # Add sub-agents
)
```

## API Usage

### With Authentication

```bash
curl -H "X-API-KEY: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}' \
     http://localhost:8080/api/agents/my_agent
```

### Health Check (No Auth Required)

```bash
curl http://localhost:8080/health
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type checking
mypy .
```

## Production Deployment

### Using Gunicorn

```bash
# Install production dependencies
pip install -e ".[prod]"

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[prod]"

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
```

## Observability with Langfuse

Langfuse provides:
- **Trace Analysis** - Complete visibility into agent execution
- **Performance Metrics** - Response times, token usage, costs
- **Debug Tools** - Inspect agent reasoning and tool calls
- **User Analytics** - Track usage patterns and errors

Enable by setting `LANGFUSE_ENABLED=true` in your .env file.

## Architecture Highlights

### Pydantic Configuration
- Type-safe configuration with validation
- Automatic environment variable loading
- Clear documentation with Field descriptions

### Sensitive Data Protection
- Automatic masking of credentials in logs
- URL password masking
- Configurable sensitive field list

### Modular Design
- Clean separation between server, agent, tools, and config
- Easy to test and maintain
- Extensible architecture

### Production-Ready Server
- Health checks for monitoring
- API key authentication
- CORS configuration
- OpenAPI documentation

## Best Practices

### Configuration Management
- Use environment variables for all settings
- Never commit .env files
- Document all configuration options
- Provide sensible defaults

### Security
- Always use API keys in production
- Mask sensitive data in logs
- Use HTTPS in production
- Rotate API keys regularly

### Tool Development
- Keep tools focused and single-purpose
- Include comprehensive docstrings
- Handle errors gracefully
- Add timeout handling for external calls

### Prompt Engineering
- Be specific and clear in instructions
- Include examples and use cases
- Define success criteria
- Specify do's and don'ts

## Troubleshooting

### Import Errors
```bash
# Ensure package is installed
pip install -e .
```

### Configuration Issues
```bash
# Check configuration is loaded correctly
python -c "from config import settings; print(settings.model_dump())"
```

### Langfuse Connection Issues
```bash
# Verify credentials
python -c "from langfuse import Langfuse; client = Langfuse(); print(client.auth_check())"
```

## Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/adk)
- [Langfuse Documentation](https://langfuse.com/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

---

**Note**: This scaffold provides a production-ready foundation for building robust, observable, and secure ADK agents. Customize it based on your specific requirements!
