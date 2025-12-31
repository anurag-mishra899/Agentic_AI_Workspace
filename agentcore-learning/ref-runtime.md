# AgentCore Runtime - Reference

## Overview

Amazon Bedrock AgentCore Runtime is a secure, serverless runtime designed for deploying and scaling AI agents and tools. It supports any frameworks, models, and protocols, enabling developers to transform local prototypes into production-ready solutions with minimal code changes.

## Key Features

### Framework and Model Flexibility
- Deploy agents from any framework (Strands Agents, LangChain, LangGraph, CrewAI, LlamaIndex)
- Use any model (Amazon Bedrock, OpenAI, Anthropic direct, etc.)

### Integration Points
- AgentCore Memory
- AgentCore Gateway
- AgentCore Observability
- AgentCore Tools

### Use Cases
- Real-time, interactive AI agents
- Long-running, complex AI workflows
- Multi-modal AI processing (text, image, audio, video)

## Core Pattern: The @app.entrypoint Decorator

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    """Your AI agent function"""
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
```

## Deployment Workflow

```bash
# 1. Install packages
pip install bedrock-agentcore strands-agents bedrock-agentcore-starter-toolkit

# 2. Test locally
python my_agent.py
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'

# 3. Configure and deploy
agentcore configure -e my_agent.py
agentcore launch

# 4. Invoke deployed agent
agentcore invoke '{"prompt": "tell me a joke"}'
```

## Tutorial Structure (from repository)

```
01-AgentCore-runtime/
├── 01-hosting-agent/           # Basic agent deployment
├── 02-hosting-MCP-server/      # MCP server on Runtime
├── 03-advanced-concepts/       # Advanced patterns
├── 04-hosting-ts-MCP-server/   # TypeScript MCP servers
├── 05-hosting-a2a/             # Agent-to-Agent communication
├── 06-bi-directional-streaming/ # Streaming patterns
└── 07-mcp-dynamic-client-registration/
```

## Required Permissions

- `BedrockAgentCoreFullAccess` managed policy
- `AmazonBedrockFullAccess` managed policy
- ECR permissions for container images
- IAM role creation permissions
