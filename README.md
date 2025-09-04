# ADK Agent Scaffold Template

A comprehensive scaffold template for creating ADK (Agent Development Kit) based agents. This template provides a well-structured foundation with proper documentation, configuration management, and prompt templates.

## 🚀 Quick Setup

### Method 1: One-liner Install (Easiest)

```bash
curl -s https://raw.githubusercontent.com/VENKATESHWARAN-R/adk_scaffold/main/install.sh | bash
```

### Method 2: Download the Script

Download and set up the scaffold script:

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

### Method 4: Source Function (Alternative)

If you prefer to keep it as a shell function, add this to your `~/.zshrc` or `~/.bashrc`:

```bash
# Source the ADK scaffold function
source /path/to/adk_scaffold/adk_scaffold.sh
```

**After any setup method, you can use `adk_scaffold` from anywhere!**

## 📋 Usage

### Create a new agent

```bash
adk_scaffold my_research_agent
```

### Create agent in specific directory

```bash
adk_scaffold data_processor ~/workspace/agents/
```

### What the scaffold does automatically

- Copy the template files
- Replace all `adk_agent` references with your agent name
- Create environment configuration files
- Provide next steps for customization

## 💡 Why Use Method 1 (Separate Script)?

The separate script approach is recommended because:

- ✅ **Cleaner shell config**: Keeps your `.zshrc`/`.bashrc` minimal
- ✅ **Version control friendly**: Easy to update the script independently
- ✅ **Shell agnostic**: Works in bash, zsh, fish, etc.
- ✅ **Portable**: Can be called from other scripts or tools
- ✅ **No pollution**: Doesn't add large functions to your shell environment

## 🏗️ Template Structure

```
adk_agent/
├── __init__.py           # Package initialization and exports
├── agent.py              # Main agent definition and configuration
├── config.py             # Centralized configuration management
├── prompts.py            # Agent instructions and descriptions templates
├── logging_config.py     # Logging system setup
└── README.md            # Template documentation
```

## 🎯 Customization Guide

### 1. Agent Prompts (`prompts.py`)

The prompt template includes placeholder sections:

- **`[AGENT_NAME]`** - Replace with your agent's name
- **`[Agent Role/Specialization]`** - Define the agent's primary role
- **`[ROLE_DESCRIPTION]`** - Detailed description of what the agent does
- **`[PRIMARY_FUNCTION]`** - Main capability or service provided
- **`[MAIN_OBJECTIVE]`** - Core goal the agent works toward
- **`[KEY_METHODS]`** - How the agent accomplishes its objectives

### 2. Tools Configuration

In `agent.py`, add your tools to the `tools` list:

```python
tools=[
    google_search_tool,
    file_operations_tool,
    custom_analysis_tool,
],
```

### 3. Environment Variables

Required environment variables:

```bash
MODEL_ID=your-llm-model-id        # Required
LOG_LEVEL=INFO                    # Optional
DATABASE_URL=your-database-url    # Optional
USE_LITELLM_PROXY=True           # Optional
```

## 🎲 Agent Types & Examples

### Research Agent

- **Purpose**: Information gathering and analysis
- **Tools**: Search, web scraping, document analysis
- **Output**: Structured reports and recommendations

### Data Processing Agent

- **Purpose**: Transform and analyze data
- **Tools**: Data manipulation, visualization, statistics
- **Output**: Processed datasets and insights

### Task Automation Agent

- **Purpose**: Execute workflows and processes
- **Tools**: API calls, file operations, system commands
- **Output**: Completed tasks and status reports

## 🔧 Advanced Configuration

### Multi-Agent Workflows

```python
sub_agents=[
    specialist_research_agent,
    data_analysis_agent,
    report_generation_agent,
]
```

### Custom Configuration Options

```python
@dataclass
class AgentConfig:
    # Agent-specific settings
    api_endpoint: str = field(default_factory=lambda: os.getenv("API_ENDPOINT"))
    rate_limit: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT", "10")))
```

## 📝 Best Practices

### Prompt Engineering

- Use clear, specific instructions
- Include examples and use cases
- Define success criteria explicitly
- Specify do's and don'ts clearly

### Configuration Management

- Use environment variables for secrets
- Provide sensible defaults
- Document all configuration options

### Error Handling

- Include error handling strategies in prompts
- Provide fallback behaviors
- Log configuration issues appropriately

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Resources

- [ADK Documentation](https://docs.google.com/adk)
- [Agent Development Guide](https://docs.google.com/adk/agents)
- [Multi-Agent Workflows](https://docs.google.com/adk/multi-agent)

## 📄 License

This project is licensed under the MIT License.

---

**Note**: This scaffold provides a solid foundation for building robust, maintainable ADK agents. Customize it based on your specific requirements and use case!
