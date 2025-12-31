# Module 1: Foundation & Mental Model

## 1.1 The Problem Space: Why Agent Infrastructure is Hard

Before diving into AgentCore, let's understand the problem it solves. When you build an AI agent prototype, everything seems straightforward:

```python
# Your prototype - simple, clean, works locally
from langchain.agents import create_react_agent

agent = create_react_agent(llm, tools, prompt)
response = agent.invoke({"input": "What's the weather?"})
```

But moving to production exposes a cascade of infrastructure challenges:

### The Production Gap

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROTOTYPE                                            │
│  ✓ Single user          ✓ Local tools        ✓ No auth needed               │
│  ✓ Stateless            ✓ No monitoring      ✓ Hardcoded secrets            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ "Let's deploy this!"
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION REQUIREMENTS                              │
│  ? How do I handle 1000 concurrent users?                                   │
│  ? How do I secure access to user-specific data?                            │
│  ? How does the agent remember previous conversations?                      │
│  ? How do I monitor what the agent is doing?                                │
│  ? How do I share tools across multiple agents?                             │
│  ? How do I evaluate if the agent is performing well?                       │
│  ? How do I deploy without rewriting everything?                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Infrastructure You'd Have to Build

Without AgentCore, you'd need to build and maintain:

| Component | What You'd Build | Complexity |
|-----------|------------------|------------|
| **Hosting** | Containers, load balancers, auto-scaling | High |
| **Tool Management** | API gateway, Lambda integrations, auth proxies | High |
| **Authentication** | OAuth flows, token management, IdP integration | Very High |
| **Memory** | Database schema, vector stores, caching layer | High |
| **Monitoring** | Custom tracing, log aggregation, dashboards | Medium |
| **Evaluation** | Test frameworks, metrics pipelines, A/B testing | High |

**This is "undifferentiated heavy lifting"** — necessary but not unique to your business.

---

## 1.2 AgentCore Architecture Overview: The 7 Core Services

AgentCore's insight is to **separate agent logic from agent infrastructure**:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     YOUR AGENT LOGIC (What Makes You Unique)               │
│  • Business rules          • Domain knowledge        • User experience     │
│  • Conversation design     • Tool selection logic    • Prompt engineering  │
└────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ═══════════════════╪═══════════════════
                         AgentCore SDK (bedrock-agentcore)
                    ═══════════════════╪═══════════════════
                                       │
┌────────────────────────────────────────────────────────────────────────────┐
│                     AWS MANAGED INFRASTRUCTURE                              │
│                                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│   │ RUNTIME  │  │ GATEWAY  │  │ IDENTITY │  │  MEMORY  │                  │
│   │ Deploy & │  │ Tool     │  │ Auth &   │  │ State    │                  │
│   │ Scale    │  │ Registry │  │ AuthZ    │  │ Persist  │                  │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘                  │
│                                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                                │
│   │  TOOLS   │  │ OBSERVE  │  │  EVALS   │                                │
│   │ Code/    │  │ Trace &  │  │ Quality  │                                │
│   │ Browser  │  │ Monitor  │  │ Metrics  │                                │
│   └──────────┘  └──────────┘  └──────────┘                                │
└────────────────────────────────────────────────────────────────────────────┘
```

### Each Service Explained

| Service | Purpose | Key Problem Solved |
|---------|---------|-------------------|
| **Runtime** | Serverless hosting for agents | Deploy any framework without managing infrastructure |
| **Gateway** | Convert APIs/Lambda to MCP tools | Unified tool interface without rewrites |
| **Identity** | Authentication & authorization | Secure agent access to user resources |
| **Memory** | Short & long-term persistence | Agents remember across conversations |
| **Tools** | Code Interpreter & Browser | Secure sandboxed execution environments |
| **Observability** | Tracing & monitoring | Debug and monitor agent behavior |
| **Evaluations** | Quality assessment | Measure and improve agent performance |

---

## 1.3 Key Concepts: MCP Protocol, Tool Calling, Agent Patterns

### What is MCP (Model Context Protocol)?

MCP is a **standard protocol** for how AI models interact with tools. Think of it as "USB for AI tools" — a universal interface that works across frameworks and models.

```
                    MCP Standard Interface
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Lambda Func   │  │ REST API      │  │ Database      │
│ get_weather() │  │ /api/orders   │  │ query_users() │
└───────────────┘  └───────────────┘  └───────────────┘
```

**Why MCP matters:**
- Tools written once work with any MCP-compatible agent
- Agents don't need tool-specific integration code
- Standardized discovery (`listTools`) and invocation (`invokeTool`)

### How Tool Calling Works

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│  Agent  │────▶│   LLM   │────▶│ Gateway │
│ Request │     │ Runtime │     │ (Tool   │     │ (Tools) │
│         │     │         │     │ Select) │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                    │               │               │
                    │    "I need    │   "Call       │
                    │    weather    │   get_weather │
                    │    data"      │   with zip    │
                    │               │   90210"      │
                    │               │               │
                    ▼               ▼               ▼
              Agent receives   LLM decides    Gateway routes
              user input       which tool     to actual tool
                               to use         implementation
```

### Agent Patterns in AgentCore

**Pattern 1: Single Agent**
```
User ──▶ Agent ──▶ Tools
```
One agent handles everything. Simple, good for focused use cases.

**Pattern 2: Agent-to-Agent (A2A)**
```
User ──▶ Orchestrator Agent ──▶ Specialist Agent A
                            ──▶ Specialist Agent B
```
Orchestrator delegates to specialists. Good for complex domains.

**Pattern 3: Agents as Tools**
```
User ──▶ Agent A ──▶ Gateway ──▶ Agent B (exposed as tool)
```
One agent calls another through Gateway. Maximum composability.

---

## 1.4 SDK & CLI Overview

### The Two Key Packages

```bash
pip install bedrock-agentcore              # Core SDK
pip install bedrock-agentcore-starter-toolkit  # CLI tools
```

### SDK: `bedrock-agentcore`

The SDK provides the `BedrockAgentCoreApp` class:

```python
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    # Your agent logic here
    return {"result": "Hello!"}

if __name__ == "__main__":
    app.run()  # Starts local server on port 8080
```

### CLI: `agentcore` Command

| Command | Purpose |
|---------|---------|
| `agentcore configure -e my_agent.py` | Set up deployment config |
| `agentcore launch` | Deploy to AWS |
| `agentcore invoke '{"prompt": "hi"}'` | Test deployed agent |
| `agentcore logs` | View agent logs |
| `agentcore destroy` | Tear down deployment |

### Integration with Any Framework

```python
# With Strands Agents
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    result = agent(payload["prompt"])
    return {"result": result.message}
```

```python
# With LangGraph
from bedrock_agentcore import BedrockAgentCoreApp
from my_langgraph_agent import graph

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    result = graph.invoke({"input": payload["prompt"]})
    return {"result": result["output"]}
```

The `@app.entrypoint` decorator is the **only AgentCore-specific code** in your agent.

---

## Module 1 Summary

### Key Points

1. **The Problem**: Moving agents from prototype to production requires solving hosting, security, memory, monitoring, and evaluation

2. **AgentCore's Solution**: Seven managed services that separate your agent logic from infrastructure concerns

3. **MCP Protocol**: Universal standard for tool interaction — write tools once, use everywhere

4. **Minimal Code Changes**: The `@app.entrypoint` decorator is the primary integration point

5. **Framework Agnostic**: Works with Strands, LangGraph, CrewAI, LlamaIndex, or custom code

### Architecture Mental Model

```
Your Code (Framework-specific)
        │
        ▼
   @app.entrypoint  ◄── This is the integration point
        │
        ▼
AgentCore Services (Managed by AWS)
```

---

## Comprehension Check

1. **In your own words**, what problem does AgentCore solve?

2. **Which AgentCore service** would you use if you wanted to:
   - a) Give your agent access to a company's REST API?
   - b) Let your agent remember a user's preferences across sessions?
   - c) Debug why your agent chose a specific tool?

3. **What is MCP** and why does AgentCore use it?
