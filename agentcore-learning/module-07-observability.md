# Module 7: AgentCore Observability

## 7.1 Why Agent Observability is Different

### The Challenge: Agents are Non-Deterministic

Traditional applications:
```
Input → Code → Output (predictable)
```

Agent applications:
```
Input → LLM → Tool Choice → Tool Execution → LLM → Maybe More Tools → Output
         ↑                                         ↑
         │         (unpredictable path)            │
         └─────────────────────────────────────────┘
```

### What Can Go Wrong

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT FAILURE MODES                               │
│                                                                      │
│   1. Wrong Tool Selection                                           │
│      "Why did the agent use search instead of database lookup?"     │
│                                                                      │
│   2. Infinite Loops                                                 │
│      "Agent keeps calling the same tool over and over"              │
│                                                                      │
│   3. Hallucinated Tool Calls                                        │
│      "Agent called a tool with made-up parameters"                  │
│                                                                      │
│   4. Silent Failures                                                │
│      "Agent returned wrong answer but no error was thrown"          │
│                                                                      │
│   5. Cost Overruns                                                  │
│      "Why did this request use 50,000 tokens?"                      │
└─────────────────────────────────────────────────────────────────────┘
```

### What You Need to See

| Question | Observability Answers |
|----------|----------------------|
| What tools did the agent use? | Tool call traces |
| Why did it choose that tool? | LLM decision context |
| How long did each step take? | Latency spans |
| How many tokens were used? | Token metrics |
| What errors occurred? | Error traces with context |
| What was the full conversation? | Message history |

---

## 7.2 OpenTelemetry Foundation

### What is OpenTelemetry?

OpenTelemetry (OTel) is the **standard protocol** for observability data. Think of it as "USB for metrics and traces."

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPENTELEMETRY CONCEPTS                            │
│                                                                      │
│   TRACE: End-to-end request journey                                 │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ Trace ID: abc-123                                            │  │
│   │                                                              │  │
│   │   SPAN: Agent Invocation (parent)                           │  │
│   │   ├── SPAN: LLM Call #1                                     │  │
│   │   │   └── tokens: 150, latency: 800ms                       │  │
│   │   ├── SPAN: Tool Call (get_weather)                         │  │
│   │   │   └── params: {city: "Seattle"}, latency: 200ms         │  │
│   │   └── SPAN: LLM Call #2                                     │  │
│   │       └── tokens: 100, latency: 600ms                       │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                      │
│   Key Terms:                                                        │
│   • Trace = Full request journey                                    │
│   • Span = Single operation within trace                            │
│   • Attributes = Metadata on spans                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Why AgentCore Uses OpenTelemetry

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   Your Agent ──▶ OpenTelemetry Format ──▶ ANY Backend               │
│                                               │                      │
│                         ┌─────────────────────┼─────────────────┐   │
│                         ▼                     ▼                 ▼   │
│                   CloudWatch            Langfuse            Arize   │
│                   (AWS native)          (LLM-focused)    (ML-focused)│
│                                                                      │
│   Benefits:                                                          │
│   • No vendor lock-in                                               │
│   • Standard format, any backend                                    │
│   • Rich ecosystem of tools                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7.3 Automatic Instrumentation (Runtime-Hosted)

### Zero-Config Observability

When your agent runs on AgentCore Runtime, observability is **automatic**:

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent(tools=[...])

@app.entrypoint
def invoke(payload):
    result = agent(payload["prompt"])
    return {"response": result.message}

# That's it! Traces automatically captured:
# • Agent invocation span
# • Each LLM call span
# • Each tool call span
# • Token counts, latencies, errors
```

### What Gets Captured Automatically

```
Automatic Spans Created:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  Agent Invocation                                                   │
│  ├── input: "What's the weather in Seattle?"                       │
│  ├── output: "The weather in Seattle is 65°F and cloudy"           │
│  ├── duration: 2.3s                                                │
│  │                                                                  │
│  ├── LLM Call #1 (claude-3-sonnet)                                 │
│  │   ├── input_tokens: 150                                         │
│  │   ├── output_tokens: 45                                         │
│  │   ├── duration: 800ms                                           │
│  │   └── tool_choice: "get_weather"                                │
│  │                                                                  │
│  ├── Tool Call (get_weather)                                       │
│  │   ├── params: {"city": "Seattle"}                               │
│  │   ├── result: {"temp": 65, "condition": "cloudy"}               │
│  │   └── duration: 150ms                                           │
│  │                                                                  │
│  └── LLM Call #2 (claude-3-sonnet)                                 │
│      ├── input_tokens: 200                                         │
│      ├── output_tokens: 30                                         │
│      └── duration: 600ms                                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7.4 Manual Instrumentation (Non-Runtime)

### When Your Agent Runs Elsewhere

For agents not on AgentCore Runtime (Lambda, ECS, EC2, local), you add instrumentation manually:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure exporter (to CloudWatch or other backend)
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(
    endpoint="https://xray.us-east-1.amazonaws.com"
))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("my-agent")

# Instrument your agent
def run_agent(prompt):
    with tracer.start_as_current_span("agent_invocation") as span:
        span.set_attribute("input", prompt)

        # LLM call
        with tracer.start_as_current_span("llm_call") as llm_span:
            response = call_llm(prompt)
            llm_span.set_attribute("model", "claude-3-sonnet")
            llm_span.set_attribute("tokens", response.usage.total_tokens)

        # Tool call (if needed)
        if response.tool_calls:
            with tracer.start_as_current_span("tool_call") as tool_span:
                tool_span.set_attribute("tool_name", response.tool_calls[0].name)
                result = execute_tool(response.tool_calls[0])
                tool_span.set_attribute("result", str(result))

        span.set_attribute("output", final_response)
        return final_response
```

### Framework-Specific Instrumentation

**Strands (Non-Runtime):**
```python
from strands import Agent
from strands.telemetry import StrandsInstrumentor

# Enable instrumentation
StrandsInstrumentor().instrument()

agent = Agent(tools=[...])
result = agent("What's the weather?")
# Traces automatically captured
```

**LangGraph:**
```python
from langchain_community.callbacks import OpenTelemetryCallbackHandler

otel_handler = OpenTelemetryCallbackHandler(tracer)
graph = workflow.compile()
result = graph.invoke(input, config={"callbacks": [otel_handler]})
```

**CrewAI:**
```python
from crewai.telemetry import CrewAIInstrumentor

CrewAIInstrumentor().instrument()
crew = Crew(agents=[...], tasks=[...])
result = crew.kickoff()
```

---

## 7.5 CloudWatch GenAI Observability Dashboard

### Enabling Transaction Search

First, enable the CloudWatch feature:

```bash
# Using CloudFormation template from repository
aws cloudformation deploy \
    --template-file enable-transaction-search.yaml \
    --stack-name agentcore-observability
```

### Dashboard Views

```
┌─────────────────────────────────────────────────────────────────────┐
│              CLOUDWATCH GENAI OBSERVABILITY                          │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ SUMMARY VIEW                                                    │ │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │ │
│  │ │Invocations│ │ Errors  │ │ Latency  │ │  Tokens  │           │ │
│  │ │   1,234   │ │   12    │ │  2.3s    │ │  45,000  │           │ │
│  │ │   today   │ │  0.97%  │ │   p50    │ │  today   │           │ │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ TRACE VIEW                                                      │ │
│  │                                                                 │ │
│  │ Trace: abc-123-def                                             │ │
│  │ ├── Agent Invocation ──────────────────────────────── 2.3s    │ │
│  │ │   ├── LLM Call ────────────────────── 800ms                 │ │
│  │ │   ├── Tool: get_weather ───── 150ms                         │ │
│  │ │   └── LLM Call ────────────── 600ms                         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ TOOL USAGE                                                      │ │
│  │                                                                 │ │
│  │ get_weather    ████████████████████  45%                       │ │
│  │ search_docs    ████████████          28%                       │ │
│  │ calculator     ████████              18%                       │ │
│  │ send_email     ████                   9%                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Querying Traces

```python
import boto3

logs = boto3.client('logs')

# Find traces with errors
response = logs.start_query(
    logGroupName='/aws/agentcore/my-agent',
    queryString='''
        fields @timestamp, trace_id, error_message
        | filter error = true
        | sort @timestamp desc
        | limit 20
    '''
)

# Find slow invocations
response = logs.start_query(
    logGroupName='/aws/agentcore/my-agent',
    queryString='''
        fields @timestamp, trace_id, duration_ms
        | filter duration_ms > 5000
        | sort duration_ms desc
        | limit 20
    '''
)
```

---

## 7.6 Custom Span Creation

### Adding Business Context

Sometimes automatic spans aren't enough. Add custom spans for business-specific tracking:

```python
from opentelemetry import trace

tracer = trace.get_tracer("my-agent")

@app.entrypoint
def invoke(payload):
    with tracer.start_as_current_span("agent_invocation") as root_span:
        # Add business context
        root_span.set_attribute("user_id", payload.get("user_id"))
        root_span.set_attribute("request_type", payload.get("type"))

        # Track specific business logic
        with tracer.start_as_current_span("validate_user_permissions") as span:
            permissions = check_permissions(payload["user_id"])
            span.set_attribute("permissions", permissions)

        # Track custom processing
        with tracer.start_as_current_span("process_financial_data") as span:
            span.set_attribute("data_source", "internal_db")
            data = fetch_financial_data()
            span.set_attribute("records_processed", len(data))

        result = agent(payload["prompt"])

        # Track response quality
        with tracer.start_as_current_span("response_validation") as span:
            is_valid = validate_response(result)
            span.set_attribute("response_valid", is_valid)

        return {"response": result.message}
```

### What Custom Spans Enable

```
Before (automatic only):
├── Agent Invocation
│   ├── LLM Call
│   ├── Tool Call
│   └── LLM Call

After (with custom spans):
├── Agent Invocation
│   ├── validate_user_permissions    ← Business context
│   │   └── permissions: ["read", "write"]
│   ├── process_financial_data       ← Domain tracking
│   │   └── records_processed: 150
│   ├── LLM Call
│   ├── Tool Call
│   ├── LLM Call
│   └── response_validation          ← Quality tracking
│       └── response_valid: true
```

---

## 7.7 Partner Integrations

### Langfuse

```python
from langfuse import Langfuse
from langfuse.openai import openai  # Instrumented OpenAI client

langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-...",
    host="https://cloud.langfuse.com"
)

# Traces automatically sent to Langfuse
# Provides: prompt management, A/B testing, user feedback tracking
```

### Arize

```python
from arize.otel import register_otel

register_otel(
    space_id="your-space-id",
    api_key="your-api-key",
    model_id="my-agent"
)

# Provides: drift detection, performance monitoring, model comparison
```

### Braintrust

```python
from braintrust import init_logger

logger = init_logger(project="my-agent")

# Provides: evaluation framework, experiment tracking, prompt versioning
```

### Choosing a Partner

| Partner | Best For |
|---------|----------|
| **CloudWatch** | AWS-native, cost tracking, alerts |
| **Langfuse** | Prompt management, user feedback |
| **Arize** | ML monitoring, drift detection |
| **Braintrust** | Evaluations, experiments |
| **Instana** | Enterprise APM, full-stack tracing |

---

## 7.8 End-to-End Tracing Across Services

### Multi-Service Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    END-TO-END TRACE                                  │
│                                                                      │
│   Frontend → API Gateway → Orchestrator → Specialist → Database     │
│      │           │             │              │            │        │
│      ▼           ▼             ▼              ▼            ▼        │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  Trace ID: abc-123                                           │  │
│   │                                                              │  │
│   │  ├── Frontend Request ────────────────────────────── 50ms   │  │
│   │  ├── API Gateway ─────────────────────────────────── 10ms   │  │
│   │  ├── Orchestrator Agent ─────────────────────────── 2.5s    │  │
│   │  │   ├── LLM Call ────────────────────────── 800ms          │  │
│   │  │   └── Call Specialist ────────────────── 1.5s            │  │
│   │  │       ├── Specialist Agent ────────────── 1.4s           │  │
│   │  │       │   ├── LLM Call ────────── 600ms                  │  │
│   │  │       │   └── DB Query ────────── 200ms                  │  │
│   │  │       └── Response ────────────── 100ms                  │  │
│   │  └── Final Response ──────────────────────────────── 50ms   │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                      │
│   Same trace ID propagated through ALL services                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Context Propagation

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

# Orchestrator: Pass trace context to specialist
def call_specialist(request):
    headers = {}
    inject(headers)  # Injects trace context into headers

    response = specialist_client.invoke(
        payload=request,
        headers=headers  # Trace context passed along
    )
    return response

# Specialist: Extract trace context
@app.entrypoint
def invoke(payload, headers):
    context = extract(headers)  # Extracts parent trace context

    with tracer.start_as_current_span("specialist_work", context=context):
        # This span is now child of orchestrator's span
        result = do_work()
        return result
```

---

## Module 7 Summary

### Key Points

1. **Agent observability is different** — Non-deterministic paths require detailed tracing
2. **OpenTelemetry** — Standard protocol, works with any backend
3. **Automatic instrumentation** — Runtime-hosted agents get observability free
4. **Manual instrumentation** — Add OTel for non-runtime agents
5. **CloudWatch GenAI Dashboard** — AWS-native visualization and querying
6. **Custom spans** — Add business context to traces
7. **Partner integrations** — Langfuse, Arize, Braintrust for specialized needs
8. **End-to-end tracing** — Context propagation across services

### Observability Decision Tree

```
Where is your agent hosted?
│
├─► AgentCore Runtime
│   └─► Automatic instrumentation (done!)
│
└─► Elsewhere (Lambda, ECS, EC2)
    │
    ├─► Add OpenTelemetry SDK
    ├─► Configure exporter (CloudWatch or partner)
    └─► Instrument your code (or use framework instrumentors)
```

---

## Comprehension Check

1. Why is agent observability more complex than traditional application observability?

2. What is the relationship between traces and spans in OpenTelemetry?

3. What's the difference between automatic and manual instrumentation?

4. When would you use a partner integration like Langfuse instead of CloudWatch?

