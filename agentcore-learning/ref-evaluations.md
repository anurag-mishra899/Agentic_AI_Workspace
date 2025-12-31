# AgentCore Evaluations & Policy - Reference

## Evaluations Overview

AgentCore Evaluations helps optimize agent quality based on real-world interactions. While Observability provides operational insights into agent health, Evaluations focuses on agent **decision quality** and **performance outcomes**.

## Key Features

### Built-in Evaluators
13 built-in evaluators for critical dimensions:
- Correctness
- Helpfulness
- Safety
- Relevance
- Coherence
- And more...

### Custom Evaluators
Create evaluators for business-specific requirements.

### Evaluation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **On-Demand** | Synchronous evaluation on individual traces | Development, testing, debugging |
| **Online** | Automatic sampling and evaluation in production | Production monitoring at scale |

## On-Demand Evaluations

Run synchronous evaluations using built-in and custom metrics on individual traces.

**Input**: OpenTelemetry (OTEL) traces

**Output**:
- Score value
- Explanation for the score
- Token usage

## Online Evaluations

Continuous performance monitoring without manual evaluation:

1. Define sample size and trace selection criteria
2. Choose evaluation metrics
3. AgentCore handles sampling and evaluation
4. Performance data generated automatically

## Tutorial Structure

```
07-AgentCore-evaluations/
├── 00-prereqs/                    # Sample agent setup
├── 01-creating-custom-evaluators/ # Custom metric creation
├── 02-running-evaluations/        # On-demand and online usage
├── 03-advanced/                   # CloudWatch queries, dashboards
└── 04-using-evaluation-results/   # Acting on evaluation data
```

---

## Policy Overview

AgentCore Policy provides governance and access control for agent actions.

## Key Features

### Natural Language Policy Authoring
Write policies in plain English that get compiled to enforcement rules.

### Fine-Grained Access Control
- Control which tools agents can access
- Restrict actions based on user context
- Implement business rules as policies

## Tutorial Structure

```
08-AgentCore-policy/
├── 01-Getting-Started/
├── 02-Natural-Language-Policy-Authoring/
└── 03-Fine-Grained-Access-Control/
```

## Combined Quality Stack

```
┌─────────────────────────────────────┐
│         Production Agent            │
└─────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌───────┐  ┌─────────┐  ┌────────┐
│Policy │  │Observ-  │  │Eval-   │
│(Guard)│  │ability  │  │uations │
│       │  │(Monitor)│  │(Score) │
└───────┘  └─────────┘  └────────┘
    │           │           │
    └───────────┴───────────┘
                │
        Quality Feedback Loop
```
