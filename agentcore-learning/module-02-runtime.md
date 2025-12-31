# Module 2: AgentCore Runtime

## 2.1 The `@app.entrypoint` Decorator Pattern

The Runtime is the **foundation of AgentCore** — it's where your agent code actually runs. The key abstraction is the `BedrockAgentCoreApp` class with its `@app.entrypoint` decorator.

### The Core Pattern

```python
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload: dict) -> dict:
    """
    This function becomes your agent's HTTP endpoint.

    Args:
        payload: JSON body from the request (dict)

    Returns:
        dict: JSON response to send back
    """
    user_input = payload.get("prompt", "")

    # Your agent logic here - ANY framework works
    response = process_with_your_agent(user_input)

    return {"result": response}

if __name__ == "__main__":
    app.run()  # Starts HTTP server on port 8080
```

### What the Decorator Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    @app.entrypoint                               │
│                                                                  │
│  1. Wraps your function in HTTP handler                         │
│  2. Parses incoming JSON → payload dict                         │
│  3. Calls your function with payload                            │
│  4. Serializes return dict → JSON response                      │
│  5. Handles errors, timeouts, logging                           │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Your Function                                    │
│                                                                  │
│  def invoke(payload):                                           │
│      # You only write business logic                            │
│      return {"result": "..."}                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Real Examples with Different Frameworks

**Strands Agents:**
```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.tools import calculator, web_search

app = BedrockAgentCoreApp()
agent = Agent(tools=[calculator, web_search])

@app.entrypoint
def invoke(payload):
    result = agent(payload["prompt"])
    return {
        "response": result.message,
        "tools_used": [t.name for t in result.tool_calls]
    }
```

**LangGraph:**
```python
from bedrock_agentcore import BedrockAgentCoreApp
from langgraph.graph import StateGraph

app = BedrockAgentCoreApp()

# Your LangGraph workflow
workflow = StateGraph(AgentState)
# ... define nodes and edges ...
graph = workflow.compile()

@app.entrypoint
def invoke(payload):
    result = graph.invoke({
        "messages": [HumanMessage(content=payload["prompt"])]
    })
    return {"response": result["messages"][-1].content}
```

**CrewAI:**
```python
from bedrock_agentcore import BedrockAgentCoreApp
from crewai import Agent, Task, Crew

app = BedrockAgentCoreApp()

researcher = Agent(role="Researcher", ...)
writer = Agent(role="Writer", ...)
crew = Crew(agents=[researcher, writer], tasks=[...])

@app.entrypoint
def invoke(payload):
    result = crew.kickoff(inputs={"topic": payload["topic"]})
    return {"result": str(result)}
```

---

## 2.2 Local Development with Docker

Before deploying, you test locally. AgentCore uses Docker for consistency between local and deployed environments.

### Local Testing Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   LOCAL DEVELOPMENT                           │
│                                                               │
│   1. Write agent code (my_agent.py)                          │
│   2. Run directly: python my_agent.py                        │
│   3. Test: curl http://localhost:8080/invocations            │
│   4. Iterate until working                                    │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   DOCKER TESTING                              │
│                                                               │
│   1. agentcore configure -e my_agent.py                      │
│   2. Docker image built automatically                         │
│   3. Test containerized version locally                       │
│   4. Matches production environment exactly                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   DEPLOY TO AWS                               │
│                                                               │
│   1. agentcore launch                                        │
│   2. Image pushed to ECR                                      │
│   3. Runtime provisions infrastructure                        │
│   4. Agent accessible via AWS endpoint                        │
└──────────────────────────────────────────────────────────────┘
```

### Project Structure

```
my-agent/
├── my_agent.py          # Your agent code with @app.entrypoint
├── requirements.txt     # Python dependencies
├── Dockerfile          # (Optional) Custom Dockerfile
└── .env                # (Optional) Environment variables
```

### Minimal requirements.txt

```
bedrock-agentcore
strands-agents          # Or your framework of choice
boto3
```

### Testing Locally

```bash
# Terminal 1: Start your agent
python my_agent.py
# Output: Starting server on http://0.0.0.0:8080

# Terminal 2: Test it
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2 + 2?"}'

# Response:
# {"result": "2 + 2 equals 4"}
```

---

## 2.3 `agentcore configure` and `agentcore launch`

The CLI abstracts away all deployment complexity.

### Step 1: Configure

```bash
agentcore configure -e my_agent.py
```

This command:
1. Analyzes your code to find the entrypoint
2. Scans `requirements.txt` for dependencies
3. Creates/updates deployment configuration
4. Builds Docker image locally

**Configuration Options:**

| Flag | Purpose | Example |
|------|---------|---------|
| `-e` | Entrypoint file | `-e my_agent.py` |
| `--name` | Runtime name | `--name my-prod-agent` |
| `--memory` | Memory allocation | `--memory 2048` |
| `--timeout` | Request timeout | `--timeout 300` |

### Step 2: Launch

```bash
agentcore launch
```

This command:
1. Pushes Docker image to ECR
2. Creates IAM roles with least-privilege
3. Provisions AgentCore Runtime
4. Returns endpoint URL

**What Gets Created:**

```
AWS Resources Created by 'agentcore launch':

┌─────────────────┐     ┌─────────────────┐
│   ECR Repo      │     │   IAM Role      │
│ (Container      │     │ (Execution      │
│  Image)         │     │  Permissions)   │
└─────────────────┘     └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌─────────────────────┐
         │  AgentCore Runtime  │
         │  (Serverless Host)  │
         │                     │
         │  • Auto-scaling     │
         │  • Load balancing   │
         │  • Health checks    │
         └─────────────────────┘
                     │
                     ▼
         ┌─────────────────────┐
         │   HTTPS Endpoint    │
         │ (Your Agent's URL)  │
         └─────────────────────┘
```

### Step 3: Invoke

```bash
# Using CLI
agentcore invoke '{"prompt": "Hello!"}'

# Using boto3
import boto3

client = boto3.client('bedrock-agentcore-runtime')
response = client.invoke_agent(
    agentId='your-agent-id',
    payload={'prompt': 'Hello!'}
)
```

### Other Useful Commands

```bash
# View logs
agentcore logs --follow

# Check status
agentcore status

# Update after code changes
agentcore configure -e my_agent.py
agentcore launch  # Deploys new version

# Tear down
agentcore destroy
```

---

## 2.4 Hosting MCP Servers on Runtime

Runtime can host not just agents, but also **MCP servers** — making your tools available to any MCP-compatible client.

### Why Host MCP Servers?

```
Traditional Approach:
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Agent A │────▶│ Tool 1  │     │ Agent B │────▶ (can't access Tool 1)
└─────────┘     └─────────┘     └─────────┘

With MCP Server on Runtime:
┌─────────┐     ┌─────────────────────┐     ┌─────────┐
│ Agent A │────▶│   MCP Server        │◀────│ Agent B │
└─────────┘     │   (on Runtime)      │     └─────────┘
                │   • Tool 1          │
                │   • Tool 2          │
                │   • Tool 3          │
                └─────────────────────┘
                         ▲
                         │
                    ┌─────────┐
                    │ Agent C │
                    └─────────┘
```

### Creating an MCP Server

```python
from bedrock_agentcore import BedrockAgentCoreApp
from mcp.server import Server
from mcp.types import Tool, TextContent

app = BedrockAgentCoreApp()
mcp_server = Server("my-tools")

# Define tools using MCP protocol
@mcp_server.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your implementation
    return f"Weather in {city}: 72°F, Sunny"

@mcp_server.tool()
async def search_database(query: str) -> str:
    """Search the company database."""
    # Your implementation
    return f"Results for '{query}': ..."

# Expose MCP server via Runtime
@app.entrypoint
def invoke(payload):
    # Handle MCP protocol messages
    return mcp_server.handle_request(payload)

if __name__ == "__main__":
    app.run()
```

### Connecting Agents to MCP Server

Once deployed, any agent can connect:

```python
from strands import Agent
from strands.mcp import MCPClient

# Connect to your MCP server on Runtime
mcp_client = MCPClient(
    endpoint="https://your-runtime-endpoint.aws",
    # Authentication handled by AgentCore Identity
)

agent = Agent(
    tools=mcp_client.get_tools()  # Dynamically loads tools
)

result = agent("What's the weather in Seattle?")
# Agent automatically uses get_weather tool from MCP server
```

---

## 2.5 Agent-to-Agent (A2A) Communication

Complex systems need multiple specialized agents working together.

### A2A Pattern

```
┌──────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                            │
│                     (Deployed on Runtime)                         │
│                                                                   │
│   "I need to help user plan a trip"                              │
│                                                                   │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │ Route to    │  │ Route to    │  │ Route to    │             │
│   │ Flight      │  │ Hotel       │  │ Activities  │             │
│   │ Agent       │  │ Agent       │  │ Agent       │             │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└──────────┼────────────────┼────────────────┼─────────────────────┘
           │                │                │
           ▼                ▼                ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │  Flight    │   │   Hotel    │   │ Activities │
    │  Agent     │   │   Agent    │   │   Agent    │
    │ (Runtime)  │   │ (Runtime)  │   │ (Runtime)  │
    └────────────┘   └────────────┘   └────────────┘
```

### Implementation

**Specialist Agent (flight_agent.py):**
```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent(
    system_prompt="You are a flight booking specialist..."
)

@app.entrypoint
def invoke(payload):
    result = agent(payload["request"])
    return {"flights": result.message}
```

**Orchestrator Agent (orchestrator.py):**
```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.client import AgentCoreClient
from strands import Agent, tool

app = BedrockAgentCoreApp()

# Clients for specialist agents
flight_client = AgentCoreClient(agent_id="flight-agent-id")
hotel_client = AgentCoreClient(agent_id="hotel-agent-id")

@tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights."""
    response = flight_client.invoke({
        "request": f"Find flights from {origin} to {destination} on {date}"
    })
    return response["flights"]

@tool
def search_hotels(city: str, checkin: str, checkout: str) -> str:
    """Search for available hotels."""
    response = hotel_client.invoke({
        "request": f"Find hotels in {city} from {checkin} to {checkout}"
    })
    return response["hotels"]

orchestrator = Agent(
    system_prompt="You help users plan trips...",
    tools=[search_flights, search_hotels]
)

@app.entrypoint
def invoke(payload):
    result = orchestrator(payload["prompt"])
    return {"response": result.message}
```

### IAM for A2A

Agents need permission to invoke each other:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeAgent",
      "Resource": [
        "arn:aws:bedrock-agentcore:*:*:agent/flight-agent-id",
        "arn:aws:bedrock-agentcore:*:*:agent/hotel-agent-id"
      ]
    }
  ]
}
```

---

## 2.6 Bi-Directional Streaming

For real-time interactions, Runtime supports streaming responses.

### Why Streaming?

```
Without Streaming:
User ──request──▶ Agent ──────────────────▶ Response (after 30s)
                         (user waits...)

With Streaming:
User ──request──▶ Agent ──token──▶ "The"
                        ──token──▶ "weather"
                        ──token──▶ "in"
                        ──token──▶ "Seattle"
                        ──token──▶ "is..."
                  (user sees progress immediately)
```

### Implementing Streaming

```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.streaming import StreamingResponse

app = BedrockAgentCoreApp()

@app.entrypoint
async def invoke(payload):
    async def generate():
        # Stream tokens as they're generated
        async for token in agent.stream(payload["prompt"]):
            yield {"token": token}

        # Final message
        yield {"done": True}

    return StreamingResponse(generate())
```

### Client-Side Streaming

```python
from bedrock_agentcore.client import AgentCoreClient

client = AgentCoreClient(agent_id="your-agent-id")

# Streaming invocation
for chunk in client.invoke_stream({"prompt": "Tell me a story"}):
    if "token" in chunk:
        print(chunk["token"], end="", flush=True)
    elif chunk.get("done"):
        print("\n[Complete]")
```

---

## Module 2 Summary

### Key Points

1. **`@app.entrypoint`** is the single integration point — wraps your function in HTTP handling

2. **Local development** uses the same code that runs in production — `python my_agent.py` for testing

3. **`agentcore configure` + `agentcore launch`** handles all deployment complexity (ECR, IAM, infrastructure)

4. **MCP Servers** can be hosted on Runtime, making tools shareable across agents

5. **A2A Communication** enables multi-agent architectures with orchestrators and specialists

6. **Streaming** provides real-time responses for better UX

### Deployment Flow

```
Write Code → Test Locally → Configure → Launch → Invoke
     │            │             │          │         │
my_agent.py   curl test    agentcore   agentcore  agentcore
                           configure    launch     invoke
```

---

## Comprehension Check

1. What does the `@app.entrypoint` decorator do to your function?

2. What AWS resources does `agentcore launch` create?

3. When would you host an MCP server on Runtime instead of just an agent?

4. In A2A communication, how does the orchestrator agent call specialist agents?
