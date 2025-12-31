# AgentCore Gateway - Reference

## Overview

Bedrock AgentCore Gateway provides a way to turn existing APIs and Lambda functions into fully-managed MCP servers without managing infrastructure or hosting. It provides a uniform Model Context Protocol (MCP) interface across all tools.

## Key Concepts

### Gateway
HTTP endpoint that customers call with an MCP client for executing standard MCP operations (`listTools`, `invokeTool`). Can also be invoked via AWS SDK (boto3).

### Gateway Target
Resource attached to a Gateway. Supported target types:
- **Lambda ARNs**: Direct Lambda function integration
- **API Specifications**: OpenAPI or Smithy models
- **MCP Servers**: Existing MCP servers as targets

### MCP Transport
Currently supports **Streamable HTTP connections** only.

## Architecture Flow

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Agent /   │────▶│  AgentCore      │────▶│  Target          │
│  MCP Client │     │  Gateway        │     │  (Lambda/API/MCP)│
└─────────────┘     └─────────────────┘     └──────────────────┘
       │                    │                        │
       │ OAuth Token        │ Validate &             │ Outbound
       │                    │ Authorize              │ Auth
       ▼                    ▼                        ▼
   Inbound Auth         Gateway Logic           External Resources
```

## Authentication Model

### Inbound Auth
Validates access for users/applications calling agents or tools:
- Analyzes OAuth token passed during invocation
- Decides allow/deny access to Gateway tools
- Complies with MCP authorization specification

### Outbound Auth
Enables access to external resources:
- API Key authentication
- IAM credentials
- OAuth access tokens
- Configured via Credentials Provider API

## Semantic Tool Search

Built-in capability to find relevant tools through natural language queries:
- Reduces context passed to agent for tool selection
- Uses vector embeddings for semantic matching
- Enabled during Gateway creation via `CreateGateway` API
- `CreateTarget` triggers automatic embedding generation

## Tutorial Structure (from repository)

```
02-AgentCore-gateway/
├── 01-transform-lambda-into-mcp-tools/
├── 02-transform-apis-into-mcp-tools/
├── 03-search-tools/
├── 04-integration/
├── 05-mcp-server-as-a-target/
├── 06-gateway-observability/
├── 07-bearer-token-injection/
├── 08-custom-header-propagation/
├── 09-fine-grained-access-control/
├── 10-sensitive-data-masking/
├── 11-api-gateway-as-a-target/
├── 12-agents-as-tools-using-mcp/
├── 12-outbound-auth-code-grant/
└── 14-token-exchange-at-request-interceptor/
```

## Benefits

- **No infrastructure management**: Fully managed service
- **Unified interface**: Single MCP protocol for all tools
- **Built-in authentication**: OAuth and credential management
- **Automatic scaling**: Based on demand
- **Enterprise security**: Encryption, access controls, audit logging
