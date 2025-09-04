# ADK Agent Scaffold Template

A comprehensive scaffold template for creating ADK (Agent Development Kit) based agents. This template provides a well-structured foundation with proper documentation, configuration management, and prompt templates.

## 🚀 Quick Setup

Add this function to your `~/.zshrc` or `~/.bashrc`:

```bash
adk_scaffold() {
    if [ -z "$1" ]; then
        echo "Usage: adk_scaffold <agent_name> [target_directory]"
        return 1
    fi
    
    local agent_name="$1"
    local target_dir="${2:-.}"
    local temp_dir=$(mktemp -d)
    
    echo "🚀 Fetching latest scaffold template..."
    git clone https://github.com/VENKATESHWARAN-R/adk_scaffold.git "$temp_dir" --quiet
    
    echo "📦 Setting up agent: $agent_name"
    
    # Copy template
    cp -r "$temp_dir/adk_agent" "$target_dir/$agent_name"
    
    # Replace all references
    find "$target_dir/$agent_name" -type f -name "*.py" -exec sed -i.bak "s/adk_agent/$agent_name/g" {} \;
    find "$target_dir/$agent_name" -type f -name "*.md" -exec sed -i.bak "s/adk_agent/$agent_name/g" {} \;
    
    # Clean up backup files
    find "$target_dir/$agent_name" -name "*.bak" -delete
    
    # Create additional files
    cat > "$target_dir/$agent_name/.env.template" << ENVEOF
# Environment Configuration for $agent_name
# Copy this file to .env and fill in your values

# Required: LLM Model Configuration
MODEL_ID=your-model-id-here

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s %(levelname)s [%(name)s] %(message)s

# Optional: Database Configuration
DATABASE_URL=

# Optional: LiteLLM Proxy
USE_LITELLM_PROXY=False

# Optional: Custom Agent Configuration
AGENT_INSTRUCTION=
AGENT_DESCRIPTION=

# Add your agent-specific environment variables here
ENVEOF

    cat > "$target_dir/$agent_name/requirements.txt" << REQEOF
# Core dependencies for ADK-based agents
google-adk[a2a]>=1.12.0
python-dotenv>=1.1.0
litellm>=1.72.7
langfuse>=3.3.2

# Add your agent-specific dependencies below:
REQEOF
    
    echo "🧹 Cleaning up..."
    rm -rf "$temp_dir"
    
    echo ""
    echo "✅ Agent '$agent_name' created successfully!"
    echo ""
    echo "📁 Created files:"
    echo "  ├── 🐍 __init__.py"
    echo "  ├── 🤖 agent.py"
    echo "  ├── ⚙️  config.py"
    echo "  ├── 📝 prompts.py"
    echo "  ├── 📊 logging_config.py"
    echo "  ├── 📖 README.md"
    echo "  ├── 🌍 .env.template"
    echo "  └── 📦 requirements.txt"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. cd $target_dir/$agent_name"
    echo "  2. cp .env.template .env"
    echo "  3. Edit .env with your configuration"
    echo "  4. Customize prompts.py for your agent's role"
    echo "  5. Add tools to agent.py"
    echo ""
    echo "🎉 Happy coding!"
}
```

After adding this to your shell config, reload it:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

## 📋 Usage

### Create a new agent:
```bash
adk_scaffold my_research_agent
```

### Create agent in specific directory:
```bash
adk_scaffold data_processor ~/workspace/agents/
```

### The scaffold will automatically:
- Copy the template files
- Replace all `adk_agent` references with your agent name
- Create environment configuration files
- Provide next steps for customization

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
