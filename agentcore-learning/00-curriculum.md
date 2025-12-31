# Amazon Bedrock AgentCore - Learning Curriculum

## Module Overview

| Module | Title | Goal |
|--------|-------|------|
| 1 | Foundation & Mental Model | Understand what AgentCore is and why it exists |
| 2 | AgentCore Runtime | Deploy your first agent to AWS |
| 3 | AgentCore Gateway | Convert APIs and Lambda functions into MCP tools |
| 4 | AgentCore Identity | Implement secure authentication for agents |
| 5 | AgentCore Memory | Give agents persistent memory |
| 6 | AgentCore Tools | Use AWS-managed execution environments |
| 7 | AgentCore Observability | Trace, debug, and monitor agents in production |
| 8 | Evaluations & Policy | Ensure agent quality and compliance |
| 9 | Framework Integrations | Use AgentCore with your preferred framework |
| 10 | Production Deployment | Deploy production-ready agent systems |
| 11 | Capstone | Build a complete production agent |

---

## Module 1: Foundation & Mental Model

| Topic | Content |
|-------|---------|
| 1.1 | The Problem Space: Why agent infrastructure is hard |
| 1.2 | AgentCore Architecture Overview: The 7 core services |
| 1.3 | Key Concepts: MCP protocol, tool calling, agent patterns |
| 1.4 | SDK & CLI Overview: `bedrock-agentcore`, `agentcore` CLI |

---

## Module 2: AgentCore Runtime (The Foundation)

| Topic | Content |
|-------|---------|
| 2.1 | The `@app.entrypoint` decorator pattern |
| 2.2 | Local development with Docker |
| 2.3 | `agentcore configure` and `agentcore launch` |
| 2.4 | Hosting MCP servers on Runtime |
| 2.5 | Agent-to-Agent (A2A) communication |
| 2.6 | Bi-directional streaming |

---

## Module 3: AgentCore Gateway (Tool Management)

| Topic | Content |
|-------|---------|
| 3.1 | Gateway concepts: Targets, MCP transport |
| 3.2 | Lambda → MCP tool conversion |
| 3.3 | OpenAPI/Smithy → MCP tool conversion |
| 3.4 | Semantic tool search (reducing context) |
| 3.5 | Bearer token injection & header propagation |
| 3.6 | Fine-grained access control & data masking |

---

## Module 4: AgentCore Identity (Security)

| Topic | Content |
|-------|---------|
| 4.1 | Inbound vs Outbound authentication |
| 4.2 | OAuth 2-legged (client credentials) flow |
| 4.3 | OAuth 3-legged (authorization code) flow |
| 4.4 | Integration with Cognito, Okta, EntraID |
| 4.5 | Zero-trust security model |
| 4.6 | Delegation vs impersonation patterns |

---

## Module 5: AgentCore Memory (State Management)

| Topic | Content |
|-------|---------|
| 5.1 | Short-term memory: Session context |
| 5.2 | Long-term memory: Cross-conversation persistence |
| 5.3 | Memory strategies: Semantic, Summary, Preferences, Custom |
| 5.4 | Memory branching for multi-turn conversations |
| 5.5 | Memory security patterns |
| 5.6 | Integration with Strands hooks and tools |

---

## Module 6: AgentCore Tools (Built-in Capabilities)

| Topic | Content |
|-------|---------|
| 6.1 | Code Interpreter: Secure sandboxed code execution |
| 6.2 | Browser Tool: Automated web navigation |
| 6.3 | S3 integration for large files |
| 6.4 | Multi-language runtime support |

---

## Module 7: AgentCore Observability (Monitoring)

| Topic | Content |
|-------|---------|
| 7.1 | OpenTelemetry integration |
| 7.2 | CloudWatch GenAI Observability dashboards |
| 7.3 | Custom span creation |
| 7.4 | Partner integrations: Langfuse, Arize, Braintrust |
| 7.5 | End-to-end tracing across services |

---

## Module 8: AgentCore Evaluations & Policy (Quality)

| Topic | Content |
|-------|---------|
| 8.1 | Built-in evaluators (13 metrics) |
| 8.2 | Custom evaluator creation |
| 8.3 | On-demand vs online evaluations |
| 8.4 | Natural language policy authoring |
| 8.5 | Fine-grained access control policies |

---

## Module 9: Framework Integrations

| Topic | Content |
|-------|---------|
| 9.1 | Strands Agents (AWS native) |
| 9.2 | LangGraph integration |
| 9.3 | CrewAI integration |
| 9.4 | LlamaIndex integration |
| 9.5 | OpenAI Agents SDK integration |
| 9.6 | PydanticAI integration |

---

## Module 10: Production Deployment

| Topic | Content |
|-------|---------|
| 10.1 | Infrastructure as Code: CloudFormation, CDK, Terraform |
| 10.2 | Multi-agent architectures |
| 10.3 | VPC integration & network security |
| 10.4 | Cost optimization strategies |
| 10.5 | Scaling patterns |

---

## Module 11: Capstone - End-to-End Application

| Topic | Content |
|-------|---------|
| 11.1 | Customer Support Agent: Full implementation |
| 11.2 | Lab progression: Prototype → Memory → Gateway → Runtime → Evals → Frontend |

---

## Topic Mapping (Special Interests)

| Interest Area | Primary Module | Secondary Coverage |
|--------------|----------------|-------------------|
| How agents decide which tools to use | Module 3.4 | Module 1.3 |
| Memory and context management | Module 5 | Module 11 |
| Custom tools/functions | Module 3.1-3.3 | Module 6 |
| Security (IAM, data privacy) | Module 4 | Module 3.6 |
| Cost optimization | Module 10.4 | Throughout |
| Error handling and retry | Module 2 | Module 7 |
| Observability and monitoring | Module 7 | Module 8 |
| Agent performance evaluation | Module 8 | Module 7 |
| AWS service integration | Modules 3, 4, 6, 10 | Throughout |
| Multi-agent orchestration | Module 2.5 | Module 9, 10.2 |
