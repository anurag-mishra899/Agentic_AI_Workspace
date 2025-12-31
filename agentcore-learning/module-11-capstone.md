# Module 11: Capstone - Building a Production Agent End-to-End

## 11.1 Course Summary: The Complete Picture

### What You've Learned

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENTCORE KNOWLEDGE MAP                           │
│                                                                      │
│   Module 1: Foundation                                              │
│   └── Problem space, 7 services, MCP protocol                       │
│                                                                      │
│   Module 2: Runtime                                                 │
│   └── @app.entrypoint, deployment, A2A, streaming                   │
│                                                                      │
│   Module 3: Gateway                                                 │
│   └── Targets, MCP conversion, semantic search, auth                │
│                                                                      │
│   Module 4: Identity                                                │
│   └── Inbound/outbound auth, OAuth flows, delegation                │
│                                                                      │
│   Module 5: Memory                                                  │
│   └── Short/long-term, strategies, branching, security              │
│                                                                      │
│   Module 6: Tools                                                   │
│   └── Code Interpreter, Browser Tool, S3, sessions                  │
│                                                                      │
│   Module 7: Observability                                           │
│   └── OpenTelemetry, traces, CloudWatch, partners                   │
│                                                                      │
│   Module 8: Evaluations & Policy                                    │
│   └── Metrics, custom evaluators, Cedar, NL2Cedar                   │
│                                                                      │
│   Module 9: Framework Integrations                                  │
│   └── Strands, LangGraph, CrewAI, LlamaIndex, etc.                  │
│                                                                      │
│   Module 10: Production Deployment                                  │
│   └── IaC, multi-agent, VPC, cost optimization, CI/CD               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The 7 Services Recap

| Service | Purpose | Key Concept |
|---------|---------|-------------|
| **Runtime** | Host your agent | `@app.entrypoint` |
| **Gateway** | Manage tools | MCP protocol |
| **Identity** | Authentication | OAuth 2/3-legged |
| **Memory** | Persistence | Short/long-term |
| **Tools** | Capabilities | Code Interpreter, Browser |
| **Observability** | Monitoring | OpenTelemetry |
| **Evaluations** | Quality | Built-in + custom metrics |

---

## 11.2 Capstone Project: Customer Support Agent

### Project Overview

Build a **complete customer support system** from prototype to production:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CUSTOMER SUPPORT AGENT                            │
│                                                                      │
│   User: "I want to return the headphones I bought last week"        │
│                                                                      │
│   Agent:                                                            │
│   1. Recognizes returning customer (Memory)                         │
│   2. Looks up return policy (Gateway → Lambda)                      │
│   3. Finds order history (Gateway → Database)                       │
│   4. Processes return request                                       │
│   5. Responds with personalized help                                │
│                                                                      │
│   All while:                                                        │
│   ✓ Authenticated via Cognito (Identity)                           │
│   ✓ Traced in CloudWatch (Observability)                           │
│   ✓ Scored for quality (Evaluations)                               │
│   ✓ Protected by policies (Policy)                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 11.3 Lab Progression

### Lab 1: Create Agent Prototype (~20 mins)

**Goal:** Build a working prototype locally

```python
from strands import Agent, tool

@tool
def get_return_policy(product_type: str) -> str:
    """Get return policy for a product type."""
    policies = {
        "electronics": "30-day return with receipt",
        "clothing": "60-day return, unworn with tags",
        "default": "14-day return policy"
    }
    return policies.get(product_type, policies["default"])

@tool
def search_products(query: str) -> str:
    """Search product catalog."""
    # Simulated search
    return f"Found 3 products matching '{query}'"

@tool
def web_search(query: str) -> str:
    """Search web for troubleshooting."""
    return f"Troubleshooting results for: {query}"

agent = Agent(
    model="anthropic.claude-3-sonnet",
    tools=[get_return_policy, search_products, web_search],
    system_prompt="""You are a helpful customer support agent.
    Help customers with returns, product questions, and troubleshooting."""
)

# Test locally
result = agent("What's the return policy for headphones?")
print(result.message)
```

**What you learn:** Basic agent creation, tool definition, local testing

---

### Lab 2: Add Memory (~20 mins)

**Goal:** Agent remembers customers across sessions

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient()

# Create memory store with strategies
memory.create_memory_store(
    name="customer-support-memory",
    memoryStrategies=[
        {"strategyType": "SEMANTIC", "configuration": {"embeddingModel": "amazon.titan-embed-text-v2"}},
        {"strategyType": "USER_PREFERENCE", "configuration": {}},
        {"strategyType": "SUMMARY", "configuration": {"summaryModel": "anthropic.claude-3-haiku"}}
    ]
)

# Integration with agent
@tool
def remember_customer(customer_id: str, fact: str) -> str:
    """Store important customer information."""
    memory.save_memory(
        memoryStoreId="customer-support-memory",
        actorId=customer_id,
        content=fact
    )
    return f"Noted: {fact}"

@tool
def recall_customer(customer_id: str, query: str) -> str:
    """Recall information about customer."""
    results = memory.search_memories(
        memoryStoreId="customer-support-memory",
        actorId=customer_id,
        query=query
    )
    return "\n".join([r["content"] for r in results])

agent = Agent(
    tools=[get_return_policy, search_products, remember_customer, recall_customer],
    system_prompt="""You are a helpful customer support agent.
    Remember customer preferences and past interactions."""
)
```

**What you learn:** Memory store creation, strategies, memory tools

---

### Lab 3: Gateway & Identity (~30 mins)

**Goal:** Shared tools with authentication

```python
import boto3

client = boto3.client('bedrock-agentcore')

# Create Gateway
gateway = client.create_gateway(
    name="customer-support-gateway",
    description="Tools for customer support agents"
)

# Add Lambda tool
client.create_target(
    gatewayId=gateway["gatewayId"],
    name="order-lookup",
    description="Look up customer orders",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456:function:order-lookup"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "order_id": {"type": "string"}
        }
    }
)

# Configure authentication
client.configure_inbound_auth(
    gatewayId=gateway["gatewayId"],
    authConfiguration={
        "cognitoConfiguration": {
            "userPoolId": "us-east-1_xxxxx",
            "clientId": "your-client-id"
        }
    }
)

# Agent uses Gateway tools
from bedrock_agentcore.gateway import GatewayClient

gateway_client = GatewayClient(gateway_id=gateway["gatewayId"])
gateway_tools = gateway_client.list_tools()

agent = Agent(tools=gateway_tools)
```

**What you learn:** Gateway creation, Lambda targets, Cognito authentication

---

### Lab 4: Deploy to Runtime (~30 mins)

**Goal:** Production deployment with observability

```python
# customer_support_agent.py
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.gateway import GatewayClient
from bedrock_agentcore.memory import MemoryClient
from strands import Agent

app = BedrockAgentCoreApp()

# Initialize services
gateway = GatewayClient(gateway_id="customer-support-gateway")
memory = MemoryClient()

# Create agent with Gateway tools
agent = Agent(
    tools=gateway.list_tools(),
    system_prompt="You are a helpful customer support agent."
)

@app.entrypoint
def invoke(payload):
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    prompt = payload.get("prompt")

    # Retrieve customer context
    context = memory.search_memories(
        memoryStoreId="customer-support-memory",
        actorId=user_id,
        query=prompt,
        maxResults=3
    )

    # Enhance prompt with context
    enhanced_prompt = f"Customer context: {context}\n\nCustomer: {prompt}"

    # Run agent
    result = agent(enhanced_prompt)

    # Save interaction
    memory.save_event(
        memoryStoreId="customer-support-memory",
        sessionId=session_id,
        actorId=user_id,
        event={"role": "assistant", "content": result.message}
    )

    return {"response": result.message}

if __name__ == "__main__":
    app.run()
```

**Deploy:**
```bash
agentcore configure -e customer_support_agent.py
agentcore launch
```

**What you learn:** `@app.entrypoint`, deployment, automatic observability

---

### Lab 5: Evaluations (~10 mins)

**Goal:** Continuous quality monitoring

```python
from bedrock_agentcore.evaluations import EvaluationsClient

evals = EvaluationsClient()

# Set up online evaluations
evals.create_online_evaluation(
    name="customer-support-quality",
    agentId="your-agent-id",
    samplingConfiguration={
        "sampleRate": 0.1,  # 10% of requests
        "minSamplesPerHour": 20
    },
    evaluators=[
        "correctness",
        "helpfulness",
        "safety",
        "task_completion"
    ],
    alertConfiguration={
        "threshold": 0.75,
        "metric": "helpfulness",
        "snsTopicArn": "arn:aws:sns:..."
    }
)
```

**What you learn:** Online evaluations, quality thresholds, alerting

---

### Lab 6: Frontend (~20 mins)

**Goal:** Customer-facing chat interface

```python
# streamlit_app.py
import streamlit as st
import boto3

st.title("Customer Support")

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can we help?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call agent
    client = boto3.client('bedrock-agentcore-runtime')
    response = client.invoke_agent(
        agentId='your-agent-id',
        payload={
            "user_id": st.session_state.get("user_id", "anonymous"),
            "session_id": st.session_state.get("session_id"),
            "prompt": prompt
        }
    )

    # Display response
    assistant_message = response["response"]
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    with st.chat_message("assistant"):
        st.markdown(assistant_message)
```

**Run:**
```bash
streamlit run streamlit_app.py
```

**What you learn:** Frontend integration, streaming, session management

---

## 11.4 Architecture Evolution

```
Lab 1: Prototype
┌─────────────┐
│   Agent     │──── Local tools
└─────────────┘

Lab 2: + Memory
┌─────────────┐      ┌─────────────┐
│   Agent     │─────►│   Memory    │
└─────────────┘      └─────────────┘

Lab 3: + Gateway & Identity
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Agent     │─────►│   Gateway   │─────►│   Lambda    │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                     ┌──────▼──────┐
                     │  Identity   │
                     │  (Cognito)  │
                     └─────────────┘

Lab 4: + Runtime & Observability
┌─────────────────────────────────────────────────────────────────────┐
│                         AgentCore Runtime                            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐         │
│  │   Agent     │─────►│   Gateway   │─────►│   Lambda    │         │
│  └──────┬──────┘      └─────────────┘      └─────────────┘         │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────┐      ┌─────────────┐                              │
│  │   Memory    │      │Observability│                              │
│  └─────────────┘      │(CloudWatch) │                              │
│                       └─────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘

Lab 5-6: + Evaluations & Frontend
┌─────────────────────────────────────────────────────────────────────┐
│   ┌──────────────┐                                                  │
│   │   Frontend   │                                                  │
│   │  (Streamlit) │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│          ▼                                                          │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │                    AgentCore Runtime                         │  │
│   │                                                              │  │
│   │   Agent ──► Gateway ──► Lambda                              │  │
│   │     │                                                        │  │
│   │     ├──► Memory                                             │  │
│   │     ├──► Observability                                      │  │
│   │     └──► Evaluations                                        │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 11.5 Other Use Cases to Explore

### Available in Repository

| Use Case | Description | Key Features |
|----------|-------------|--------------|
| **A2A Incident Response** | Multi-agent system | Agent-to-agent communication |
| **AWS Operations Agent** | Cloud management | Okta auth, monitoring |
| **DB Performance Analyzer** | Database analysis | PostgreSQL, Code Interpreter |
| **Device Management** | IoT agent | Cognito, real-time |
| **Enterprise Web Intelligence** | Research agent | Browser Tool |
| **Farm Management Advisor** | Agricultural | Weather, plant detection |
| **Finance Personal Assistant** | Budget management | Multi-agent, guardrails |
| **Healthcare Appointment** | FHIR scheduling | Patient data |
| **Market Trends Agent** | Financial analysis | Browser, memory |
| **SRE Agent** | Site reliability | LangGraph multi-agent |
| **Text to Python IDE** | Code generation | Code Interpreter |

### Blueprints (Full-Stack Apps)

| Blueprint | Description |
|-----------|-------------|
| **Shopping Concierge** | E-commerce assistant |
| **Travel Concierge** | Travel planning |

---

## 11.6 Next Steps

### Immediate Actions

1. **Complete the E2E Lab Series**
   ```
   01-tutorials/09-AgentCore-E2E/
   ├── lab-01-create-an-agent.ipynb
   ├── lab-02-agentcore-memory.ipynb
   ├── lab-03-agentcore-gateway.ipynb
   ├── lab-04-agentcore-runtime.ipynb
   ├── lab-05-agentcore-evals.ipynb
   └── lab-06-frontend.ipynb
   ```

2. **Explore Use Cases** relevant to your domain

3. **Deploy an IaC template** to understand production patterns

### Learning Path by Role

| Role | Focus Areas | Recommended Use Cases |
|------|-------------|----------------------|
| **Developer** | Runtime, Tools, Integrations | Text-to-Python IDE, Customer Support |
| **Architect** | Gateway, Identity, Multi-agent | A2A Incident Response, SRE Agent |
| **ML Engineer** | Evaluations, Observability | Any + evaluation deep dive |
| **Security** | Identity, Policy, VPC | Healthcare, Finance |
| **DevOps** | IaC, CI/CD, Monitoring | Any + infrastructure templates |

---

## Module 11 Summary

### You Are Now Ready To:

1. **Build agents** with any framework using `@app.entrypoint`
2. **Share tools** via Gateway with authentication
3. **Persist state** with short-term and long-term memory
4. **Execute code** safely with Code Interpreter
5. **Automate web tasks** with Browser Tool
6. **Monitor agents** with OpenTelemetry and CloudWatch
7. **Measure quality** with evaluations and custom metrics
8. **Enforce policies** with Cedar and NL2Cedar
9. **Deploy to production** with IaC and CI/CD
10. **Scale** with multi-agent architectures

### Final Architecture Mental Model

```
YOUR AGENT CODE (Any Framework)
        │
        ▼
   @app.entrypoint ─────────────────────────────────────────────┐
        │                                                        │
        ▼                                                        │
┌─────────────────────────────────────────────────────────────┐ │
│                    AGENTCORE SERVICES                        │ │
│                                                              │ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │ │
│  │ Runtime  │  │ Gateway  │  │ Identity │  │  Memory  │   │ │
│  │ (Host)   │  │ (Tools)  │  │  (Auth)  │  │ (State)  │   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │ │
│                                                              │ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │ │
│  │  Tools   │  │ Observe  │  │  Evals   │  │  Policy  │   │ │
│  │(Browser/ │  │ (Trace)  │  │ (Score)  │  │ (Guard)  │   │ │
│  │  Code)   │  │          │  │          │  │          │   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │ │
│                                                              │ │
└─────────────────────────────────────────────────────────────┘ │
        │                                                        │
        └────────────────────────────────────────────────────────┘
                         AWS Managed Infrastructure
```

---

## Course Complete!

You've completed all 11 modules of the Amazon Bedrock AgentCore learning curriculum.

**Repository for hands-on practice:**
https://github.com/awslabs/amazon-bedrock-agentcore-samples

**Start building:**
```bash
git clone https://github.com/awslabs/amazon-bedrock-agentcore-samples.git
cd amazon-bedrock-agentcore-samples/01-tutorials/09-AgentCore-E2E
pip install -r requirements.txt
jupyter notebook lab-01-create-an-agent.ipynb
```

