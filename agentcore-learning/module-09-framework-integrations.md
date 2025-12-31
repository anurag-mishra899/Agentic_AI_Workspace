# Module 9: Framework Integrations

## 9.1 AgentCore is Framework-Agnostic

### The Key Insight

AgentCore doesn't force you to use a specific agent framework. Your agent code is yours — AgentCore provides the infrastructure around it.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     YOUR CHOICE OF FRAMEWORK                         │
│                                                                      │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│   │ Strands │ │LangGraph│ │ CrewAI  │ │LlamaIdx │ │ OpenAI  │      │
│   │ Agents  │ │         │ │         │ │         │ │ Agents  │      │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘      │
│        │           │           │           │           │            │
│        └───────────┴───────────┴───────────┴───────────┘            │
│                                │                                     │
│                    ════════════╪════════════                        │
│                         @app.entrypoint                             │
│                    ════════════╪════════════                        │
│                                │                                     │
│              AGENTCORE INFRASTRUCTURE                               │
│              (Runtime, Gateway, Identity, Memory, etc.)             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The Integration Point

No matter which framework you choose, the integration is the same:

```python
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    # YOUR FRAMEWORK CODE HERE
    result = your_agent(payload["prompt"])
    return {"response": result}

if __name__ == "__main__":
    app.run()
```

---

## 9.2 Strands Agents (AWS Native)

### Best Integration Experience

Strands is AWS's native agent framework, designed to work seamlessly with AgentCore.

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.tools import calculator, web_search

app = BedrockAgentCoreApp()

# Create agent with tools
agent = Agent(
    model="anthropic.claude-3-sonnet",
    tools=[calculator, web_search],
    system_prompt="You are a helpful assistant."
)

@app.entrypoint
def invoke(payload):
    result = agent(payload["prompt"])
    return {
        "response": result.message,
        "tool_calls": [t.name for t in result.tool_calls]
    }
```

### Strands Features with AgentCore

| Feature | Description |
|---------|-------------|
| **Automatic Observability** | Traces captured without extra code |
| **Native Memory Integration** | MemoryHook for automatic persistence |
| **Gateway Tools** | Direct MCP tool consumption |
| **Streaming** | Built-in streaming support |

### Strands with Gateway Tools

```python
from strands import Agent
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(gateway_id="my-gateway")
gateway_tools = gateway.list_tools()

agent = Agent(
    tools=gateway_tools  # MCP tools from Gateway
)
```

### Strands with Memory

```python
from strands import Agent
from strands.hooks import MemoryHook
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient()
memory_hook = MemoryHook(
    memory_client=memory,
    memory_store_id="my-memory-store",
    auto_save=True,
    auto_retrieve=True
)

agent = Agent(hooks=[memory_hook])
```

---

## 9.3 LangChain / LangGraph Integration

### LangChain (Simple Chains)

```python
from bedrock_agentcore import BedrockAgentCoreApp
from langchain_aws import ChatBedrock
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool

app = BedrockAgentCoreApp()

# Create LLM
llm = ChatBedrock(model_id="anthropic.claude-3-sonnet")

# Define tools
@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: 72°F, Sunny"

# Create agent
agent = create_react_agent(llm, [get_weather], prompt)
executor = AgentExecutor(agent=agent, tools=[get_weather])

@app.entrypoint
def invoke(payload):
    result = executor.invoke({"input": payload["prompt"]})
    return {"response": result["output"]}
```

### LangGraph (Stateful Multi-Agent)

```python
from bedrock_agentcore import BedrockAgentCoreApp
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock

app = BedrockAgentCoreApp()

# Define state
class AgentState(TypedDict):
    messages: list
    next_step: str

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)
workflow.set_entry_point("researcher")

graph = workflow.compile()

@app.entrypoint
def invoke(payload):
    result = graph.invoke({
        "messages": [HumanMessage(content=payload["prompt"])]
    })
    return {"response": result["messages"][-1].content}
```

### LangGraph with Checkpointing

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Enable state persistence
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = workflow.compile(checkpointer=checkpointer)

@app.entrypoint
def invoke(payload):
    config = {"configurable": {"thread_id": payload.get("session_id", "default")}}
    result = graph.invoke(
        {"messages": [HumanMessage(content=payload["prompt"])]},
        config=config
    )
    return {"response": result["messages"][-1].content}
```

---

## 9.4 CrewAI Integration

### Multi-Agent Crews

```python
from bedrock_agentcore import BedrockAgentCoreApp
from crewai import Agent, Task, Crew, Process
from langchain_aws import ChatBedrock

app = BedrockAgentCoreApp()

llm = ChatBedrock(model_id="anthropic.claude-3-sonnet")

# Define agents
researcher = Agent(
    role="Researcher",
    goal="Research and gather information",
    backstory="Expert at finding and synthesizing information",
    llm=llm
)

writer = Agent(
    role="Writer",
    goal="Create compelling content",
    backstory="Skilled writer with attention to detail",
    llm=llm
)

# Define tasks
research_task = Task(
    description="Research {topic}",
    agent=researcher,
    expected_output="Comprehensive research notes"
)

writing_task = Task(
    description="Write article based on research",
    agent=writer,
    expected_output="Polished article"
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential
)

@app.entrypoint
def invoke(payload):
    result = crew.kickoff(inputs={"topic": payload["topic"]})
    return {"result": str(result)}
```

---

## 9.5 LlamaIndex Integration

### RAG-Focused Agents

```python
from bedrock_agentcore import BedrockAgentCoreApp
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.bedrock import Bedrock
from llama_index.core.agent import ReActAgent

app = BedrockAgentCoreApp()

# Load documents
documents = SimpleDirectoryReader("data/").load_data()
index = VectorStoreIndex.from_documents(documents)

# Create query engine
query_engine = index.as_query_engine()

# Create agent with RAG tool
llm = Bedrock(model="anthropic.claude-3-sonnet")
agent = ReActAgent.from_tools(
    [query_engine_tool],
    llm=llm,
    verbose=True
)

@app.entrypoint
def invoke(payload):
    response = agent.chat(payload["prompt"])
    return {"response": str(response)}
```

---

## 9.6 OpenAI Agents SDK Integration

### Using OpenAI's Agent Framework with Bedrock

```python
from bedrock_agentcore import BedrockAgentCoreApp
from openai import OpenAI
from agents import Agent, Runner

app = BedrockAgentCoreApp()

# Configure OpenAI client for Bedrock (via proxy or adapter)
client = OpenAI(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1",
    api_key="dummy"  # Uses IAM auth
)

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model="anthropic.claude-3-sonnet"
)

@app.entrypoint
def invoke(payload):
    result = Runner.run_sync(agent, payload["prompt"])
    return {"response": result.final_output}
```

---

## 9.7 PydanticAI Integration

### Type-Safe Agent Development

```python
from bedrock_agentcore import BedrockAgentCoreApp
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockModel
from pydantic import BaseModel

app = BedrockAgentCoreApp()

# Define typed output
class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str

# Create type-safe agent
model = BedrockModel("anthropic.claude-3-sonnet")
agent = Agent(model, result_type=WeatherResponse)

@agent.tool
def get_weather(city: str) -> dict:
    """Get weather for a city."""
    return {"city": city, "temperature": 72.0, "condition": "Sunny"}

@app.entrypoint
def invoke(payload):
    result = agent.run_sync(payload["prompt"])
    return result.data.model_dump()  # Type-safe response
```

---

## 9.8 AutoGen Integration

### Multi-Agent Conversations

```python
from bedrock_agentcore import BedrockAgentCoreApp
from autogen import AssistantAgent, UserProxyAgent

app = BedrockAgentCoreApp()

# Configure for Bedrock
config_list = [{
    "model": "anthropic.claude-3-sonnet",
    "api_type": "bedrock"
}]

assistant = AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list}
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "workspace"}
)

@app.entrypoint
def invoke(payload):
    user_proxy.initiate_chat(assistant, message=payload["prompt"])
    return {"response": assistant.last_message()["content"]}
```

---

## 9.9 Framework Selection Guide

### Decision Matrix

| Framework | Best For | Complexity | AgentCore Integration |
|-----------|----------|------------|----------------------|
| **Strands** | AWS-native, simple agents | Low | Native (best) |
| **LangChain** | Chain workflows, tool use | Medium | Good |
| **LangGraph** | Stateful multi-step flows | High | Good |
| **CrewAI** | Role-based multi-agent | Medium | Good |
| **LlamaIndex** | RAG-focused agents | Medium | Good |
| **PydanticAI** | Type-safe development | Low | Good |
| **AutoGen** | Multi-agent conversations | High | Good |
| **OpenAI SDK** | OpenAI API compatibility | Low | Good |

### Selection Flowchart

```
What's your primary need?
│
├─► Simple agent with tools
│   └─► Strands Agents (AWS native, best integration)
│
├─► RAG / Document Q&A
│   └─► LlamaIndex
│
├─► Complex multi-step workflows
│   └─► LangGraph
│
├─► Role-based multi-agent teams
│   └─► CrewAI
│
├─► Type-safe responses
│   └─► PydanticAI
│
├─► Multi-agent conversations
│   └─► AutoGen
│
└─► Migrating from OpenAI
    └─► OpenAI Agents SDK
```

---

## 9.10 Common Integration Patterns

### Pattern 1: Adding Observability

```python
# Any framework - add OpenTelemetry
from opentelemetry import trace

tracer = trace.get_tracer("my-agent")

@app.entrypoint
def invoke(payload):
    with tracer.start_as_current_span("agent_invocation"):
        result = your_framework_agent(payload["prompt"])
        return {"response": result}
```

### Pattern 2: Adding Memory

```python
# Any framework - retrieve and save context
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient()

@app.entrypoint
def invoke(payload):
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")

    # Retrieve relevant memories
    context = memory.search_memories(
        memoryStoreId="my-store",
        actorId=user_id,
        query=payload["prompt"]
    )

    # Add context to prompt
    enhanced_prompt = f"Context: {context}\n\nUser: {payload['prompt']}"

    # Run agent
    result = your_framework_agent(enhanced_prompt)

    # Save interaction
    memory.save_event(
        memoryStoreId="my-store",
        sessionId=session_id,
        actorId=user_id,
        event={"role": "assistant", "content": result}
    )

    return {"response": result}
```

### Pattern 3: Using Gateway Tools

```python
# Any framework - convert Gateway tools to framework-specific format
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(gateway_id="my-gateway")
mcp_tools = gateway.list_tools()

# Convert to your framework's tool format
framework_tools = convert_to_framework_format(mcp_tools)

agent = YourFrameworkAgent(tools=framework_tools)
```

---

## Module 9 Summary

### Key Points

1. **AgentCore is framework-agnostic** — Use any agent framework
2. **Single integration point** — `@app.entrypoint` decorator
3. **Strands has best integration** — AWS native, automatic observability
4. **All major frameworks supported** — LangGraph, CrewAI, LlamaIndex, etc.
5. **Common patterns apply** — Memory, observability, Gateway tools work with any framework
6. **Choose based on need** — RAG → LlamaIndex, Multi-agent → CrewAI, Simple → Strands

### Integration Pattern

```python
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# 1. Initialize YOUR framework's agent
agent = YourFrameworkAgent(...)

# 2. Wrap with entrypoint
@app.entrypoint
def invoke(payload):
    result = agent(payload["prompt"])
    return {"response": result}

# 3. Run
if __name__ == "__main__":
    app.run()
```

---

## Comprehension Check

1. What is the only AgentCore-specific code you need to add to use any framework?

2. Why is Strands Agents recommended for new AWS projects?

3. When would you choose LangGraph over Strands?

4. How can you add memory to an agent built with any framework?

