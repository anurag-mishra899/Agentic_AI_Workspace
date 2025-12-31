# Amazon Bedrock AgentCore - Technical Question Checklist

## How to Use This Checklist
- Answer each question without looking at the modules
- Mark questions you struggle with for review
- Use `[ ]` for unanswered, `[x]` for mastered, `[?]` for needs review

---

## Module 1: Foundation & Mental Model

### Architecture & Core Concepts

- [ ] **Q1.1**: List all 7 AgentCore services and their primary purpose in one sentence each.

- [ ] **Q1.2**: What is the "production gap" and what infrastructure components would you need to build without AgentCore?

- [ ] **Q1.3**: What is MCP (Model Context Protocol) and what two standard operations does it provide?

- [ ] **Q1.4**: Draw the tool calling flow: `User → Agent → LLM → Gateway → Tool`. What happens at each step?

### Agent Patterns

- [ ] **Q1.5**: Describe the three agent patterns: Single Agent, A2A (Agent-to-Agent), and Agents as Tools. When would you use each?

- [ ] **Q1.6**: What is the difference between an orchestrator agent and a specialist agent?

### SDK & CLI

- [ ] **Q1.7**: What are the two pip packages needed for AgentCore? What does each provide?
  ```
  Package 1: _____________ (provides: _____________)
  Package 2: _____________ (provides: _____________)
  ```

- [ ] **Q1.8**: What are the five main `agentcore` CLI commands and what does each do?

- [ ] **Q1.9**: What is the ONLY AgentCore-specific code needed in your agent file? Write the minimal boilerplate.

---

## Module 2: AgentCore Runtime

### The Entrypoint Pattern

- [ ] **Q2.1**: What are the 5 things the `@app.entrypoint` decorator does to your function?

- [ ] **Q2.2**: What is the function signature for an entrypoint function? What type does `payload` have and what must you return?

- [ ] **Q2.3**: Write the minimal agent code structure with Strands:
  ```python
  # Fill in the blanks
  from _____________ import _____________
  from _____________ import _____________

  app = _____________
  agent = _____________

  @_____________
  def invoke(payload):
      result = _____________
      return _____________

  if __name__ == "__main__":
      _____________
  ```

### Local Development & Deployment

- [ ] **Q2.4**: What is the local development flow? (3 steps before Docker, then 2 steps with Docker)

- [ ] **Q2.5**: What does `agentcore configure -e my_agent.py` do? (List 4 things)

- [ ] **Q2.6**: What AWS resources does `agentcore launch` create? (List at least 4)

- [ ] **Q2.7**: What are the optional flags for `agentcore configure`? (`--name`, `--memory`, `--timeout` - what does each do?)

### MCP Servers & A2A

- [ ] **Q2.8**: Why would you host an MCP server on Runtime instead of just an agent?

- [ ] **Q2.9**: In A2A communication, what IAM permission does the orchestrator need to call specialist agents? Write the IAM statement.

- [ ] **Q2.10**: What is bi-directional streaming and why is it important for UX? How do you implement it?

---

## Module 3: AgentCore Gateway

### Core Concepts

- [ ] **Q3.1**: What problem does Gateway solve? (Describe the "integration nightmare")

- [ ] **Q3.2**: What are the three types of targets Gateway supports?

- [ ] **Q3.3**: What are the two MCP operations Gateway exposes?

### Target Configuration

- [ ] **Q3.4**: Write the boto3 code to create a Gateway and add a Lambda function as a target.

- [ ] **Q3.5**: How do you create a target from an OpenAPI spec? What two fields are required in `openApiTarget`?

### Semantic Tool Search

- [ ] **Q3.6**: What is semantic tool search and why does it reduce costs?

- [ ] **Q3.7**: Write the code to enable semantic search when creating a Gateway.

- [ ] **Q3.8**: How do you use semantic search to get only relevant tools instead of all 100 tools?

### Security Features

- [ ] **Q3.9**: What is bearer token injection? Write the configuration for it.

- [ ] **Q3.10**: What is header propagation? When would you use it?

- [ ] **Q3.11**: How do you restrict a tool to only users with specific claims (e.g., role=admin)?

- [ ] **Q3.12**: What masking rules are available for sensitive data? (List 3 patterns)

- [ ] **Q3.13**: What does masked data look like? Show before/after for SSN and email.

---

## Module 4: AgentCore Identity

### Authentication Directions

- [ ] **Q4.1**: What is the difference between inbound and outbound authentication? What question does each answer?

- [ ] **Q4.2**: List the supported methods for inbound authentication (2 methods).

- [ ] **Q4.3**: List the supported methods for outbound authentication (4 methods).

### OAuth Flows

- [ ] **Q4.4**: What is 2-legged OAuth (Client Credentials)? When would you use it? (Give 3 scenarios)

- [ ] **Q4.5**: What is 3-legged OAuth (Authorization Code)? When would you use it? (Give 3 scenarios)

- [ ] **Q4.6**: In 3-legged OAuth, who stores and manages the tokens? What happens when they expire?

- [ ] **Q4.7**: Write the boto3 code to create a credential provider for 2-legged OAuth.

- [ ] **Q4.8**: Write the boto3 code to create a credential provider for 3-legged OAuth (e.g., Google).

### Identity Provider Integration

- [ ] **Q4.9**: What are the three enterprise IdPs that AgentCore supports for inbound auth?

- [ ] **Q4.10**: Write the configuration for Cognito inbound authentication.

- [ ] **Q4.11**: What OIDC configuration fields are needed for Okta or Entra ID?

### Zero Trust & Delegation

- [ ] **Q4.12**: What are the 6 token validation steps in zero trust?

- [ ] **Q4.13**: What is the difference between delegation and impersonation? Why does AgentCore use delegation?

- [ ] **Q4.14**: In a delegation token, what do `sub` and `act.sub` represent?

---

## Module 5: AgentCore Memory

### Short-Term vs Long-Term

- [ ] **Q5.1**: What is short-term memory? What is its scope?

- [ ] **Q5.2**: What is long-term memory? How does it differ from short-term?

- [ ] **Q5.3**: Write the code to save an event to short-term memory.

- [ ] **Q5.4**: Write the code to retrieve session history.

### Memory Strategies

- [ ] **Q5.5**: List the 4 memory strategies and what each extracts.
  ```
  SEMANTIC: _____________
  SUMMARY: _____________
  USER_PREFERENCE: _____________
  CUSTOM: _____________
  ```

- [ ] **Q5.6**: Write the configuration to create a memory store with SEMANTIC and SUMMARY strategies.

- [ ] **Q5.7**: How do you search long-term memories? Write the code.

- [ ] **Q5.8**: What is the CUSTOM strategy? When would you use it? Write an example configuration.

### Memory Branching

- [ ] **Q5.9**: What is memory branching? Draw the branching diagram.

- [ ] **Q5.10**: Write the code to create a branch and save events to it.

### Security

- [ ] **Q5.11**: What is actor isolation and why is it important?

- [ ] **Q5.12**: What are the three TTL configurations for memory retention?

- [ ] **Q5.13**: What are the three PII handling options? (`MASK`, `REDACT`, `ENCRYPT`)

### Integration

- [ ] **Q5.14**: What are the two approaches for integrating memory with Strands agents?

- [ ] **Q5.15**: When would you use memory hooks vs memory tools?

---

## Module 6: AgentCore Tools

### Code Interpreter

- [ ] **Q6.1**: What problem does Code Interpreter solve? Why not execute code on user's machine or your servers?

- [ ] **Q6.2**: What three language runtimes does Code Interpreter support?

- [ ] **Q6.3**: What security properties does the Code Interpreter sandbox provide? (List 5)

- [ ] **Q6.4**: Write the code to create a Code Interpreter session and execute Python code.

### Session Persistence

- [ ] **Q6.5**: Why are sessions important in Code Interpreter? Show the difference between stateless and stateful execution.

- [ ] **Q6.6**: Write code demonstrating session persistence (define function in one call, use it in another).

### S3 Integration

- [ ] **Q6.7**: What problem does S3 integration solve? What are the limits of API payloads?

- [ ] **Q6.8**: Write the code to configure a session with S3 input/output buckets.

- [ ] **Q6.9**: In the sandbox, what paths map to S3? (`/input/` → ?, `/output/` → ?)

### Browser Tool

- [ ] **Q6.10**: What problem does Browser Tool solve? List 3 use cases.

- [ ] **Q6.11**: What security properties does Browser Tool provide? (List 5)

- [ ] **Q6.12**: Write the code to create a browser session and execute navigation commands.

- [ ] **Q6.13**: What is Live View? What are 4 use cases for it?

### VPC Integration

- [ ] **Q6.14**: Why would you configure Browser Tool with VPC access?

- [ ] **Q6.15**: Write the VPC configuration for a browser session.

### Combining Tools

- [ ] **Q6.16**: When would you use both Code Interpreter and Browser Tool together? Give an example workflow.

---

## Module 7: AgentCore Observability

### Why Agent Observability is Different

- [ ] **Q7.1**: How does the execution flow of an agent differ from a traditional application?

- [ ] **Q7.2**: List 5 agent failure modes that observability helps debug.

- [ ] **Q7.3**: What 6 questions does observability answer about your agent?

### OpenTelemetry

- [ ] **Q7.4**: What is OpenTelemetry and why does AgentCore use it?

- [ ] **Q7.5**: Define: Trace, Span, Attributes. How do they relate?

- [ ] **Q7.6**: Draw an example trace with parent span and child spans (agent invocation → LLM call → tool call → LLM call).

### Automatic vs Manual Instrumentation

- [ ] **Q7.7**: What gets captured automatically when running on AgentCore Runtime? (List 6 things)

- [ ] **Q7.8**: When do you need manual instrumentation? (2 scenarios)

- [ ] **Q7.9**: Write the code for manual OpenTelemetry instrumentation (configure provider, create spans).

- [ ] **Q7.10**: What framework-specific instrumentors are available? (Strands, LangGraph, CrewAI)

### CloudWatch Integration

- [ ] **Q7.11**: How do you enable CloudWatch Transaction Search?

- [ ] **Q7.12**: What views does the CloudWatch GenAI Dashboard provide? (List 3)

- [ ] **Q7.13**: Write a CloudWatch Logs query to find traces with errors.

### Custom Spans & Context Propagation

- [ ] **Q7.14**: When would you create custom spans? Give 3 examples of business context.

- [ ] **Q7.15**: In multi-service architectures, how do you propagate trace context? What functions do you use?

### Partner Integrations

- [ ] **Q7.16**: What are 4 partner integrations for observability? What is each best for?

---

## Module 8: Evaluations & Policy

### Observability vs Evaluations

- [ ] **Q8.1**: What question does observability answer vs what question does evaluations answer?

- [ ] **Q8.2**: Give an example where observability shows success but evaluations show failure.

### Built-in Evaluators

- [ ] **Q8.3**: List all 13 built-in evaluators.

- [ ] **Q8.4**: What is the score range for evaluators? What does a high toxicity score mean?

- [ ] **Q8.5**: Write the code to evaluate a trace with 3 built-in evaluators.

### Custom Evaluators

- [ ] **Q8.6**: When would you create a custom evaluator? Give 3 business-specific examples.

- [ ] **Q8.7**: What are the 3 custom evaluator types? When would you use each?

- [ ] **Q8.8**: Write the code to create an LLM_AS_JUDGE custom evaluator.

- [ ] **Q8.9**: Write the code to create a PROGRAMMATIC custom evaluator.

### On-Demand vs Online

- [ ] **Q8.10**: What is the difference between on-demand and online evaluations?
  ```
  On-Demand: When: _____, How: _____, What: _____, Use for: _____
  Online: When: _____, How: _____, What: _____, Use for: _____
  ```

- [ ] **Q8.11**: Write the code to configure online evaluation with sampling and alerting.

### Policy Engine

- [ ] **Q8.12**: What problem does Policy Engine solve? Give a scenario without policy vs with policy.

- [ ] **Q8.13**: Draw the policy architecture: Agent → Gateway → Policy Engine → Target.

### Cedar Language

- [ ] **Q8.14**: What is Cedar? What is its basic structure? (`permit(principal, action, resource) when { conditions }`)

- [ ] **Q8.15**: Write a Cedar policy to allow applications under $1M coverage.

- [ ] **Q8.16**: Write a Cedar policy to restrict a tool to users with role "senior-adjuster".

- [ ] **Q8.17**: Write a Cedar `forbid` policy to deny high-value refunds.

### NL2Cedar & Policy Modes

- [ ] **Q8.18**: What is NL2Cedar? Write an example natural language input and expected Cedar output.

- [ ] **Q8.19**: What are the two policy modes? When would you use each?

- [ ] **Q8.20**: CRITICAL: What is the default action when Policy Engine is attached in ENFORCE mode? Why is this important?

---

## Module 9: Framework Integrations

### Framework-Agnostic Architecture

- [ ] **Q9.1**: What is the only AgentCore-specific code needed regardless of framework?

- [ ] **Q9.2**: Draw the integration diagram: Frameworks → @app.entrypoint → AgentCore Infrastructure.

### Framework-Specific Integration

- [ ] **Q9.3**: Write the integration code for each framework:
  - Strands Agents
  - LangGraph
  - CrewAI
  - LlamaIndex

- [ ] **Q9.4**: What special features does Strands have with AgentCore? (List 4)

- [ ] **Q9.5**: How do you use Gateway tools with Strands?

- [ ] **Q9.6**: How do you use Memory with Strands? (MemoryHook)

- [ ] **Q9.7**: What is LangGraph checkpointing and how do you enable it?

### Framework Selection

- [ ] **Q9.8**: Complete the framework selection guide:
  ```
  Simple agent with tools → _____________
  RAG / Document Q&A → _____________
  Complex multi-step workflows → _____________
  Role-based multi-agent teams → _____________
  Type-safe responses → _____________
  Multi-agent conversations → _____________
  Migrating from OpenAI → _____________
  ```

- [ ] **Q9.9**: What is the complexity level of each framework? (Low/Medium/High)

### Common Patterns

- [ ] **Q9.10**: Write the pattern for adding observability to any framework.

- [ ] **Q9.11**: Write the pattern for adding memory to any framework.

- [ ] **Q9.12**: Write the pattern for using Gateway tools with any framework.

---

## Module 10: Production Deployment

### Production Checklist

- [ ] **Q10.1**: List the 5 categories in the production readiness checklist.

- [ ] **Q10.2**: What items fall under each category? (Infrastructure, Security, Observability, Quality, Operations)

### Infrastructure as Code

- [ ] **Q10.3**: What are the 3 IaC options for AgentCore? What is each best for?

- [ ] **Q10.4**: Write a CloudFormation template for AgentCore Runtime with IAM role.

- [ ] **Q10.5**: Write CDK code (Python) for AgentCore Runtime with ECR repo.

- [ ] **Q10.6**: Write Terraform code for ECR repo and IAM role.

### Multi-Agent Architectures

- [ ] **Q10.7**: Draw the orchestrator + specialists architecture.

- [ ] **Q10.8**: What IAM policy does an orchestrator need to call specialists?

- [ ] **Q10.9**: When should you use multi-agent vs single agent? (List 6 scenarios)

### VPC Integration

- [ ] **Q10.10**: What is the difference between agent without VPC vs with VPC?

- [ ] **Q10.11**: Write CDK code to create a VPC with private subnets and security group.

- [ ] **Q10.12**: What VPC endpoints should you add for AWS services? (List 3)

### Cost Optimization

- [ ] **Q10.13**: What is the cost breakdown for AgentCore? (LLM calls %, Runtime %, Tools %, Storage %)

- [ ] **Q10.14**: List 4 cost optimization strategies.

- [ ] **Q10.15**: How does model selection reduce costs? Write example code.

- [ ] **Q10.16**: How does semantic tool search reduce costs?

- [ ] **Q10.17**: Write a CloudWatch alarm for daily spend threshold.

### Scaling & CI/CD

- [ ] **Q10.18**: What scaling configuration options are available? (minInstances, maxInstances, targetConcurrency, etc.)

- [ ] **Q10.19**: Draw the CI/CD pipeline stages (5 stages).

- [ ] **Q10.20**: Write a GitHub Actions workflow for AgentCore deployment.

---

## Quick Reference Answers

### Key Code Patterns

```python
# Minimal Agent Boilerplate
from bedrock_agentcore import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    return {"response": "..."}

if __name__ == "__main__":
    app.run()
```

```python
# Gateway Client
from bedrock_agentcore.gateway import GatewayClient
gateway = GatewayClient(gateway_id="my-gateway")
tools = gateway.list_tools()
```

```python
# Memory Client
from bedrock_agentcore.memory import MemoryClient
memory = MemoryClient()
memory.save_event(memoryStoreId="...", sessionId="...", actorId="...", event={...})
memories = memory.search_memories(memoryStoreId="...", actorId="...", query="...")
```

```python
# Identity Client
from bedrock_agentcore.identity import IdentityClient
identity = IdentityClient()
token = identity.get_user_token(credential_provider="...", user_id="...")
```

```python
# Code Interpreter
from bedrock_agentcore.tools import CodeInterpreterClient
code_interpreter = CodeInterpreterClient()
session = code_interpreter.create_session(runtime="python")
result = code_interpreter.execute(sessionId=session["sessionId"], code="...")
```

```python
# Evaluations
from bedrock_agentcore.evaluations import EvaluationsClient
evals = EvaluationsClient()
result = evals.evaluate(traceId="...", evaluators=["correctness", "safety"])
```

### Key Numbers to Remember

| Metric | Value |
|--------|-------|
| Built-in evaluators | 13 |
| Memory strategies | 4 (SEMANTIC, SUMMARY, USER_PREFERENCE, CUSTOM) |
| Gateway target types | 3 (Lambda, OpenAPI, Smithy) |
| OAuth flow types | 2 (2-legged, 3-legged) |
| Code Interpreter runtimes | 3 (Python, JavaScript, TypeScript) |
| Framework integrations | 8+ (Strands, LangGraph, CrewAI, LlamaIndex, PydanticAI, AutoGen, OpenAI SDK) |
| LLM cost percentage | 60-70% |
| Token validation steps | 6 |

### Critical Concepts

1. **@app.entrypoint** - Only AgentCore-specific code needed
2. **MCP Protocol** - Universal tool interface (listTools, callTool)
3. **Default DENY** - Policy Engine blocks everything unless explicitly permitted
4. **Delegation not Impersonation** - Agent acts FOR user, not AS user
5. **Trace = Journey, Span = Operation** - OpenTelemetry hierarchy
6. **Automatic vs Manual Instrumentation** - Runtime vs elsewhere

---

## Self-Assessment Score

Count your `[x]` marks:

| Range | Level |
|-------|-------|
| 0-40 | Beginner - Review all modules |
| 41-80 | Intermediate - Focus on weak areas |
| 81-100 | Advanced - Ready for hands-on labs |
| 101+ | Expert - Ready for production deployment |

**Total Questions: ~115**

---

## Review Schedule

- [ ] Week 1: Modules 1-3 (Foundation, Runtime, Gateway)
- [ ] Week 2: Modules 4-6 (Identity, Memory, Tools)
- [ ] Week 3: Modules 7-8 (Observability, Evaluations & Policy)
- [ ] Week 4: Modules 9-10 (Framework Integrations, Production)
- [ ] Week 5: Full review + Hands-on labs
