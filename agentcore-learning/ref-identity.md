# AgentCore Identity - Reference

## Overview

Amazon Bedrock AgentCore Identity is a comprehensive identity and credential management service designed specifically for AI agents and automated workloads. It enables agents to securely access user-specific data across multiple services without compromising security.

**Core Principle**: Delegation rather than impersonation - agents authenticate as themselves while carrying verifiable user context.

## Key Features

- **Inbound Authentication**: Validate access for users/applications calling agents
- **Outbound Authentication**: Secure access from agents to external services on behalf of users
- **OAuth Integration**: Support for 2-legged and 3-legged OAuth flows
- **AWS IAM Integration**: Native integration with AWS identity management
- **Zero Trust Security**: Every request validated regardless of source
- **Cross-Platform Support**: AWS, other clouds, and on-premise

## Authentication Types

### Inbound Auth
Validates access for users calling agents or tools in Runtime or Gateway:

| Method | Description |
|--------|-------------|
| AWS IAM | Direct IAM-based access control |
| OAuth | Token-based auth without IAM for end users |

### Outbound Auth
Enables agents to access resources on behalf of users:

| Method | Description |
|--------|-------------|
| AWS Resources | IAM execution roles for AWS service access |
| 2-Legged OAuth | Client credentials flow (service-to-service) |
| 3-Legged OAuth | Authorization code flow (user delegation) |

## Workflow

```
1. User Authentication
   └── Users authenticate through existing IdP (Cognito, Auth0, Okta)

2. Agent Authorization
   └── Applications request agent access with user tokens

3. Token Exchange
   └── AgentCore Identity validates user tokens
   └── Issues workload access tokens

4. Resource Access
   └── Agents use workload tokens to access resources

5. Delegation & Audit
   └── All actions maintain user context and audit trails
```

## Tutorial Examples

| Example | Type | Description |
|---------|------|-------------|
| Inbound Auth | Inbound | User authentication with Strands agents |
| Outbound Auth | Outbound | Agent access to external services |
| 3-Legged OAuth | Outbound | User-delegated access with Cognito |
| GitHub Integration | Outbound | GitHub API via 3-legged OAuth |

## Supported Identity Providers

- Amazon Cognito
- Okta
- Microsoft Entra ID (Azure AD)
- Auth0
- Any OIDC-compliant provider

## Tutorial Structure (from repository)

```
03-AgentCore-identity/
├── 01-getting_started.md
├── 02-how_it_works.md
├── 03-Inbound Auth example/
├── 04-Outbound Auth example/
├── 05-Outbound_Auth_3lo/        # 3-legged OAuth
└── 06-Outbound_Auth_Github/
```

## Integration Points

- **AgentCore Runtime**: Authentication for hosted agents
- **AgentCore Gateway**: Secures access to tools and APIs
- **AgentCore Memory**: Secure access to user-specific memory
- **Third-Party Services**: External API integration
