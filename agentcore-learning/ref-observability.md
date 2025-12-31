# AgentCore Observability - Reference

## Overview

AgentCore Observability helps developers trace, debug, and monitor agent performance in production through unified operational dashboards. Built on OpenTelemetry for compatibility with existing observability stacks.

## Key Features

- **OpenTelemetry Compatible**: Standard telemetry format
- **CloudWatch Integration**: Native AWS observability
- **Detailed Visualizations**: Step-by-step agent workflow views
- **Partner Integrations**: Langfuse, Arize, Braintrust, Instana

## Observability Patterns

### 1. Runtime-Hosted Agents
Agents deployed on AgentCore Runtime with automatic instrumentation:
- Strands Agents
- CrewAI
- Automatic span creation

### 2. Non-Runtime Agents
Agents hosted elsewhere with manual instrumentation:
- CrewAI
- LangGraph
- LlamaIndex
- Strands

### 3. Advanced Patterns
- Custom span creation for detailed tracing
- Specific operation monitoring within workflows

### 4. Partner Observability
Integration with third-party platforms:

| Partner | Description |
|---------|-------------|
| Arize | AI and Agent engineering platform |
| Braintrust | AI evaluation and monitoring |
| Instana | Real-time APM and Observability |
| Langfuse | LLM observability and analytics |

## Tutorial Structure (from repository)

```
06-AgentCore-observability/
├── 00-enable-transaction-search-template/
├── 01-Agentcore-runtime-hosted/
│   ├── CrewAI/
│   └── Strands Agents/
├── 02-Agent-not-hosted-on-runtime/
│   ├── CrewAI/
│   ├── Langgraph/
│   ├── LlamaIndex/
│   └── Strands/
├── 03-advanced-concepts/
│   └── 01-custom-span-creation/
├── 04-Agentcore-runtime-partner-observability/
│   ├── Arize/
│   ├── Braintrust/
│   ├── Instana/
│   └── Langfuse/
└── 05-Lambda-AgentCore-invocation/
```

## Implementation Steps

1. Enable Transaction Search in CloudWatch
2. Configure OpenTelemetry instrumentation
3. Set up environment variables for observability
4. View traces in CloudWatch GenAI Observability dashboard

## What You Can Monitor

- **Agent Invocations**: Full request/response lifecycle
- **Tool Calls**: Which tools used, latency, success/failure
- **LLM Calls**: Token usage, latency, model selection
- **Memory Operations**: Read/write patterns
- **Error Tracking**: Exceptions and failures with context

## CloudWatch GenAI Dashboard

Provides unified view of:
- Agent performance metrics
- Tool usage statistics
- Error rates and patterns
- Latency distributions
- Cost attribution
