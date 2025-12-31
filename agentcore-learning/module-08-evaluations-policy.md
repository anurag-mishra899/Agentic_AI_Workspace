# Module 8: AgentCore Evaluations & Policy

## 8.1 Observability vs Evaluations

### Different Questions, Different Tools

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   OBSERVABILITY                    EVALUATIONS                       │
│   ─────────────                    ───────────                       │
│   "What happened?"                 "How good was it?"                │
│                                                                      │
│   • Traces and spans               • Quality scores                  │
│   • Latencies                      • Correctness metrics             │
│   • Tool calls                     • Helpfulness ratings             │
│   • Errors                         • Safety assessments              │
│                                                                      │
│   Answer: "Agent called            Answer: "The response was         │
│   get_weather, took 2.3s"          85% correct and helpful"          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The Evaluation Challenge

```
User: "What's the capital of France?"

Agent Response A: "Paris is the capital of France."
Agent Response B: "The capital of France is Paris, a beautiful city on the Seine."
Agent Response C: "France's capital is Berlin." ← WRONG!

Observability sees: All 3 completed successfully, ~1s latency
Evaluations sees: A=correct, B=correct+helpful, C=INCORRECT
```

---

## 8.2 Built-in Evaluators

### 13 Built-in Metrics

AgentCore provides evaluators for critical quality dimensions:

| Evaluator | What It Measures | Score Range |
|-----------|------------------|-------------|
| **Correctness** | Is the answer factually accurate? | 0-1 |
| **Helpfulness** | Does it address the user's need? | 0-1 |
| **Relevance** | Is the response on-topic? | 0-1 |
| **Coherence** | Is it logical and well-structured? | 0-1 |
| **Safety** | Is it free from harmful content? | 0-1 |
| **Groundedness** | Is it supported by provided context? | 0-1 |
| **Faithfulness** | Does it stick to source material? | 0-1 |
| **Toxicity** | Contains offensive language? | 0-1 (lower=better) |
| **Fluency** | Is it grammatically correct? | 0-1 |
| **Completeness** | Does it fully answer the question? | 0-1 |
| **Conciseness** | Is it appropriately brief? | 0-1 |
| **Tool Selection** | Did it choose the right tools? | 0-1 |
| **Task Completion** | Did it complete the requested task? | 0-1 |

### Using Built-in Evaluators

```python
from bedrock_agentcore.evaluations import EvaluationsClient

evals = EvaluationsClient()

# Evaluate a single trace
result = evals.evaluate(
    traceId="abc-123-def",
    evaluators=["correctness", "helpfulness", "safety"]
)

print(result)
# {
#     "correctness": {"score": 0.92, "explanation": "Response accurately..."},
#     "helpfulness": {"score": 0.88, "explanation": "Addressed user's question..."},
#     "safety": {"score": 1.0, "explanation": "No harmful content detected"}
# }
```

---

## 8.3 Custom Evaluators

### When Built-in Isn't Enough

Your business may have domain-specific quality requirements:

```
Built-in: "Is the response helpful?"
Custom:   "Does it follow our company's tone guidelines?"
Custom:   "Does it correctly apply our refund policy?"
Custom:   "Does it avoid mentioning competitor products?"
```

### Creating Custom Evaluators

```python
# Create a custom evaluator
evals.create_evaluator(
    name="brand-tone-compliance",
    description="Checks if response follows brand guidelines",
    evaluatorType="LLM_AS_JUDGE",
    configuration={
        "model": "anthropic.claude-3-haiku",
        "prompt": """
        Evaluate if the following response follows our brand guidelines:

        Brand Guidelines:
        - Professional but friendly tone
        - No jargon or technical terms unless necessary
        - Always offer to help further
        - Never use phrases like "I cannot" - instead say "Let me find another way"

        Response to evaluate:
        {response}

        Score 0-1 based on compliance. Explain your reasoning.
        """,
        "outputFormat": {
            "score": "float",
            "explanation": "string"
        }
    }
)
```

### Custom Evaluator Types

| Type | How It Works | Best For |
|------|--------------|----------|
| **LLM_AS_JUDGE** | Another LLM scores the response | Subjective quality, tone, style |
| **PROGRAMMATIC** | Code-based rules | Exact matches, format validation |
| **HUMAN_IN_LOOP** | Routes to human reviewer | High-stakes decisions |

### Programmatic Evaluator Example

```python
evals.create_evaluator(
    name="response-length-check",
    evaluatorType="PROGRAMMATIC",
    configuration={
        "code": """
def evaluate(response):
    word_count = len(response.split())
    if word_count < 10:
        return {"score": 0.3, "explanation": "Response too short"}
    elif word_count > 500:
        return {"score": 0.5, "explanation": "Response too long"}
    else:
        return {"score": 1.0, "explanation": "Appropriate length"}
"""
    }
)
```

---

## 8.4 On-Demand vs Online Evaluations

### Two Evaluation Modes

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   ON-DEMAND EVALUATIONS              ONLINE EVALUATIONS              │
│   ─────────────────────              ──────────────────              │
│                                                                      │
│   When: Development, testing         When: Production                │
│   How: You trigger manually          How: Automatic sampling         │
│   What: Specific traces              What: Statistical sample        │
│   Cost: Per evaluation               Cost: Based on sample rate      │
│                                                                      │
│   Use for:                           Use for:                        │
│   • Debugging specific issues        • Continuous monitoring         │
│   • A/B testing prompts              • Trend detection               │
│   • Pre-deployment validation        • Alerting on quality drops     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### On-Demand Evaluation

```python
# Evaluate specific trace (synchronous)
result = evals.evaluate_on_demand(
    traceId="abc-123",
    evaluators=["correctness", "brand-tone-compliance"]
)

# Returns immediately with scores
print(result["correctness"]["score"])  # 0.95
```

### Online Evaluation Setup

```python
# Configure continuous evaluation for production
evals.create_online_evaluation(
    name="production-quality-monitor",
    agentId="my-agent-id",
    samplingConfiguration={
        "sampleRate": 0.05,  # Evaluate 5% of requests
        "minSamplesPerHour": 10,
        "maxSamplesPerHour": 100
    },
    evaluators=["correctness", "helpfulness", "safety"],
    alertConfiguration={
        "threshold": 0.7,  # Alert if score drops below 0.7
        "metric": "correctness",
        "snsTopicArn": "arn:aws:sns:..."
    }
)
```

### Evaluation Results Flow

```
                    On-Demand                    Online
                        │                           │
                        ▼                           ▼
               ┌────────────────┐         ┌────────────────┐
               │ Single Trace   │         │ Sampled Traces │
               │ Evaluation     │         │ (5% of traffic)│
               └───────┬────────┘         └───────┬────────┘
                       │                          │
                       ▼                          ▼
               ┌────────────────┐         ┌────────────────┐
               │ Immediate      │         │ Aggregated     │
               │ Results        │         │ Metrics        │
               │                │         │                │
               │ score: 0.92    │         │ avg: 0.89      │
               │ explanation:.. │         │ p95: 0.95      │
               └────────────────┘         │ trend: ↑       │
                                          └────────────────┘
```

---

## 8.5 Acting on Evaluation Results

### Quality Feedback Loop

```python
# Query evaluation results
results = evals.query_evaluations(
    agentId="my-agent-id",
    timeRange={"hours": 24},
    groupBy="evaluator"
)

# Identify problem areas
for evaluator, metrics in results.items():
    if metrics["average"] < 0.8:
        print(f"⚠️ {evaluator}: {metrics['average']:.2f} - needs attention")
    else:
        print(f"✓ {evaluator}: {metrics['average']:.2f}")

# Output:
# ✓ correctness: 0.91
# ⚠️ helpfulness: 0.72 - needs attention
# ✓ safety: 0.99
```

### Drill Down into Low Scores

```python
# Find traces with low helpfulness scores
low_scores = evals.query_evaluations(
    agentId="my-agent-id",
    evaluator="helpfulness",
    scoreRange={"max": 0.7},
    limit=10
)

for trace in low_scores:
    print(f"Trace: {trace['traceId']}")
    print(f"Score: {trace['score']}")
    print(f"Explanation: {trace['explanation']}")
    print(f"Input: {trace['input'][:100]}...")
    print("---")
```

---

## 8.6 AgentCore Policy: Governance & Access Control

### The Problem: Agents Need Guardrails

```
Without Policy:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   User: "Process a refund for $50,000"                              │
│                                                                      │
│   Agent: "Done! I've processed the $50,000 refund."                 │
│                                                                      │
│   Problem: No authorization check! Anyone can request any refund.   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

With Policy:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   User: "Process a refund for $50,000"                              │
│                                                                      │
│   Policy Engine: "User role=agent, max_refund=$1000" → DENY         │
│                                                                      │
│   Agent: "I'm not authorized to process refunds over $1,000.        │
│           Please contact a supervisor."                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Policy Architecture

```
┌─────────────┐
│   AI Agent  │
└──────┬──────┘
       │ Tool Call Request
       ▼
┌─────────────────────┐
│  AgentCore Gateway  │
└──────┬──────────────┘
       │ Policy Check
       ▼
┌─────────────────────┐
│   Policy Engine     │  ← Cedar Policies
│   (Real-time eval)  │
└──────┬──────────────┘
       │ ALLOW / DENY
       ▼
┌─────────────────────┐
│   Lambda Target     │  ← Only executes if ALLOWED
└─────────────────────┘
```

---

## 8.7 Cedar Policy Language

### What is Cedar?

Cedar is a **declarative policy language** developed by AWS. It's designed for authorization decisions.

### Basic Structure

```cedar
permit(
    principal,           // WHO can access
    action,              // WHAT action they can perform
    resource             // ON what resource
) when {
    conditions           // UNDER what conditions
};
```

### Real Examples

**Allow applications under $1M coverage:**
```cedar
permit(
    principal,
    action == AgentCore::Action::"ApplicationTool___create_application",
    resource == AgentCore::Gateway::"arn:aws:agentcore:us-east-1:123456:gateway/my-gateway"
) when {
    context.input.coverage_amount <= 1000000
};
```

**Restrict by user role:**
```cedar
permit(
    principal,
    action == AgentCore::Action::"ApprovalTool___approve_claim",
    resource == AgentCore::Gateway::"<gateway-arn>"
) when {
    principal.getTag("role") == "senior-adjuster" &&
    context.input.claim_amount <= 100000
};
```

**Deny high-risk operations:**
```cedar
forbid(
    principal,
    action == AgentCore::Action::"RefundTool___process_refund",
    resource == AgentCore::Gateway::"<gateway-arn>"
) when {
    context.input.amount > 10000
};
```

---

## 8.8 Natural Language Policy Authoring (NL2Cedar)

### Write Policies in Plain English

Instead of learning Cedar syntax, write policies naturally:

```
Natural Language:
"Allow all users to invoke the application tool when the
coverage amount is under 1 million and the region is US or Canada"

        │
        ▼ NL2Cedar

Generated Cedar:
permit(
    principal,
    action == AgentCore::Action::"ApplicationTool___create_application",
    resource == AgentCore::Gateway::"<gateway-arn>"
) when {
    (context.input.coverage_amount < 1000000) &&
    ((context.input.applicant_region == "US") ||
     (context.input.applicant_region == "CAN"))
};
```

### Implementation

```python
from bedrock_agentcore.policy import PolicyClient

policy = PolicyClient()

# Generate Cedar from natural language
generated = policy.generate_policy(
    gatewayId="my-gateway",
    naturalLanguage="""
    Allow all users to invoke the risk model tool when
    data governance approval is true.
    Block users from calling the approval tool unless
    they have the role senior-adjuster.
    """
)

# Creates multiple policies from multi-line input
for cedar_policy in generated["generatedPolicies"]:
    print(cedar_policy)
```

### Principal-Based Policies

```
Natural Language:
"Forbid principals from using the approval tool unless
they have the scope group:Controller"

Generated Cedar:
forbid(
    principal,
    action == AgentCore::Action::"ApprovalTool",
    resource == AgentCore::Gateway::"<gateway-arn>"
) when {
    !((principal.hasTag("scope")) &&
      (principal.getTag("scope") like "*group:Controller*"))
};
```

---

## 8.9 Policy Modes and Lifecycle

### Policy Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **LOG_ONLY** | Evaluates but doesn't block | Testing, shadow mode |
| **ENFORCE** | Actively blocks violations | Production |

### Policy Lifecycle

```
1. Write Policy (Natural Language or Cedar)
        │
        ▼
2. Create in LOG_ONLY mode
        │
        ▼
3. Monitor decisions in CloudWatch
        │
        ▼
4. Verify expected ALLOW/DENY patterns
        │
        ▼
5. Switch to ENFORCE mode
        │
        ▼
6. Production enforcement
```

### Important: Default DENY

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚠️  CRITICAL CONCEPT                                                │
│                                                                      │
│  When a Policy Engine is attached to a Gateway in ENFORCE mode:     │
│                                                                      │
│  DEFAULT ACTION = DENY                                              │
│                                                                      │
│  You must EXPLICITLY create permit policies for each tool           │
│  you want to allow access to.                                       │
│                                                                      │
│  No policy = No access                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8.10 Combined Quality Stack

### Evaluations + Policy + Observability

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRODUCTION AGENT                                 │
│                                                                      │
│                          Request                                     │
│                             │                                        │
│        ┌────────────────────┼────────────────────┐                  │
│        ▼                    ▼                    ▼                  │
│   ┌─────────┐         ┌──────────┐         ┌──────────┐            │
│   │ POLICY  │         │OBSERV-   │         │ EVAL-    │            │
│   │         │         │ABILITY   │         │ UATIONS  │            │
│   │ "Can    │         │          │         │          │            │
│   │  they   │         │ "What    │         │ "How     │            │
│   │  do     │         │  happened│         │  good    │            │
│   │  this?" │         │  ?"      │         │  was it?"│            │
│   └────┬────┘         └────┬─────┘         └────┬─────┘            │
│        │                   │                    │                   │
│   ALLOW/DENY          Traces/Spans          Scores                 │
│        │                   │                    │                   │
│        └───────────────────┴────────────────────┘                   │
│                            │                                        │
│                    Quality Feedback Loop                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Scenario | Tool |
|----------|------|
| "Is this user allowed to process refunds?" | **Policy** |
| "Why did the agent call that tool?" | **Observability** |
| "Was the agent's response accurate?" | **Evaluations** |
| "Who processed the $50K refund yesterday?" | **Observability** |
| "Is our agent getting better or worse over time?" | **Evaluations** |
| "Prevent agents from accessing customer PII" | **Policy** |

---

## Module 8 Summary

### Key Points

1. **Evaluations measure quality** — Correctness, helpfulness, safety scores
2. **13 built-in evaluators** — Plus custom evaluators for business needs
3. **On-demand vs Online** — Manual testing vs continuous production monitoring
4. **Policy provides governance** — Fine-grained access control for agent actions
5. **Cedar language** — Declarative policy syntax (permit/forbid)
6. **NL2Cedar** — Write policies in plain English
7. **Default DENY** — Must explicitly permit each allowed action
8. **Combined stack** — Policy + Observability + Evaluations = production-ready

### Decision Guide

```
Need to...                              Use...
─────────────────────────────────────────────────────────────────
Measure response quality            →   Evaluations
Block unauthorized actions          →   Policy
Debug agent behavior                →   Observability
Monitor quality trends              →   Online Evaluations
Test specific traces                →   On-Demand Evaluations
Restrict by user role               →   Policy (principal-based)
Check if response is correct        →   Evaluations (correctness)
```

---

## Comprehension Check

1. What is the difference between Observability and Evaluations?

2. When would you use On-Demand vs Online evaluations?

3. What happens by default when a Policy Engine is attached to a Gateway in ENFORCE mode?

4. What is Cedar and what does NL2Cedar do?

