# Amazon Bedrock AgentCore - Learning Overview

## What is AgentCore?

Amazon Bedrock AgentCore is AWS's comprehensive, framework-agnostic infrastructure platform for deploying and operating AI agents at enterprise scale. Unlike point solutions, AgentCore provides a unified set of managed services that handle the "undifferentiated heavy lifting" of agent infrastructure.

## Repository Reference

- **Source**: https://github.com/awslabs/amazon-bedrock-agentcore-samples
- **Documentation**: https://docs.aws.amazon.com/bedrock-agentcore/
- **Python SDK**: https://github.com/aws/bedrock-agentcore-sdk-python
- **Starter Toolkit**: https://github.com/aws/bedrock-agentcore-starter-toolkit

## The 7 Core Services

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Your Agent Application                            │
│         (Strands / LangGraph / CrewAI / LlamaIndex / Custom)            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│    Runtime    │          │    Gateway    │          │    Memory     │
│  (Hosting &   │          │ (Tool→MCP     │          │ (Short & Long │
│   Scaling)    │          │  Conversion)  │          │    Term)      │
└───────────────┘          └───────────────┘          └───────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   Identity    │          │    Tools      │          │ Observability │
│ (Auth & IAM)  │          │(Code/Browser) │          │  (Tracing)    │
└───────────────┘          └───────────────┘          └───────────────┘
                                    │
                                    ▼
                          ┌───────────────┐
                          │  Evaluations  │
                          │  & Policy     │
                          └───────────────┘
```

### Service Summary

| Service | Purpose | Key Problem Solved |
|---------|---------|-------------------|
| **Runtime** | Serverless hosting for agents | Deploy any framework without managing infrastructure |
| **Gateway** | Convert APIs/Lambda to MCP tools | Unified tool interface without rewrites |
| **Identity** | Authentication & authorization | Secure agent access to user resources |
| **Memory** | Short & long-term persistence | Agents remember across conversations |
| **Tools** | Code Interpreter & Browser | Secure sandboxed execution environments |
| **Observability** | Tracing & monitoring | Debug and monitor agent behavior |
| **Evaluations** | Quality assessment | Measure and improve agent performance |

## Key Differentiators

1. **Framework Agnostic**: Works with Strands, LangGraph, CrewAI, LlamaIndex, or custom code
2. **Model Agnostic**: Use Bedrock models, OpenAI, or any LLM
3. **MCP Native**: Built around Model Context Protocol for tool standardization
4. **Enterprise Security**: Zero-trust, OAuth, IAM integration out of the box
5. **Fully Managed**: No infrastructure to maintain

## Prerequisites

```bash
# Core packages
pip install bedrock-agentcore strands-agents bedrock-agentcore-starter-toolkit

# AWS permissions needed (managed policies)
# - BedrockAgentCoreFullAccess
# - AmazonBedrockFullAccess
```

## Repository Structure

```
amazon-bedrock-agentcore-samples/
├── 01-tutorials/           # Learning fundamentals
│   ├── 01-AgentCore-runtime/
│   ├── 02-AgentCore-gateway/
│   ├── 03-AgentCore-identity/
│   ├── 04-AgentCore-memory/
│   ├── 05-AgentCore-tools/
│   ├── 06-AgentCore-observability/
│   ├── 07-AgentCore-evaluations/
│   ├── 08-AgentCore-policy/
│   └── 09-AgentCore-E2E/
├── 02-use-cases/           # Real-world applications
├── 03-integrations/        # Framework integrations
├── 04-infrastructure-as-code/  # CDK, CloudFormation, Terraform
└── 05-blueprints/          # Full-stack reference apps
```
