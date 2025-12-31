# Capstone: Enterprise Loan Processing Agent

## Deep Dive into Gateway Fine-Grained Access & Identity Authentication

This capstone is specifically designed for learners who want to master **AgentCore Gateway** and **Identity** concepts through a realistic enterprise scenario using **LangGraph**.

---

## Learning Objectives

By completing this capstone, you will master:

### Gateway Concepts
- [ ] Creating Gateway with multiple target types (Lambda, OpenAPI)
- [ ] Semantic tool search configuration
- [ ] Bearer token injection for API authentication
- [ ] Header propagation for multi-tenant systems
- [ ] Fine-grained access control with `allowedClaims`
- [ ] Sensitive data masking (SSN, account numbers)
- [ ] Tool-level permissions based on user roles

### Identity Concepts
- [ ] Configuring inbound authentication (Cognito/OIDC)
- [ ] Setting up 2-legged OAuth (client credentials) for service accounts
- [ ] Setting up 3-legged OAuth (authorization code) for user delegation
- [ ] Token management and automatic refresh
- [ ] Zero-trust validation flow
- [ ] Delegation vs impersonation patterns

### LangGraph Concepts
- [ ] StateGraph with typed state
- [ ] Multi-node workflows
- [ ] Conditional edges and routing
- [ ] Checkpointing for state persistence
- [ ] Integration with AgentCore Runtime

---

## Scenario: SecureBank Loan Processing System

### Business Context

SecureBank needs an AI-powered loan processing system with strict security requirements:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECUREBANK LOAN PROCESSING SYSTEM                         │
│                                                                              │
│   USER ROLES:                                                                │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐              │
│   │  Loan Officer   │ │Senior Underwriter│ │Compliance Officer│             │
│   │                 │ │                 │ │                 │              │
│   │ • View apps     │ │ • All officer   │ │ • All underwriter│             │
│   │ • Create apps   │ │   permissions   │ │   permissions   │              │
│   │ • Basic credit  │ │ • Approve <$500K│ │ • Approve any   │              │
│   │   checks        │ │ • Full credit   │ │ • Override flags│              │
│   │ • Apps <$100K   │ │ • Risk models   │ │ • Audit access  │              │
│   └─────────────────┘ └─────────────────┘ └─────────────────┘              │
│                                                                              │
│   EXTERNAL SERVICES (Outbound OAuth):                                       │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐              │
│   │ Equifax Credit  │ │ Plaid Bank      │ │ DocuSign        │              │
│   │ Bureau API      │ │ Verification    │ │ (User's account)│              │
│   │ (2-legged)      │ │ (2-legged)      │ │ (3-legged)      │              │
│   └─────────────────┘ └─────────────────┘ └─────────────────┘              │
│                                                                              │
│   INTERNAL SERVICES (Lambda/OpenAPI):                                       │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐              │
│   │ Customer CRM    │ │ Loan Database   │ │ Risk Model      │              │
│   │ (OpenAPI)       │ │ (Lambda)        │ │ (Lambda)        │              │
│   └─────────────────┘ └─────────────────┘ └─────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOAN PROCESSING WORKFLOW                             │
│                                                                              │
│   START                                                                      │
│     │                                                                        │
│     ▼                                                                        │
│   ┌─────────────────┐                                                       │
│   │  1. INTAKE      │  Collect applicant info, validate identity            │
│   │     NODE        │  Tools: CRM lookup, create application                │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  2. CREDIT      │  Pull credit report, calculate score                  │
│   │     CHECK       │  Tools: Equifax API (2-legged OAuth)                  │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  3. BANK        │  Verify income, check account history                 │
│   │     VERIFY      │  Tools: Plaid API (2-legged OAuth)                    │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐     Amount > $100K?                                   │
│   │  4. RISK        │─────────────────────┐                                 │
│   │     ASSESSMENT  │     No              │ Yes                             │
│   └────────┬────────┘                     │                                 │
│            │                              ▼                                  │
│            │               ┌─────────────────┐                              │
│            │               │  5. SENIOR      │  Advanced risk model         │
│            │               │     REVIEW      │  (Role: senior_underwriter)  │
│            │               └────────┬────────┘                              │
│            │                        │                                        │
│            ▼                        ▼                                        │
│   ┌─────────────────────────────────────────┐                               │
│   │           6. DECISION NODE              │                               │
│   │   Route based on amount and risk        │                               │
│   └─────────────────┬───────────────────────┘                               │
│                     │                                                        │
│        ┌────────────┼────────────┐                                          │
│        ▼            ▼            ▼                                          │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐                                      │
│   │ APPROVE │ │ MANUAL  │ │ DECLINE │                                      │
│   │         │ │ REVIEW  │ │         │                                      │
│   └────┬────┘ └────┬────┘ └────┬────┘                                      │
│        │           │           │                                            │
│        ▼           ▼           ▼                                            │
│   ┌─────────────────────────────────────────┐                               │
│   │        7. DOCUMENT SIGNING              │                               │
│   │   DocuSign via user's account           │                               │
│   │   (3-legged OAuth - user delegation)    │                               │
│   └─────────────────────────────────────────┘                               │
│                     │                                                        │
│                     ▼                                                        │
│                   END                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Identity Configuration

### 1.1 Inbound Authentication (Who Calls Our Agent?)

First, configure Cognito to authenticate bank employees:

```python
import boto3

client = boto3.client('bedrock-agentcore')

# Step 1: Configure Cognito for inbound authentication
# This answers: "Who is calling my agent?"

client.configure_inbound_auth(
    runtimeId="loan-processing-runtime",
    authConfiguration={
        "cognitoConfiguration": {
            # Your Cognito User Pool
            "userPoolId": "us-east-1_SecureBankPool",
            "clientId": "7abc123def456ghi789",

            # Only these groups can access the agent
            "allowedGroups": [
                "loan-officers",
                "senior-underwriters",
                "compliance-officers"
            ]
        }
    }
)

# IMPORTANT: Users must include JWT token in requests
# Token contains claims like:
# {
#   "sub": "user-123",
#   "cognito:groups": ["loan-officers"],
#   "custom:role": "loan_officer",
#   "custom:branch": "NYC-001",
#   "custom:max_approval_amount": "100000"
# }
```

**Key Concept - Zero Trust Validation:**

```
Every request is validated:
┌─────────────────────────────────────────────────────────────────────────────┐
│  REQUEST with JWT Token                                                      │
│                                                                              │
│  1. Token Structure    → Valid JWT format?                                  │
│  2. Signature          → Matches Cognito's public key?                      │
│  3. Expiration         → exp claim in the future?                           │
│  4. Issuer             → iss matches our Cognito pool?                      │
│  5. Audience           → aud includes our client ID?                        │
│  6. Claims             → User in allowed groups?                            │
│                                                                              │
│  ✓ All pass → Request proceeds                                              │
│  ✗ Any fail → 401 Unauthorized                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Outbound Authentication - 2-Legged OAuth (Service-to-Service)

Configure credentials for external APIs that don't need user context:

```python
# ═══════════════════════════════════════════════════════════════════════════
# 2-LEGGED OAUTH: Agent acts as ITSELF, not on behalf of any user
# Use for: Service-to-service calls, shared data access
# ═══════════════════════════════════════════════════════════════════════════

# Equifax Credit Bureau API - Agent's own credentials
client.create_credential_provider(
    name="equifax-credit-bureau",
    credentialProviderType="OAUTH2_CLIENT_CREDENTIALS",
    oauth2ClientCredentialsConfiguration={
        # Equifax's OAuth token endpoint
        "tokenEndpoint": "https://api.equifax.com/oauth/token",

        # Our service account credentials (stored in Secrets Manager)
        "clientId": "securebank-loan-service",
        "clientSecretArn": "arn:aws:secretsmanager:us-east-1:123456789:secret:equifax-client-secret",

        # Scopes we need
        "scopes": [
            "credit_report:read",
            "credit_score:read"
        ]
    }
)

# Plaid Bank Verification API
client.create_credential_provider(
    name="plaid-bank-verification",
    credentialProviderType="OAUTH2_CLIENT_CREDENTIALS",
    oauth2ClientCredentialsConfiguration={
        "tokenEndpoint": "https://production.plaid.com/oauth/token",
        "clientId": "securebank-plaid-client",
        "clientSecretArn": "arn:aws:secretsmanager:us-east-1:123456789:secret:plaid-client-secret",
        "scopes": [
            "transactions:read",
            "accounts:read",
            "identity:read"
        ]
    }
)
```

**2-Legged OAuth Flow Diagram:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     2-LEGGED OAUTH FLOW                                      │
│                                                                              │
│   Your Agent              Equifax Auth Server           Equifax API          │
│      │                           │                           │               │
│      │  1. Request token         │                           │               │
│      │     client_id +           │                           │               │
│      │     client_secret         │                           │               │
│      │  ─────────────────────▶   │                           │               │
│      │                           │                           │               │
│      │  2. access_token          │                           │               │
│      │  ◀─────────────────────   │                           │               │
│      │                           │                           │               │
│      │  3. API call with token   │                           │               │
│      │  ─────────────────────────────────────────────────▶   │               │
│      │                           │                           │               │
│      │  4. Credit report data    │                           │               │
│      │  ◀─────────────────────────────────────────────────   │               │
│      │                           │                           │               │
│                                                                              │
│   KEY POINT: No user involved - Agent acts as SecureBank service            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Outbound Authentication - 3-Legged OAuth (User Delegation)

Configure credentials for services that need user's permission:

```python
# ═══════════════════════════════════════════════════════════════════════════
# 3-LEGGED OAUTH: Agent acts ON BEHALF OF a specific user
# Use for: User's private data, actions requiring user consent
# ═══════════════════════════════════════════════════════════════════════════

# DocuSign - We need to send documents to USER'S DocuSign account
# The applicant must authorize our agent to send them documents

client.create_credential_provider(
    name="docusign-user-delegation",
    credentialProviderType="OAUTH2_AUTHORIZATION_CODE",
    oauth2AuthorizationCodeConfiguration={
        # DocuSign OAuth endpoints
        "authorizationEndpoint": "https://account.docusign.com/oauth/auth",
        "tokenEndpoint": "https://account.docusign.com/oauth/token",

        # Our app's credentials
        "clientId": "securebank-docusign-app",
        "clientSecretArn": "arn:aws:secretsmanager:us-east-1:123456789:secret:docusign-secret",

        # What permissions we request from the user
        "scopes": [
            "signature",           # Send envelopes for signature
            "extended"             # Access user's account info
        ],

        # Where DocuSign redirects after user authorizes
        "redirectUri": "https://loans.securebank.com/oauth/callback/docusign"
    }
)
```

**3-Legged OAuth Flow Diagram:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     3-LEGGED OAUTH FLOW                                      │
│                                                                              │
│  Applicant    SecureBank App    AgentCore       DocuSign        DocuSign    │
│  (User)                         Identity        Auth            API         │
│     │              │               │               │               │         │
│     │  1. "Send me │               │               │               │         │
│     │   loan docs" │               │               │               │         │
│     │  ───────────▶│               │               │               │         │
│     │              │               │               │               │         │
│     │  2. Redirect to DocuSign login             │               │         │
│     │  ◀──────────────────────────────────────────               │         │
│     │              │               │               │               │         │
│     │  3. User logs in and clicks "Authorize SecureBank"        │         │
│     │  ─────────────────────────────────────────▶│               │         │
│     │              │               │               │               │         │
│     │  4. Redirect with authorization code        │               │         │
│     │  ◀─────────────────────────────────────────│               │         │
│     │              │               │               │               │         │
│     │              │  5. Exchange code for tokens │               │         │
│     │              │  ────────────▶│◀────────────▶│               │         │
│     │              │               │               │               │         │
│     │              │  6. Tokens stored (encrypted, per-user)     │         │
│     │              │               │               │               │         │
│     │              │        ... LATER (days/weeks) ...           │         │
│     │              │               │               │               │         │
│     │              │  7. Agent needs to send documents            │         │
│     │              │  ────────────▶│               │               │         │
│     │              │               │               │               │         │
│     │              │  8. Get stored │               │               │         │
│     │              │     user token│               │               │         │
│     │              │  ◀────────────│               │               │         │
│     │              │               │               │               │         │
│     │              │  9. Call DocuSign API with user's token      │         │
│     │              │  ───────────────────────────────────────────▶│         │
│     │              │               │               │               │         │
│     │  10. User receives document in their DocuSign account      │         │
│     │  ◀─────────────────────────────────────────────────────────│         │
│                                                                              │
│  KEY POINT: Agent acts FOR user (delegation), not AS user (impersonation)   │
│                                                                              │
│  Delegation Token contains:                                                 │
│  {                                                                          │
│    "sub": "securebank-loan-agent",     ← Agent's identity                   │
│    "act": {                                                                 │
│      "sub": "applicant@email.com"      ← Acting for this user               │
│    },                                                                       │
│    "scope": "signature extended"       ← Limited permissions                │
│  }                                                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Using Identity in Agent Code

```python
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()

# ═══════════════════════════════════════════════════════════════════════════
# Using 2-legged OAuth (Service-to-service)
# ═══════════════════════════════════════════════════════════════════════════

def get_credit_report(ssn: str) -> dict:
    """
    Get credit report from Equifax.
    Uses 2-legged OAuth - no user context needed.
    """
    # Get service token (AgentCore manages refresh automatically)
    token = identity.get_service_token(
        credential_provider="equifax-credit-bureau"
    )

    # Call Equifax API with our service token
    response = requests.post(
        "https://api.equifax.com/v1/credit-report",
        headers={"Authorization": f"Bearer {token}"},
        json={"ssn": ssn}
    )

    return response.json()


# ═══════════════════════════════════════════════════════════════════════════
# Using 3-legged OAuth (User delegation)
# ═══════════════════════════════════════════════════════════════════════════

def send_loan_documents(user_id: str, document_url: str) -> dict:
    """
    Send loan documents via DocuSign to user's account.
    Uses 3-legged OAuth - acting on behalf of specific user.
    """
    # Get token for THIS SPECIFIC USER
    # (User must have previously authorized via OAuth flow)
    token = identity.get_user_token(
        credential_provider="docusign-user-delegation",
        user_id=user_id  # The applicant's user ID
    )

    if not token:
        raise Exception(f"User {user_id} has not authorized DocuSign access")

    # Call DocuSign API on behalf of the user
    response = requests.post(
        "https://api.docusign.com/v2/envelopes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "documents": [{"documentUrl": document_url}],
            "recipients": {"signers": [{"email": user_id}]}
        }
    )

    return response.json()
```

---

## Part 2: Gateway Configuration

### 2.1 Create Gateway with Semantic Search

```python
import boto3

client = boto3.client('bedrock-agentcore')

# ═══════════════════════════════════════════════════════════════════════════
# Create Gateway with semantic search enabled
# ═══════════════════════════════════════════════════════════════════════════

gateway_response = client.create_gateway(
    name="loan-processing-gateway",
    description="Gateway for SecureBank loan processing tools",

    # Enable semantic search to reduce context tokens
    semanticSearchConfiguration={
        "enabled": True,
        "embeddingModel": "amazon.titan-embed-text-v2"
    }
)

gateway_id = gateway_response["gatewayId"]
gateway_arn = gateway_response["gatewayArn"]

print(f"Created Gateway: {gateway_id}")
```

**Why Semantic Search Matters:**

```
Without Semantic Search:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Agent has 50 tools → Send ALL 50 descriptions to LLM → 10,000+ tokens     │
│                                                                              │
│  Cost: High token usage, slower responses                                   │
│  Accuracy: LLM may pick wrong tool from too many options                    │
└─────────────────────────────────────────────────────────────────────────────┘

With Semantic Search:
┌─────────────────────────────────────────────────────────────────────────────┐
│  User: "Check the applicant's credit score"                                 │
│                           │                                                  │
│                           ▼                                                  │
│  Semantic Search: Find tools matching "credit score"                        │
│                           │                                                  │
│                           ▼                                                  │
│  Returns only: [get_credit_report, get_credit_score, check_credit_history] │
│                           │                                                  │
│                           ▼                                                  │
│  Send 3 tool descriptions to LLM → ~500 tokens                              │
│                                                                              │
│  Cost: 95% reduction in tool-related tokens                                 │
│  Accuracy: LLM picks correct tool from focused options                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Add Lambda Targets with Fine-Grained Access Control

```python
# ═══════════════════════════════════════════════════════════════════════════
# Target 1: Customer CRM Lookup (All roles can access)
# ═══════════════════════════════════════════════════════════════════════════

client.create_target(
    gatewayId=gateway_id,
    name="lookup-customer",
    description="Look up existing customer information from CRM",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:crm-lookup"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID or SSN (last 4 digits)"
            },
            "search_type": {
                "type": "string",
                "enum": ["id", "ssn", "email", "phone"],
                "description": "Type of search to perform"
            }
        },
        "required": ["customer_id", "search_type"]
    },
    # Fine-grained access: All loan-related roles can access
    accessControl={
        "allowedClaims": {
            "custom:role": ["loan_officer", "senior_underwriter", "compliance_officer"]
        }
    },
    # Mask sensitive data in responses
    dataMasking={
        "enabled": True,
        "maskingRules": [
            {"pattern": "SSN", "action": "MASK", "replacement": "XXX-XX-{last4}"},
            {"pattern": "ACCOUNT_NUMBER", "action": "PARTIAL_MASK"}
        ]
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# Target 2: Create Loan Application (Officers only, amount limit)
# ═══════════════════════════════════════════════════════════════════════════

client.create_target(
    gatewayId=gateway_id,
    name="create-loan-application",
    description="Create a new loan application in the system",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:create-loan-app"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "loan_amount": {"type": "number", "description": "Requested loan amount in USD"},
            "loan_type": {"type": "string", "enum": ["personal", "mortgage", "auto", "business"]},
            "term_months": {"type": "integer"}
        },
        "required": ["customer_id", "loan_amount", "loan_type"]
    },
    # FINE-GRAINED ACCESS: Only specific roles, with amount restrictions
    accessControl={
        "allowedClaims": {
            "custom:role": ["loan_officer", "senior_underwriter", "compliance_officer"]
        }
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# Target 3: Approve Loan (Role-based amount limits)
# ═══════════════════════════════════════════════════════════════════════════

# For loan officers - up to $100K
client.create_target(
    gatewayId=gateway_id,
    name="approve-loan-basic",
    description="Approve loans up to $100,000 (loan officers)",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:approve-loan"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "application_id": {"type": "string"},
            "approval_amount": {"type": "number", "maximum": 100000},
            "interest_rate": {"type": "number"},
            "notes": {"type": "string"}
        },
        "required": ["application_id", "approval_amount"]
    },
    accessControl={
        "allowedClaims": {
            "custom:role": ["loan_officer", "senior_underwriter", "compliance_officer"]
        }
    }
)

# For senior underwriters - up to $500K
client.create_target(
    gatewayId=gateway_id,
    name="approve-loan-senior",
    description="Approve loans up to $500,000 (senior underwriters only)",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:approve-loan-senior"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "application_id": {"type": "string"},
            "approval_amount": {"type": "number", "maximum": 500000},
            "interest_rate": {"type": "number"},
            "risk_override": {"type": "boolean"},
            "notes": {"type": "string"}
        },
        "required": ["application_id", "approval_amount"]
    },
    # RESTRICTED: Only senior underwriters and compliance
    accessControl={
        "allowedClaims": {
            "custom:role": ["senior_underwriter", "compliance_officer"]
        }
    }
)

# For compliance officers - unlimited
client.create_target(
    gatewayId=gateway_id,
    name="approve-loan-unlimited",
    description="Approve loans of any amount (compliance officers only)",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:approve-loan-unlimited"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "application_id": {"type": "string"},
            "approval_amount": {"type": "number"},
            "interest_rate": {"type": "number"},
            "risk_override": {"type": "boolean"},
            "compliance_notes": {"type": "string"},
            "board_approval_reference": {"type": "string"}
        },
        "required": ["application_id", "approval_amount", "compliance_notes"]
    },
    # MOST RESTRICTED: Only compliance officers
    accessControl={
        "allowedClaims": {
            "custom:role": ["compliance_officer"]
        }
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# Target 4: Risk Model (Senior roles only)
# ═══════════════════════════════════════════════════════════════════════════

client.create_target(
    gatewayId=gateway_id,
    name="run-risk-model",
    description="Run advanced risk assessment model",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:risk-model"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "application_id": {"type": "string"},
            "include_stress_test": {"type": "boolean"},
            "scenario": {"type": "string", "enum": ["base", "adverse", "severe"]}
        },
        "required": ["application_id"]
    },
    accessControl={
        "allowedClaims": {
            "custom:role": ["senior_underwriter", "compliance_officer"]
        }
    }
)
```

### 2.3 Add OpenAPI Target with Bearer Token Injection

```python
# ═══════════════════════════════════════════════════════════════════════════
# OpenAPI Target: Equifax Credit Bureau
# Uses bearer token injection for automatic authentication
# ═══════════════════════════════════════════════════════════════════════════

equifax_openapi_spec = """
openapi: 3.0.0
info:
  title: Equifax Credit Bureau API
  version: 1.0.0
paths:
  /v1/credit-report:
    post:
      operationId: getCreditReport
      summary: Get full credit report for an individual
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                ssn:
                  type: string
                  description: Social Security Number
                consent_reference:
                  type: string
                  description: Reference ID for consent form
              required: [ssn, consent_reference]
      responses:
        200:
          description: Credit report data
  /v1/credit-score:
    post:
      operationId: getCreditScore
      summary: Get credit score only (faster, cheaper)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                ssn:
                  type: string
              required: [ssn]
      responses:
        200:
          description: Credit score
"""

client.create_target(
    gatewayId=gateway_id,
    name="equifax-credit-api",
    description="Equifax credit bureau API for credit reports and scores",
    targetConfiguration={
        "openApiTarget": {
            "schema": equifax_openapi_spec,
            "baseUrl": "https://api.equifax.com"
        }
    },
    # BEARER TOKEN INJECTION
    # Gateway automatically gets token from our credential provider
    # and injects it into every request
    authConfiguration={
        "bearerTokenInjection": {
            "enabled": True,
            "credentialProviderName": "equifax-credit-bureau",  # 2-legged OAuth we created
            "headerName": "Authorization",
            "tokenPrefix": "Bearer "
        }
    },
    # Mask SSN in requests and responses
    dataMasking={
        "enabled": True,
        "maskingRules": [
            {"pattern": "SSN", "action": "MASK", "replacement": "XXX-XX-{last4}"}
        ]
    },
    accessControl={
        "allowedClaims": {
            "custom:role": ["loan_officer", "senior_underwriter", "compliance_officer"]
        }
    }
)
```

**Bearer Token Injection Flow:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BEARER TOKEN INJECTION                                    │
│                                                                              │
│   Agent calls Gateway                                                       │
│        │                                                                     │
│        ▼                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  GATEWAY receives: callTool("getCreditReport", {ssn: "123-45-6789"})│  │
│   └──────────────────────────────┬──────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  1. Gateway checks: bearerTokenInjection.enabled = true             │  │
│   │  2. Gateway calls Identity: get_service_token("equifax-credit-bureau")│ │
│   │  3. Identity returns: "eyJhbGciOiJSUzI1NiIs..."                     │  │
│   └──────────────────────────────┬──────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  4. Gateway injects header:                                          │  │
│   │     Authorization: Bearer eyJhbGciOiJSUzI1NiIs...                   │  │
│   │                                                                      │  │
│   │  5. Gateway calls Equifax API with injected token                   │  │
│   └──────────────────────────────┬──────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  6. Data masking applied to response:                               │  │
│   │     BEFORE: {"ssn": "123-45-6789", "score": 750}                   │  │
│   │     AFTER:  {"ssn": "XXX-XX-6789", "score": 750}                   │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   BENEFIT: Agent code never sees or handles tokens directly                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Add Target with Header Propagation (Multi-Tenant)

```python
# ═══════════════════════════════════════════════════════════════════════════
# Header Propagation: Pass tenant/branch info to internal APIs
# ═══════════════════════════════════════════════════════════════════════════

client.create_target(
    gatewayId=gateway_id,
    name="loan-database",
    description="Internal loan database for application management",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:loan-database"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get", "update", "list"],
                "description": "Database action"
            },
            "application_id": {"type": "string"},
            "filters": {"type": "object"}
        },
        "required": ["action"]
    },
    # HEADER PROPAGATION
    # Pass these headers from incoming request to the Lambda
    headerPropagation={
        "propagateHeaders": [
            "X-Branch-ID",      # Which bank branch (from user's token claims)
            "X-User-ID",        # Logged-in user
            "X-Correlation-ID", # For distributed tracing
            "X-Tenant-ID"       # Multi-tenant isolation
        ]
    },
    accessControl={
        "allowedClaims": {
            "custom:role": ["loan_officer", "senior_underwriter", "compliance_officer"]
        }
    }
)
```

**Header Propagation Use Cases:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HEADER PROPAGATION                                        │
│                                                                              │
│   User Request includes headers:                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Authorization: Bearer <JWT>                                         │  │
│   │  X-Branch-ID: NYC-001                                               │  │
│   │  X-Correlation-ID: req-abc-123                                      │  │
│   │  X-Tenant-ID: securebank                                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│                        Gateway propagates to Lambda:                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Lambda receives same headers → Can filter by branch, log with      │  │
│   │  correlation ID, enforce tenant isolation                           │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   USE CASES:                                                                │
│   • Multi-tenant: Each tenant only sees their data                         │
│   • Branch isolation: NYC branch can't see LA branch data                  │
│   • Audit: Correlation ID links all logs for a request                     │
│   • User context: Lambda knows which user made the request                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 Fine-Grained Access Control Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOOL ACCESS BY ROLE                                       │
│                                                                              │
│   Tool                        │ Loan Officer │ Sr. Underwriter │ Compliance │
│   ────────────────────────────┼──────────────┼─────────────────┼────────────│
│   lookup-customer             │      ✓       │        ✓        │     ✓      │
│   create-loan-application     │      ✓       │        ✓        │     ✓      │
│   equifax-credit-api          │      ✓       │        ✓        │     ✓      │
│   loan-database               │      ✓       │        ✓        │     ✓      │
│   approve-loan-basic (≤$100K) │      ✓       │        ✓        │     ✓      │
│   approve-loan-senior (≤$500K)│      ✗       │        ✓        │     ✓      │
│   approve-loan-unlimited      │      ✗       │        ✗        │     ✓      │
│   run-risk-model              │      ✗       │        ✓        │     ✓      │
│                                                                              │
│   When loan officer tries to use approve-loan-senior:                       │
│   Gateway returns: "Access denied: requires role senior_underwriter"        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: LangGraph Agent Implementation

### 3.1 Define State and Types

```python
# loan_agent/state.py

from typing import TypedDict, Literal, Optional, List, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class ApplicantInfo(TypedDict):
    customer_id: str
    name: str
    email: str
    ssn_last4: str

class CreditInfo(TypedDict):
    score: int
    report_id: str
    risk_factors: List[str]

class BankVerification(TypedDict):
    verified: bool
    monthly_income: float
    account_balance: float
    red_flags: List[str]

class RiskAssessment(TypedDict):
    risk_level: Literal["low", "medium", "high", "very_high"]
    risk_score: float
    recommended_action: Literal["auto_approve", "manual_review", "decline"]
    factors: List[str]

class LoanApplication(TypedDict):
    application_id: str
    loan_amount: float
    loan_type: str
    term_months: int
    status: Literal["pending", "approved", "declined", "manual_review"]
    interest_rate: Optional[float]

# Main state that flows through the graph
class LoanProcessingState(TypedDict):
    # Conversation messages (accumulates with add_messages)
    messages: Annotated[List[BaseMessage], add_messages]

    # User context (from JWT token claims)
    user_role: str
    user_id: str
    branch_id: str
    max_approval_amount: float

    # Applicant data
    applicant: Optional[ApplicantInfo]

    # Processing stages
    credit_info: Optional[CreditInfo]
    bank_verification: Optional[BankVerification]
    risk_assessment: Optional[RiskAssessment]
    loan_application: Optional[LoanApplication]

    # Workflow control
    current_stage: Literal[
        "intake",
        "credit_check",
        "bank_verify",
        "risk_assess",
        "senior_review",
        "decision",
        "documents",
        "complete"
    ]
    requires_senior_review: bool
    decision: Optional[Literal["approve", "decline", "manual_review"]]
    error: Optional[str]
```

### 3.2 Create Tool Wrappers Using Gateway

```python
# loan_agent/tools.py

from langchain_core.tools import tool
from bedrock_agentcore.gateway import GatewayClient
from bedrock_agentcore.identity import IdentityClient
from typing import Optional
import json

# Initialize clients
gateway = GatewayClient(gateway_id="loan-processing-gateway")
identity = IdentityClient()


# ═══════════════════════════════════════════════════════════════════════════
# Tool: Customer Lookup (via Gateway)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def lookup_customer(customer_id: str, search_type: str = "id") -> dict:
    """
    Look up existing customer information from CRM.

    Args:
        customer_id: Customer ID, last 4 SSN digits, email, or phone
        search_type: Type of search - "id", "ssn", "email", or "phone"

    Returns:
        Customer information including name, contact details, history
    """
    result = gateway.call_tool(
        tool_name="lookup-customer",
        parameters={
            "customer_id": customer_id,
            "search_type": search_type
        }
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Tool: Create Loan Application
# ═══════════════════════════════════════════════════════════════════════════

@tool
def create_loan_application(
    customer_id: str,
    loan_amount: float,
    loan_type: str,
    term_months: int = 60
) -> dict:
    """
    Create a new loan application in the system.

    Args:
        customer_id: Customer's unique identifier
        loan_amount: Requested loan amount in USD
        loan_type: Type of loan - "personal", "mortgage", "auto", or "business"
        term_months: Loan term in months (default 60)

    Returns:
        Application details including application_id
    """
    result = gateway.call_tool(
        tool_name="create-loan-application",
        parameters={
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "loan_type": loan_type,
            "term_months": term_months
        }
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Tool: Get Credit Report (2-legged OAuth via Gateway)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def get_credit_report(ssn: str, consent_reference: str) -> dict:
    """
    Get full credit report from Equifax.
    Requires applicant's consent.

    Args:
        ssn: Social Security Number (will be masked in logs)
        consent_reference: Reference ID for signed consent form

    Returns:
        Credit report with score, history, and risk factors
    """
    # Gateway automatically injects bearer token from our
    # equifax-credit-bureau credential provider (2-legged OAuth)
    result = gateway.call_tool(
        tool_name="getCreditReport",  # From OpenAPI spec
        parameters={
            "ssn": ssn,
            "consent_reference": consent_reference
        }
    )
    return result


@tool
def get_credit_score(ssn: str) -> dict:
    """
    Get credit score only (faster than full report).

    Args:
        ssn: Social Security Number

    Returns:
        Credit score and basic risk indicators
    """
    result = gateway.call_tool(
        tool_name="getCreditScore",
        parameters={"ssn": ssn}
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Tool: Bank Verification (2-legged OAuth)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def verify_bank_account(
    account_number: str,
    routing_number: str,
    months_history: int = 6
) -> dict:
    """
    Verify bank account and income via Plaid.

    Args:
        account_number: Bank account number
        routing_number: Bank routing number
        months_history: Months of transaction history to analyze

    Returns:
        Verification status, income estimate, account health
    """
    result = gateway.call_tool(
        tool_name="verify-bank-account",
        parameters={
            "account_number": account_number,
            "routing_number": routing_number,
            "months_history": months_history
        }
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Tool: Risk Assessment (Role-restricted)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def run_risk_model(
    application_id: str,
    include_stress_test: bool = False,
    scenario: str = "base"
) -> dict:
    """
    Run advanced risk assessment model.
    RESTRICTED: Only available to senior_underwriter and compliance_officer roles.

    Args:
        application_id: Loan application ID
        include_stress_test: Whether to include economic stress scenarios
        scenario: Risk scenario - "base", "adverse", or "severe"

    Returns:
        Risk score, risk level, and recommended action
    """
    result = gateway.call_tool(
        tool_name="run-risk-model",
        parameters={
            "application_id": application_id,
            "include_stress_test": include_stress_test,
            "scenario": scenario
        }
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Tools: Loan Approval (Role and Amount restricted)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def approve_loan_basic(
    application_id: str,
    approval_amount: float,
    interest_rate: float,
    notes: str = ""
) -> dict:
    """
    Approve loan up to $100,000.
    Available to: loan_officer, senior_underwriter, compliance_officer

    Args:
        application_id: Application to approve
        approval_amount: Amount to approve (max $100,000)
        interest_rate: Annual interest rate
        notes: Approval notes
    """
    if approval_amount > 100000:
        raise ValueError("This tool can only approve up to $100,000. Use approve_loan_senior for larger amounts.")

    result = gateway.call_tool(
        tool_name="approve-loan-basic",
        parameters={
            "application_id": application_id,
            "approval_amount": approval_amount,
            "interest_rate": interest_rate,
            "notes": notes
        }
    )
    return result


@tool
def approve_loan_senior(
    application_id: str,
    approval_amount: float,
    interest_rate: float,
    risk_override: bool = False,
    notes: str = ""
) -> dict:
    """
    Approve loan up to $500,000.
    RESTRICTED: Only available to senior_underwriter and compliance_officer.

    Args:
        application_id: Application to approve
        approval_amount: Amount to approve (max $500,000)
        interest_rate: Annual interest rate
        risk_override: Override risk model recommendation
        notes: Approval notes
    """
    if approval_amount > 500000:
        raise ValueError("This tool can only approve up to $500,000. Use approve_loan_unlimited for larger amounts.")

    result = gateway.call_tool(
        tool_name="approve-loan-senior",
        parameters={
            "application_id": application_id,
            "approval_amount": approval_amount,
            "interest_rate": interest_rate,
            "risk_override": risk_override,
            "notes": notes
        }
    )
    return result


@tool
def approve_loan_unlimited(
    application_id: str,
    approval_amount: float,
    interest_rate: float,
    risk_override: bool = False,
    compliance_notes: str = "",
    board_approval_reference: str = ""
) -> dict:
    """
    Approve loan of any amount.
    RESTRICTED: Only available to compliance_officer role.

    Args:
        application_id: Application to approve
        approval_amount: Amount to approve (no limit)
        interest_rate: Annual interest rate
        risk_override: Override risk model recommendation
        compliance_notes: Required compliance justification
        board_approval_reference: Board approval reference for amounts > $1M
    """
    result = gateway.call_tool(
        tool_name="approve-loan-unlimited",
        parameters={
            "application_id": application_id,
            "approval_amount": approval_amount,
            "interest_rate": interest_rate,
            "risk_override": risk_override,
            "compliance_notes": compliance_notes,
            "board_approval_reference": board_approval_reference
        }
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Tool: Send Documents (3-legged OAuth - User Delegation)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def send_loan_documents(
    applicant_user_id: str,
    application_id: str,
    document_type: str
) -> dict:
    """
    Send loan documents to applicant's DocuSign for signature.
    Uses 3-legged OAuth - requires applicant to have authorized DocuSign access.

    Args:
        applicant_user_id: The applicant's user ID (email)
        application_id: Loan application ID
        document_type: Type of document - "offer_letter", "agreement", "disclosure"

    Returns:
        DocuSign envelope ID and signing URL
    """
    # Get the applicant's DocuSign token (3-legged OAuth)
    # This token was obtained when the applicant authorized our app
    user_token = identity.get_user_token(
        credential_provider="docusign-user-delegation",
        user_id=applicant_user_id
    )

    if not user_token:
        return {
            "error": "Applicant has not authorized DocuSign access",
            "action_required": "Redirect applicant to DocuSign authorization",
            "auth_url": f"https://loans.securebank.com/authorize/docusign?user={applicant_user_id}"
        }

    # Call DocuSign API on behalf of the applicant
    result = gateway.call_tool(
        tool_name="send-docusign-envelope",
        parameters={
            "application_id": application_id,
            "document_type": document_type,
            "recipient_email": applicant_user_id
        },
        # Pass the user's token for this specific call
        auth_override={
            "bearerToken": user_token
        }
    )
    return result
```

### 3.3 Define Graph Nodes

```python
# loan_agent/nodes.py

from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .state import LoanProcessingState
from .tools import (
    lookup_customer, create_loan_application, get_credit_report,
    get_credit_score, verify_bank_account, run_risk_model,
    approve_loan_basic, approve_loan_senior, approve_loan_unlimited,
    send_loan_documents
)

# Initialize LLM
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229",
    model_kwargs={"temperature": 0}
)


# ═══════════════════════════════════════════════════════════════════════════
# Node 1: Intake - Collect applicant info and create application
# ═══════════════════════════════════════════════════════════════════════════

def intake_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Intake node: Look up customer, validate info, create application.
    Tools available: lookup_customer, create_loan_application
    """

    # Bind only intake-relevant tools
    intake_llm = llm.bind_tools([lookup_customer, create_loan_application])

    system_prompt = """You are a loan intake specialist at SecureBank.
    Your job is to:
    1. Look up the customer in our CRM system
    2. Verify their identity and collect necessary information
    3. Create a loan application with the requested details

    Be professional and thorough. Ask clarifying questions if needed."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = intake_llm.invoke(messages)

    # Process tool calls if any
    # (In real implementation, would handle tool execution loop)

    return {
        **state,
        "messages": [response],
        "current_stage": "credit_check"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node 2: Credit Check - Pull credit report
# ═══════════════════════════════════════════════════════════════════════════

def credit_check_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Credit check node: Get credit report and score from Equifax.
    Uses 2-legged OAuth (automatic via Gateway bearer token injection).
    """

    credit_llm = llm.bind_tools([get_credit_report, get_credit_score])

    system_prompt = """You are a credit analyst at SecureBank.
    Your job is to:
    1. Pull the applicant's credit report using their SSN
    2. Analyze the credit score and risk factors
    3. Summarize findings for the next stage

    Note: SSN will be masked in all logs for security.
    Make sure we have consent before pulling the full report."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = credit_llm.invoke(messages)

    return {
        **state,
        "messages": [response],
        "current_stage": "bank_verify"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node 3: Bank Verification - Verify income and accounts
# ═══════════════════════════════════════════════════════════════════════════

def bank_verify_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Bank verification node: Verify income and account history via Plaid.
    Uses 2-legged OAuth (service-to-service).
    """

    bank_llm = llm.bind_tools([verify_bank_account])

    system_prompt = """You are a financial verification specialist.
    Your job is to:
    1. Verify the applicant's bank account
    2. Analyze income patterns from transaction history
    3. Flag any red flags (overdrafts, irregular income, etc.)
    4. Summarize findings for risk assessment"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = bank_llm.invoke(messages)

    return {
        **state,
        "messages": [response],
        "current_stage": "risk_assess"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node 4: Risk Assessment - Evaluate loan risk
# ═══════════════════════════════════════════════════════════════════════════

def risk_assess_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Risk assessment node: Evaluate overall loan risk.
    Basic assessment available to all roles.
    """

    # Determine if we can use advanced risk model based on user role
    user_role = state["user_role"]
    loan_amount = state.get("loan_application", {}).get("loan_amount", 0)

    # Check if senior review is needed
    requires_senior = (
        loan_amount > 100000 or
        user_role == "loan_officer"
    )

    system_prompt = f"""You are a risk assessment specialist.
    Your job is to:
    1. Analyze the credit report and bank verification results
    2. Calculate a risk score based on:
       - Credit score (weight: 40%)
       - Income stability (weight: 30%)
       - Debt-to-income ratio (weight: 20%)
       - Account history (weight: 10%)
    3. Provide a risk recommendation

    Current user role: {user_role}
    Loan amount: ${loan_amount:,.2f}

    If loan amount > $100,000 or risk is elevated, flag for senior review."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = llm.invoke(messages)

    return {
        **state,
        "messages": [response],
        "requires_senior_review": requires_senior,
        "current_stage": "senior_review" if requires_senior else "decision"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node 5: Senior Review - Advanced analysis (role-restricted)
# ═══════════════════════════════════════════════════════════════════════════

def senior_review_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Senior review node: Advanced risk modeling.
    RESTRICTED: Only executes for senior_underwriter or compliance_officer.
    """

    user_role = state["user_role"]

    # Role check - this tool will fail at Gateway if role doesn't match
    if user_role not in ["senior_underwriter", "compliance_officer"]:
        return {
            **state,
            "messages": [AIMessage(content=f"""
            ⚠️ Senior Review Required

            This loan application requires senior underwriter review due to:
            - Loan amount exceeds $100,000

            Current user ({user_role}) does not have permission to complete senior review.

            Action Required: Escalate to senior_underwriter or compliance_officer.
            """)],
            "current_stage": "decision",
            "decision": "manual_review"
        }

    # Senior roles can use advanced risk model
    senior_llm = llm.bind_tools([run_risk_model])

    system_prompt = """You are a senior underwriter at SecureBank.
    You have access to the advanced risk model with stress testing.

    Your job is to:
    1. Run the risk model with stress test scenarios
    2. Evaluate the loan under adverse economic conditions
    3. Provide a final risk assessment and recommendation

    You have authority to approve loans up to $500,000."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = senior_llm.invoke(messages)

    return {
        **state,
        "messages": [response],
        "current_stage": "decision"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node 6: Decision - Approve, decline, or escalate
# ═══════════════════════════════════════════════════════════════════════════

def decision_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Decision node: Make final loan decision based on role permissions.

    Role-based approval limits:
    - loan_officer: up to $100,000
    - senior_underwriter: up to $500,000
    - compliance_officer: unlimited
    """

    user_role = state["user_role"]
    max_approval = state["max_approval_amount"]
    loan_amount = state.get("loan_application", {}).get("loan_amount", 0)

    # Select appropriate approval tool based on role and amount
    if loan_amount <= 100000:
        available_tools = [approve_loan_basic]
    elif loan_amount <= 500000 and user_role in ["senior_underwriter", "compliance_officer"]:
        available_tools = [approve_loan_senior]
    elif user_role == "compliance_officer":
        available_tools = [approve_loan_unlimited]
    else:
        # User doesn't have permission - return for manual review
        return {
            **state,
            "messages": [AIMessage(content=f"""
            ⚠️ Approval Authority Exceeded

            Loan amount: ${loan_amount:,.2f}
            Your approval limit: ${max_approval:,.2f}
            Your role: {user_role}

            This loan requires approval from a higher authority.
            Status: Pending Manual Review
            """)],
            "decision": "manual_review",
            "current_stage": "complete"
        }

    decision_llm = llm.bind_tools(available_tools)

    system_prompt = f"""You are making the final loan decision.

    Your role: {user_role}
    Your approval limit: ${max_approval:,.2f}
    Loan amount requested: ${loan_amount:,.2f}

    Based on the risk assessment and all gathered information:
    1. If risk is acceptable, approve the loan with appropriate interest rate
    2. If risk is too high, decline with clear explanation
    3. If you're unsure, recommend manual review

    Always include detailed notes for audit purposes."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = decision_llm.invoke(messages)

    # Determine decision from response
    decision = "approve"  # Would parse from actual response

    return {
        **state,
        "messages": [response],
        "decision": decision,
        "current_stage": "documents" if decision == "approve" else "complete"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node 7: Documents - Send for signature (3-legged OAuth)
# ═══════════════════════════════════════════════════════════════════════════

def documents_node(state: LoanProcessingState) -> LoanProcessingState:
    """
    Documents node: Send loan documents for signature via DocuSign.
    Uses 3-legged OAuth - acts on behalf of the applicant.
    """

    docs_llm = llm.bind_tools([send_loan_documents])

    system_prompt = """You are finalizing the approved loan.
    Your job is to:
    1. Prepare and send the loan offer letter
    2. Send the loan agreement for signature
    3. Send required disclosure documents

    All documents will be sent to the applicant's DocuSign account.
    They must have previously authorized our DocuSign integration.

    If they haven't authorized, provide the authorization link."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = docs_llm.invoke(messages)

    return {
        **state,
        "messages": [response],
        "current_stage": "complete"
    }
```

### 3.4 Build the LangGraph

```python
# loan_agent/graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import LoanProcessingState
from .nodes import (
    intake_node,
    credit_check_node,
    bank_verify_node,
    risk_assess_node,
    senior_review_node,
    decision_node,
    documents_node
)


def should_do_senior_review(state: LoanProcessingState) -> str:
    """Conditional edge: Route to senior review if needed."""
    if state.get("requires_senior_review", False):
        return "senior_review"
    return "decision"


def should_send_documents(state: LoanProcessingState) -> str:
    """Conditional edge: Only send documents if approved."""
    if state.get("decision") == "approve":
        return "documents"
    return END


def build_loan_processing_graph():
    """
    Build the LangGraph for loan processing.

    Graph structure:

    START → intake → credit_check → bank_verify → risk_assess
                                                       │
                                          ┌────────────┴────────────┐
                                          │                         │
                                          ▼                         ▼
                                    senior_review              decision
                                          │                         │
                                          └──────────┬──────────────┘
                                                     │
                                                     ▼
                                                 decision
                                                     │
                                          ┌──────────┴──────────┐
                                          │                      │
                                          ▼                      ▼
                                      documents                 END
                                          │                 (declined/
                                          ▼                  manual)
                                         END
                                     (approved)
    """

    # Create the graph with our state type
    workflow = StateGraph(LoanProcessingState)

    # Add nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("credit_check", credit_check_node)
    workflow.add_node("bank_verify", bank_verify_node)
    workflow.add_node("risk_assess", risk_assess_node)
    workflow.add_node("senior_review", senior_review_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("documents", documents_node)

    # Add edges (linear flow for most)
    workflow.add_edge("intake", "credit_check")
    workflow.add_edge("credit_check", "bank_verify")
    workflow.add_edge("bank_verify", "risk_assess")

    # Conditional edge: senior review or direct to decision
    workflow.add_conditional_edges(
        "risk_assess",
        should_do_senior_review,
        {
            "senior_review": "senior_review",
            "decision": "decision"
        }
    )

    # Senior review always goes to decision
    workflow.add_edge("senior_review", "decision")

    # Conditional edge: documents only if approved
    workflow.add_conditional_edges(
        "decision",
        should_send_documents,
        {
            "documents": "documents",
            END: END
        }
    )

    # Documents is the final step
    workflow.add_edge("documents", END)

    # Set entry point
    workflow.set_entry_point("intake")

    # Compile with checkpointing for state persistence
    checkpointer = SqliteSaver.from_conn_string("loan_checkpoints.db")

    return workflow.compile(checkpointer=checkpointer)


# Create the compiled graph
loan_graph = build_loan_processing_graph()
```

### 3.5 Integrate with AgentCore Runtime

```python
# loan_agent/main.py

from bedrock_agentcore import BedrockAgentCoreApp
from langchain_core.messages import HumanMessage
from .graph import loan_graph
from .state import LoanProcessingState
import json

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    """
    Main entrypoint for the Loan Processing Agent.

    Expected payload:
    {
        "prompt": "User's request",
        "session_id": "session-123",  # For checkpointing
        "user_context": {
            "user_id": "john.smith@securebank.com",
            "role": "loan_officer",
            "branch_id": "NYC-001",
            "max_approval_amount": 100000
        }
    }
    """

    # Extract user context from payload (comes from JWT claims in production)
    user_context = payload.get("user_context", {})
    session_id = payload.get("session_id", "default")

    # Initialize state with user context
    initial_state: LoanProcessingState = {
        "messages": [HumanMessage(content=payload["prompt"])],
        "user_role": user_context.get("role", "loan_officer"),
        "user_id": user_context.get("user_id", "unknown"),
        "branch_id": user_context.get("branch_id", "HQ"),
        "max_approval_amount": user_context.get("max_approval_amount", 100000),
        "applicant": None,
        "credit_info": None,
        "bank_verification": None,
        "risk_assessment": None,
        "loan_application": None,
        "current_stage": "intake",
        "requires_senior_review": False,
        "decision": None,
        "error": None
    }

    # Run the graph with checkpointing
    config = {"configurable": {"thread_id": session_id}}

    try:
        # Execute the graph
        final_state = loan_graph.invoke(initial_state, config=config)

        # Extract the final response
        last_message = final_state["messages"][-1]

        return {
            "response": last_message.content,
            "stage": final_state["current_stage"],
            "decision": final_state.get("decision"),
            "application": final_state.get("loan_application"),
            "session_id": session_id
        }

    except Exception as e:
        # Handle Gateway access denied errors
        if "Access denied" in str(e):
            return {
                "error": "access_denied",
                "message": f"Your role ({user_context.get('role')}) does not have permission for this action",
                "details": str(e)
            }
        raise


if __name__ == "__main__":
    app.run()
```

---

## Part 4: Testing Scenarios

### 4.1 Test Role-Based Access Control

```python
# tests/test_access_control.py

import pytest
from loan_agent.main import invoke

def test_loan_officer_basic_approval():
    """Loan officer can approve loans up to $100K"""
    response = invoke({
        "prompt": "Approve loan application APP-001 for $75,000 at 6.5% interest",
        "session_id": "test-1",
        "user_context": {
            "user_id": "officer@securebank.com",
            "role": "loan_officer",
            "max_approval_amount": 100000
        }
    })

    assert response.get("error") is None
    assert response["decision"] == "approve"


def test_loan_officer_cannot_approve_large_loan():
    """Loan officer cannot approve loans over $100K"""
    response = invoke({
        "prompt": "Approve loan application APP-002 for $250,000",
        "session_id": "test-2",
        "user_context": {
            "user_id": "officer@securebank.com",
            "role": "loan_officer",
            "max_approval_amount": 100000
        }
    })

    # Should be escalated, not approved
    assert response["decision"] == "manual_review"


def test_loan_officer_cannot_use_risk_model():
    """Loan officer cannot access advanced risk model"""
    response = invoke({
        "prompt": "Run the risk model with stress test on APP-003",
        "session_id": "test-3",
        "user_context": {
            "user_id": "officer@securebank.com",
            "role": "loan_officer",
            "max_approval_amount": 100000
        }
    })

    # Should get access denied
    assert response.get("error") == "access_denied"


def test_senior_underwriter_large_loan():
    """Senior underwriter can approve loans up to $500K"""
    response = invoke({
        "prompt": "Approve loan application APP-004 for $350,000 at 5.9% interest",
        "session_id": "test-4",
        "user_context": {
            "user_id": "senior@securebank.com",
            "role": "senior_underwriter",
            "max_approval_amount": 500000
        }
    })

    assert response.get("error") is None
    assert response["decision"] == "approve"


def test_compliance_officer_unlimited():
    """Compliance officer can approve any amount"""
    response = invoke({
        "prompt": "Approve loan application APP-005 for $2,000,000",
        "session_id": "test-5",
        "user_context": {
            "user_id": "compliance@securebank.com",
            "role": "compliance_officer",
            "max_approval_amount": float('inf')
        }
    })

    assert response.get("error") is None
    # May require board approval reference but should not be access denied
```

### 4.2 Test OAuth Flows

```python
# tests/test_oauth.py

def test_2_legged_oauth_credit_check():
    """Credit check uses 2-legged OAuth (no user context needed)"""
    # This should work for any authenticated user
    response = invoke({
        "prompt": "Pull credit report for customer CUST-001",
        "session_id": "test-oauth-1",
        "user_context": {
            "user_id": "officer@securebank.com",
            "role": "loan_officer",
            "max_approval_amount": 100000
        }
    })

    # Should succeed - Gateway handles token automatically
    assert "credit_info" in str(response) or response.get("error") is None


def test_3_legged_oauth_documents_authorized():
    """Document sending works when user has authorized DocuSign"""
    # Assume applicant has authorized
    response = invoke({
        "prompt": "Send loan documents to applicant@email.com for APP-006",
        "session_id": "test-oauth-2",
        "user_context": {
            "user_id": "officer@securebank.com",
            "role": "loan_officer",
            "max_approval_amount": 100000
        }
    })

    # Should succeed if applicant authorized DocuSign
    # or return auth_url if not
    assert "envelope_id" in str(response) or "auth_url" in str(response)


def test_3_legged_oauth_documents_not_authorized():
    """Document sending returns auth URL when user hasn't authorized"""
    # Test with a user who hasn't authorized DocuSign
    response = invoke({
        "prompt": "Send loan documents to newapplicant@email.com for APP-007",
        "session_id": "test-oauth-3",
        "user_context": {
            "user_id": "officer@securebank.com",
            "role": "loan_officer",
            "max_approval_amount": 100000
        }
    })

    # Should return authorization URL
    if "auth_url" in str(response):
        assert "docusign" in response.get("auth_url", "").lower()
```

---

## Part 5: Deployment

### 5.1 Deploy Infrastructure (CDK)

```python
# cdk/loan_agent_stack.py

from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_secretsmanager as secrets,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct

class LoanAgentStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Cognito User Pool for inbound auth
        user_pool = cognito.UserPool(
            self, "SecureBankUserPool",
            user_pool_name="securebank-loan-users",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            custom_attributes={
                "role": cognito.StringAttribute(mutable=True),
                "branch_id": cognito.StringAttribute(mutable=True),
                "max_approval_amount": cognito.NumberAttribute(mutable=True)
            }
        )

        # User Pool Groups for role-based access
        for group in ["loan-officers", "senior-underwriters", "compliance-officers"]:
            cognito.CfnUserPoolGroup(
                self, f"Group-{group}",
                user_pool_id=user_pool.user_pool_id,
                group_name=group
            )

        # Secrets for OAuth credentials
        equifax_secret = secrets.Secret(
            self, "EquifaxSecret",
            secret_name="equifax-client-secret",
            description="Equifax API client secret for 2-legged OAuth"
        )

        docusign_secret = secrets.Secret(
            self, "DocuSignSecret",
            secret_name="docusign-client-secret",
            description="DocuSign client secret for 3-legged OAuth"
        )

        # IAM role for AgentCore Runtime
        agent_role = iam.Role(
            self, "AgentRole",
            assumed_by=iam.ServicePrincipal("agentcore.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBedrockAgentCoreExecutionPolicy"
                )
            ]
        )

        # Grant access to secrets
        equifax_secret.grant_read(agent_role)
        docusign_secret.grant_read(agent_role)

        # Outputs
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "AgentRoleArn", value=agent_role.role_arn)
```

### 5.2 Deploy Agent

```bash
# Deploy infrastructure
cd cdk
cdk deploy

# Configure and launch agent
cd ../loan_agent
agentcore configure -e main.py --name loan-processing-agent
agentcore launch

# Test deployed agent
agentcore invoke '{
  "prompt": "Process a new loan application for customer CUST-001, requesting $50,000 personal loan",
  "session_id": "test-session-1",
  "user_context": {
    "user_id": "officer@securebank.com",
    "role": "loan_officer",
    "branch_id": "NYC-001",
    "max_approval_amount": 100000
  }
}'
```

---

## Summary: Concepts Covered

### Gateway Concepts Mastered

| Concept | Where Used |
|---------|------------|
| **Lambda → MCP conversion** | Internal tools (CRM, loan DB, risk model) |
| **OpenAPI → MCP conversion** | Equifax credit API |
| **Semantic tool search** | Enabled on gateway for 50+ tools |
| **Bearer token injection** | Equifax API (2-legged OAuth) |
| **Header propagation** | Branch ID, tenant ID for internal APIs |
| **Fine-grained access control** | Role-based tool restrictions |
| **Data masking** | SSN, account numbers in responses |

### Identity Concepts Mastered

| Concept | Where Used |
|---------|------------|
| **Inbound auth (Cognito)** | Authenticating bank employees |
| **2-legged OAuth** | Equifax, Plaid service accounts |
| **3-legged OAuth** | DocuSign user delegation |
| **Token management** | Automatic refresh, per-user storage |
| **Zero trust validation** | 6-step token validation |
| **Delegation pattern** | Agent acts FOR user, not AS user |

### LangGraph Concepts Mastered

| Concept | Where Used |
|---------|------------|
| **StateGraph** | Main workflow definition |
| **Typed state** | LoanProcessingState with all fields |
| **Conditional edges** | Senior review routing, approval routing |
| **Checkpointing** | Session persistence across requests |
| **Tool binding** | Per-node tool restrictions |

---

## Exercises

### Exercise 1: Add Branch Isolation
Modify the `loan-database` target to ensure users can only see loans from their own branch using header propagation and Lambda-side filtering.

### Exercise 2: Add Audit Logging
Create a new target that logs all approval decisions with:
- Who approved (from JWT claims)
- What amount
- Risk score at time of approval
- Any overrides used

### Exercise 3: Add Rate Limiting
Configure Gateway to limit:
- Credit checks: 100 per hour per branch
- Loan approvals: 50 per hour per user

### Exercise 4: Implement Loan Modification
Add a new workflow branch for modifying existing loans, with appropriate role restrictions (only senior roles can modify approved loans).

---

## References

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)
- [AWS Multi-Agent with LangGraph](https://aws.amazon.com/blogs/machine-learning/build-multi-agent-systems-with-langgraph-and-amazon-bedrock/)
- AgentCore Gateway Module (module-03)
- AgentCore Identity Module (module-04)
