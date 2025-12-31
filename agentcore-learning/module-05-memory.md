# Module 5: AgentCore Memory

## 5.1 Short-Term Memory: Session Context

### The Problem: Goldfish Agents

Without memory, every agent call is isolated - no context preserved.

### Short-Term Memory Solution

Preserves context **within a session**:

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient()

# Create memory store
memory.create_memory_store(
    name="customer-support-memory",
    description="Memory for customer support conversations"
)

# Save conversation turns
session_id = "session-abc-123"
user_id = "user-456"

memory.save_event(
    memoryStoreId="customer-support-memory",
    sessionId=session_id,
    actorId=user_id,
    event={"role": "user", "content": "My name is Alice"}
)

# Retrieve session history
history = memory.get_session_events(
    memoryStoreId="customer-support-memory",
    sessionId=session_id
)
```

---

## 5.2 Long-Term Memory: Cross-Conversation Persistence

### Beyond Sessions

Long-term memory persists **forever** across all sessions:

```
Monday: "I'm allergic to peanuts" → [Stored in long-term memory]

2 WEEKS LATER (new session):
"Recommend a restaurant" → Agent excludes peanut dishes
                           [Retrieved from long-term memory]
```

### How It Works

```
Conversations          Extract           Long-Term Storage
(Raw Events)     ──────────────▶      (Facts, Preferences, Summaries)
                                              │
                                              ▼
                                      Semantic Search
                                     (future queries)
```

### Enabling Long-Term Memory

```python
memory.create_memory_store(
    name="personal-assistant-memory",
    memoryStrategies=[
        {"strategyType": "SEMANTIC", "configuration": {"embeddingModel": "amazon.titan-embed-text-v2"}},
        {"strategyType": "USER_PREFERENCE", "configuration": {}},
        {"strategyType": "SUMMARY", "configuration": {"summaryModel": "anthropic.claude-3-haiku"}}
    ]
)
```

---

## 5.3 Memory Strategies

| Strategy | What It Extracts | Use Case |
|----------|------------------|----------|
| **SEMANTIC** | Facts as vector embeddings | "User works at Google" |
| **SUMMARY** | Conversation summaries | "Discussed Q4 budget" |
| **USER_PREFERENCE** | Likes, dislikes | "Prefers email over phone" |
| **CUSTOM** | Your own extraction logic | Domain-specific info |

### SEMANTIC Memory

```python
# Configuration
{"strategyType": "SEMANTIC", "configuration": {"embeddingModel": "amazon.titan-embed-text-v2"}}

# Retrieval
results = memory.search_memories(
    memoryStoreId="my-memory",
    actorId="user-123",
    query="What pet does the user have?",
    maxResults=5
)
```

### SUMMARY Memory

```python
{"strategyType": "SUMMARY", "configuration": {"summaryModel": "anthropic.claude-3-haiku"}}

# Creates summaries like:
# "User planning 2-week trip to Japan in March. Budget ~$5000."
```

### USER_PREFERENCE Memory

```python
{"strategyType": "USER_PREFERENCE", "configuration": {}}

# Extracts:
# {"communication": "prefers email", "food": ["spicy", "vegetarian"]}
```

### CUSTOM Memory

```python
{
    "strategyType": "CUSTOM",
    "configuration": {
        "extractionPrompt": "Extract medical conditions, medications, allergies...",
        "extractionModel": "anthropic.claude-3-haiku"
    }
}
```

---

## 5.4 Memory Branching

For conversation forks and exploration:

```
                Turn 3
                  │
       ┌─────────┴─────────┐
       │                   │
   Branch A            Branch B
   (France)            (Italy)
```

### Implementation

```python
# Create branch
branch = memory.create_branch(
    memoryStoreId="travel-memory",
    sessionId="session-123",
    branchName="exploring-france",
    parentEventId="turn-3-event-id"
)

# Save to branch
memory.save_event(
    memoryStoreId="travel-memory",
    sessionId="session-123",
    branchId=branch["branchId"],
    event={"role": "user", "content": "Tell me about France"}
)

# Get branch history
history = memory.get_session_events(
    memoryStoreId="travel-memory",
    sessionId="session-123",
    branchId=branch["branchId"]
)
```

---

## 5.5 Memory Security Patterns

### Actor Isolation

Users can't access each other's memories:

```python
# User A's data
memory.save_event(actorId="user-A", ...)

# User B queries - can't see User A's data
memory.search_memories(actorId="user-B", ...)  # Returns nothing from User A
```

### Encryption

- At rest: AWS KMS, CMK supported
- In transit: TLS 1.2+

### TTL (Time-To-Live)

```python
memory.create_memory_store(
    name="support-memory",
    retentionConfiguration={
        "eventRetentionDays": 90,
        "memoryRetentionDays": 365,
        "sessionRetentionDays": 30
    }
)
```

### PII Handling

```python
memory.create_memory_store(
    name="healthcare-memory",
    piiConfiguration={
        "detectPii": True,
        "piiHandling": "MASK",  # MASK, REDACT, or ENCRYPT
        "piiTypes": ["SSN", "CREDIT_CARD", "PHONE"]
    }
)
```

---

## 5.6 Integration with Strands

### Approach 1: Hooks (Automatic)

```python
from strands import Agent
from strands.hooks import MemoryHook

memory_hook = MemoryHook(
    memory_client=memory,
    memory_store_id="my-memory",
    auto_save=True,
    auto_retrieve=True
)

agent = Agent(hooks=[memory_hook])
# Memory handled automatically
```

### Approach 2: Tools (Agent-Controlled)

```python
@tool
def remember(fact: str, user_id: str) -> str:
    """Store important fact for future reference."""
    memory.save_memory(memoryStoreId="my-memory", actorId=user_id, content=fact)
    return f"I'll remember: {fact}"

@tool
def recall(query: str, user_id: str) -> str:
    """Search for relevant memories."""
    results = memory.search_memories(memoryStoreId="my-memory", actorId=user_id, query=query)
    return "\n".join([r["content"] for r in results])

agent = Agent(tools=[remember, recall])
# Agent decides when to use memory
```

| Approach | Control | Use Case |
|----------|---------|----------|
| **Hooks** | Automatic | Simple apps |
| **Tools** | Agent decides | Complex apps |

---

## Module 5 Summary

### Key Points

1. **Short-term** = Session context (within one session)
2. **Long-term** = Persistent facts (across all sessions)
3. **Strategies** = SEMANTIC, SUMMARY, USER_PREFERENCE, CUSTOM
4. **Branching** = Conversation forks
5. **Security** = Actor isolation, encryption, TTL, PII handling
6. **Integration** = Hooks (automatic) or Tools (agent-controlled)

### Memory Flow

```
Conversation ──▶ Short-Term ──▶ Strategies ──▶ Long-Term ──▶ Semantic Search
(raw events)     (session)      (extract)      (permanent)    (future queries)
```

---

## Comprehension Check

1. What is the difference between short-term and long-term memory?

2. Which memory strategy would you use to store "user prefers vegetarian food"?

3. How does actor isolation protect user data?

4. When would you use memory hooks vs memory tools?
