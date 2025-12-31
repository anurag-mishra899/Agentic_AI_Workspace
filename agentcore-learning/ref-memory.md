# AgentCore Memory - Reference

## Overview

Amazon Bedrock AgentCore Memory provides managed memory infrastructure enabling AI agents to maintain context over time, remember important facts, and deliver personalized experiences.

**Problem Solved**: LLMs lack persistent memory across conversations. AgentCore Memory addresses this limitation.

## Key Capabilities

| Capability | Description |
|------------|-------------|
| Core Infrastructure | Serverless setup with built-in encryption and observability |
| Event Storage | Raw event storage (conversation history/checkpointing) with branching |
| Strategy Management | Configurable extraction strategies |
| Memory Records | Automatic extraction of facts, preferences, summaries |
| Semantic Search | Vector-based retrieval using natural language queries |

## Memory Types

### Short-Term Memory
- Immediate conversation context
- Session-based information
- Continuity within single interaction

### Long-Term Memory
- Persistent information across multiple conversations
- Facts, preferences, and summaries
- Enables personalized experiences over time

## Memory Architecture Flow

```
1. Conversation Storage
   └── Complete conversations saved in raw form

2. Strategy Processing
   └── Configured strategies analyze conversations (background)

3. Information Extraction
   └── Important data extracted based on strategy types (~1 min)

4. Organized Storage
   └── Extracted info stored in structured namespaces

5. Semantic Retrieval
   └── Natural language queries retrieve relevant memories
```

## Memory Strategy Types

| Strategy | Purpose |
|----------|---------|
| **Semantic** | Stores factual information using vector embeddings |
| **Summary** | Creates/maintains conversation summaries |
| **User Preference** | Tracks user-specific preferences and settings |
| **Custom** | Customizable extraction and consolidation logic |

## Tutorial Structure (from repository)

```
04-AgentCore-memory/
├── 01-short-term-memory/
│   ├── 01-single-agent/
│   │   ├── with-strands-agent/
│   │   └── with-langgraph-agent/
│   └── 02-multi-agent/
├── 02-long-term-memory/
│   ├── 01-single-agent/
│   │   ├── using-strands-agent-hooks/
│   │   └── using-strands-agent-memory-tool/
│   └── 02-multi-agent/
├── 03-advanced-patterns/
├── 04-memory-branching/
└── 05-memory-security-patterns/
```

## Sample Use Cases

| Memory Type | Framework | Use Case |
|-------------|-----------|----------|
| Short-Term | Strands | Personal Agent |
| Short-Term | LangGraph | Fitness Coach |
| Short-Term | Strands | Travel Planning |
| Long-Term | Strands Hooks | Customer Support |
| Long-Term | Strands Tool | Culinary Assistant |
| Long-Term | Multi-Agent | Travel Booking |

## Integration Patterns

### Strands Agent Hooks
```python
# Memory integrated via lifecycle hooks
# Automatic save/retrieve on conversation events
```

### Strands Memory Tool
```python
# Memory exposed as a tool the agent can use
# Agent decides when to store/retrieve
```
