# OpenAI Agents with Azure Durable Functions - Samples

This directory contains sample code demonstrating how to use OpenAI agents with Azure Durable Functions for reliable, stateful AI workflows.

## 📖 Documentation

**Complete documentation is located at: [/docs/openai_agents/](/docs/openai_agents/)**

### Quick Links

- **[Getting Started Guide](/docs/openai_agents/getting-started.md)** - Setup and basic usage
- **[API Reference](/docs/openai_agents/reference.md)** - Complete technical reference  
- **[Overview](/docs/openai_agents/README.md)** - Feature overview and concepts

## 🚀 Quick Start

1. **Setup**: Follow the [Getting Started Guide](/docs/openai_agents/getting-started.md)
2. **Run Samples**: Explore the `/basic` directory for examples
3. **Reference**: Check [API Reference](/docs/openai_agents/reference.md) for advanced usage

## 📂 Sample Structure

```
basic/                           # Basic usage examples
├── hello_world.py              # Simplest agent example
├── tools.py                    # Function and activity tools
├── dynamic_system_prompt.py    # Dynamic prompt handling
├── lifecycle_example.py        # Agent lifecycle management
└── ...                         # Additional examples
```

## 🔧 Running Samples

```bash
# Install dependencies
pip install -r requirements.txt

# Start the Azure Functions runtime
func start

# Test with HTTP requests (see documentation for details)
```

**For complete setup instructions, configuration details, and troubleshooting, see the [Getting Started Guide](/docs/openai_agents/getting-started.md).**
