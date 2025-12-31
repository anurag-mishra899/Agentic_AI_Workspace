# Module 3: AgentCore Gateway

## 3.1 Gateway Concepts: Targets and MCP Transport

### The Problem Gateway Solves

You have existing infrastructure — Lambda functions, REST APIs, databases. Your agent needs to use them as tools. Without Gateway:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE INTEGRATION NIGHTMARE                        │
│                                                                      │
│   Agent Code:                                                        │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  # For each API, you write custom integration:                │  │
│   │  def call_orders_api(order_id):                               │  │
│   │      response = requests.get(f"{ORDERS_URL}/{order_id}",      │  │
│   │                              headers={"Auth": get_token()})   │  │
│   │      return parse_orders_response(response)                   │  │
│   │                                                               │  │
│   │  def call_inventory_lambda(product_id):                       │  │
│   │      lambda_client.invoke(FunctionName="inventory",           │  │
│   │                           Payload=json.dumps({...}))          │  │
│   │      return parse_inventory_response(...)                     │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│   Problems:                                                          │
│   • N different integration patterns for N tools                     │
│   • Auth logic scattered everywhere                                  │
│   • Can't share tools across agents                                  │
│   • Tool descriptions duplicated in each agent                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Gateway Solution

```
┌─────────────────────────────────────────────────────────────────────┐
│                     WITH AGENTCORE GATEWAY                           │
│                                                                      │
│   Agent Code:                                                        │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  # One pattern for ALL tools:                                 │  │
│   │  from strands.mcp import MCPClient                            │  │
│   │                                                               │  │
│   │  gateway = MCPClient(gateway_id="my-gateway")                 │  │
│   │  agent = Agent(tools=gateway.get_tools())                     │  │
│   │                                                               │  │
│   │  # That's it. Agent can use orders, inventory, CRM, etc.     │  │
│   └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Gateway** | HTTP endpoint exposing tools via MCP protocol |
| **Target** | Resource attached to Gateway (Lambda, OpenAPI, Smithy) |
| **MCP Transport** | Streamable HTTP connection for client-gateway communication |

**MCP Operations:**
- `listTools` — discover available tools
- `callTool` — invoke a specific tool

---

## 3.2 Lambda → MCP Tool Conversion

### Creating Gateway with Lambda Target

```python
import boto3

client = boto3.client('bedrock-agentcore')

# Step 1: Create Gateway
gateway_response = client.create_gateway(
    name="orders-gateway",
    description="Gateway for order management tools"
)
gateway_id = gateway_response["gatewayId"]

# Step 2: Add Lambda as Target
client.create_target(
    gatewayId=gateway_id,
    name="get-order",
    description="Retrieve order details by order ID",
    targetConfiguration={
        "lambdaTarget": {
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789:function:get-order"
        }
    },
    toolSchema={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The unique order identifier"
            }
        },
        "required": ["order_id"]
    }
)
```

### Agent Using Gateway Tools

```python
from strands import Agent
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(gateway_id="orders-gateway")
tools = gateway.list_tools()
agent = Agent(tools=tools)

result = agent("What's the status of order ORD-123?")
```

---

## 3.3 OpenAPI/Smithy → MCP Tool Conversion

### OpenAPI Example

```python
# Read OpenAPI spec
with open('openapi.yaml', 'r') as f:
    api_spec = f.read()

# Create target from OpenAPI
client.create_target(
    gatewayId="my-gateway",
    name="inventory-api",
    description="Inventory management API",
    targetConfiguration={
        "openApiTarget": {
            "schema": api_spec,
            "baseUrl": "https://api.company.com/inventory"
        }
    }
)
```

Gateway automatically creates MCP tools for each OpenAPI operation.

---

## 3.4 Semantic Tool Search (Reducing Context)

### The Problem

```
Agent has 100 tools → Sending all descriptions wastes tokens

With semantic search:
Query: "check stock" → Returns only: getStock, checkInventory, productAvailability
```

### Enabling Semantic Search

```python
client.create_gateway(
    name="enterprise-gateway",
    semanticSearchConfiguration={
        "enabled": True,
        "embeddingModel": "amazon.titan-embed-text-v2"
    }
)
```

### Using Semantic Search

```python
gateway = GatewayClient(gateway_id="enterprise-gateway")

# Search for relevant tools instead of listing all
relevant_tools = gateway.search_tools(
    query="check product inventory stock levels",
    max_results=5
)

agent = Agent(tools=relevant_tools)
```

---

## 3.5 Bearer Token Injection & Header Propagation

### Bearer Token Injection

```python
client.create_target(
    gatewayId="my-gateway",
    name="user-data-api",
    targetConfiguration={
        "openApiTarget": {
            "schema": api_spec,
            "baseUrl": "https://api.company.com/userdata"
        }
    },
    authConfiguration={
        "bearerTokenInjection": {
            "enabled": True,
            "headerName": "Authorization",
            "tokenPrefix": "Bearer "
        }
    }
)
```

### Custom Header Propagation

```python
client.create_target(
    gatewayId="my-gateway",
    name="multi-tenant-api",
    targetConfiguration={"openApiTarget": {...}},
    headerPropagation={
        "propagateHeaders": [
            "X-Tenant-ID",
            "X-Correlation-ID"
        ]
    }
)
```

---

## 3.6 Fine-Grained Access Control & Data Masking

### Access Control

```python
client.create_target(
    gatewayId="my-gateway",
    name="admin-only-tool",
    targetConfiguration={...},
    accessControl={
        "allowedClaims": {
            "role": ["admin", "superuser"],
            "department": ["finance"]
        }
    }
)
```

### Sensitive Data Masking

```python
client.create_target(
    gatewayId="my-gateway",
    name="customer-lookup",
    targetConfiguration={...},
    dataMasking={
        "enabled": True,
        "maskingRules": [
            {"pattern": "SSN", "action": "MASK", "replacement": "XXX-XX-****"},
            {"pattern": "CREDIT_CARD", "action": "MASK", "replacement": "****-****-****-{last4}"},
            {"pattern": "EMAIL", "action": "PARTIAL_MASK"}
        ]
    }
)
```

**Before:** `{"ssn": "123-45-6789", "email": "john@example.com"}`
**After:** `{"ssn": "XXX-XX-****", "email": "j***@example.com"}`

---

## Module 3 Summary

### Key Points

1. **Gateway converts existing resources to MCP tools** — Lambda, REST APIs, Smithy models

2. **One integration pattern for all tools** — agents connect via standard MCP protocol

3. **Semantic search reduces context** — send only relevant tool descriptions to LLM

4. **Authentication flows through Gateway** — bearer token injection, header propagation

5. **Enterprise security built-in** — fine-grained access control, automatic PII masking

### Gateway Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        AGENTS                                 │
└──────────────────────┬───────────────────────────────────────┘
                       │ MCP Protocol
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   AGENTCORE GATEWAY                           │
│  • Semantic Search    • Access Control    • Data Masking     │
│  • Token Injection    • Header Propagation                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Lambda  │   │  REST   │   │ Smithy  │
   │Functions│   │  APIs   │   │  APIs   │
   └─────────┘   └─────────┘   └─────────┘
```

---

## Comprehension Check

1. What are the three types of targets Gateway supports?

2. How does semantic tool search help reduce costs and improve accuracy?

3. What's the difference between bearer token injection and header propagation?

4. How would you restrict a tool to only be usable by users with "admin" role?
