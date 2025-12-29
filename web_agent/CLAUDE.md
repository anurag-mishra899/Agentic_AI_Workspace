# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based web agent project that uses LLMs to automate browser interactions for tasks like job searching. The agents use Playwright for browser automation via MCP (Model Context Protocol) tools.

## Architecture

The project consists of Jupyter notebooks that create browser-controlling agents:

- **web_agent_v1.ipynb**: Basic MCP tool integration with LangChain agents
- **web_agent_da_v1.ipynb**: Advanced implementation using `deepagents` library with middleware support

### Key Dependencies

- `llm_utils` - Custom utility module located at `/Users/anuragmishra/Documents/AI Workspace/llm_utils/` providing model configurations (e.g., `openai_llm`)
- `deepagents` - Custom agent framework with `create_deep_agent` function and `FilesystemBackend`
- `mcp` - Model Context Protocol for tool communication
- `langchain-mcp-adapters` - Bridges MCP tools to LangChain
- `@playwright/mcp` - Playwright browser tools exposed via MCP (run via npx)

### Agent Flow

1. Initialize MCP stdio client with Playwright server (`npx @playwright/mcp@latest`)
2. Load browser tools via `load_mcp_tools(session)`
3. Create agent with system prompt, tools, and optional middleware
4. Stream agent execution with `astream()` method

### Middleware System

The `deepagents` agent supports middleware for context management:
- `LoggingMiddleware` - Logs messages and truncates long content (>2000 chars)
- `ContextEditingMiddleware` with `ClearToolUsesEdit` - Manages context window by clearing old tool uses

## Running the Notebooks

```bash
# Ensure the virtual environment is activated
source /Users/anuragmishra/Documents/AI\ Workspace/.venv/bin/activate

# Required packages (install if missing)
pip install mcp langchain-mcp-adapters

# Playwright MCP server runs via npx (requires Node.js)
npx @playwright/mcp@latest
```

## Important Paths

- Virtual environment: `/Users/anuragmishra/Documents/AI Workspace/.venv/`
- LLM utilities: `/Users/anuragmishra/Documents/AI Workspace/llm_utils/`
