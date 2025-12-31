# AgentCore Integrations - Reference

## Supported Agentic Frameworks

| Framework | Description | Integration Location |
|-----------|-------------|---------------------|
| **Strands Agents** | AWS native framework, best integration | `agentic-frameworks/strands-agents/` |
| **LangChain** | Chain-based workflows and tools | `agentic-frameworks/langchain/` |
| **LangGraph** | Multi-agent stateful workflows | `agentic-frameworks/langgraph/` |
| **CrewAI** | Collaborative AI agent orchestration | `agentic-frameworks/crewai/` |
| **LlamaIndex** | Document processing and RAG | `agentic-frameworks/llamaindex/` |
| **OpenAI Agents** | OpenAI Assistant API integration | `agentic-frameworks/openai-agents/` |
| **PydanticAI** | Type-safe agent development | `agentic-frameworks/pydanticai-agents/` |
| **AutoGen** | Multi-agent conversations | `agentic-frameworks/autogen/` |
| **ADK** | Agent Development Kit (Google) | `agentic-frameworks/adk/` |
| **Claude Agent** | Anthropic Claude agents | `agentic-frameworks/claude-agent/` |
| **Mastra (TS)** | TypeScript agent framework | `agentic-frameworks/typescript_mastra/` |
| **Java ADK** | Java Agent Development Kit | `agentic-frameworks/java_adk/` |

## Identity Provider Integrations

| Provider | Type | Location |
|----------|------|----------|
| **Microsoft Entra ID** | 3LO outbound auth | `IDP-examples/EntraID/` |
| **Okta** | Inbound authentication | `IDP-examples/Okta/` |
| **Amazon Cognito** | Native AWS (in tutorials) | `03-AgentCore-identity/` |

## Observability Partner Integrations

| Partner | Description | Location |
|---------|-------------|----------|
| **Dynatrace** | APM integration | `observability/dynatrace/` |
| **Langfuse** | LLM observability | Runtime partner section |
| **Arize** | AI engineering platform | Runtime partner section |
| **Braintrust** | AI evaluation | Runtime partner section |
| **Instana** | Real-time APM | Runtime partner section |

## AWS Service Integrations

| Service | Integration Type | Location |
|---------|-----------------|----------|
| **SageMaker AI** | MLflow with Runtime | `amazon-sagemakerai/` |
| **Bedrock Agent** | Gateway integration | `bedrock-agent/` |
| **Lambda** | Tool targets | Gateway tutorials |
| **API Gateway** | Target configuration | Gateway tutorials |
| **CloudWatch** | Observability | Observability tutorials |
| **Cognito** | Authentication | Identity tutorials |

## Vector Store Integrations

Location: `vector-stores/`

Integrations with various vector databases for RAG patterns.

## UX Examples

| Example | Description | Location |
|---------|-------------|----------|
| **Streamlit Chat** | Interactive chat interface | `ux-examples/streamlit-chat/` |

## Integration Patterns Demonstrated

1. **Framework Adaptation**: Adapting existing frameworks to AgentCore
2. **Authentication Flow**: Various IdP integrations
3. **Monitoring Setup**: Connecting observability tools
4. **UI Integration**: Building user interfaces
5. **Service Composition**: Combining AWS services with AgentCore

## Repository Structure

```
03-integrations/
├── agentic-frameworks/
│   ├── strands-agents/
│   ├── langchain/
│   ├── langgraph/
│   ├── crewai/
│   ├── llamaindex/
│   ├── openai-agents/
│   ├── pydanticai-agents/
│   ├── autogen/
│   ├── adk/
│   ├── claude-agent/
│   ├── java_adk/
│   └── typescript_mastra/
├── IDP-examples/
│   ├── EntraID/
│   └── Okta/
├── amazon-sagemakerai/
├── bedrock-agent/
├── gateway/
├── nova/
├── observability/
├── observability-fullstack-examples/
├── ux-examples/
└── vector-stores/
```
