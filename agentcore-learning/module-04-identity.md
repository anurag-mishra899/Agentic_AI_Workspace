# Module 4: AgentCore Identity

## 4.1 Inbound vs Outbound Authentication

### The Two Authentication Directions

```
     USER                    AGENT                    EXTERNAL
    (Human)                (Your App)                 SERVICE

       │   INBOUND AUTH         │    OUTBOUND AUTH       │
       │   ─────────────▶       │    ─────────────▶      │
       │                        │                        │
       │  "Who is calling      │   "Agent accessing     │
       │   my agent?"          │    service on behalf   │
       │                        │    of user"            │
```

### Inbound Authentication

**Question answered:** "Who is calling my agent and are they allowed?"

**Supported methods:**
- **AWS IAM**: Direct IAM authentication (service-to-service)
- **OAuth/OIDC**: Token-based auth from any IdP (Cognito, Okta, etc.)

### Outbound Authentication

**Question answered:** "How does my agent access external services on behalf of the user?"

**Supported methods:**
- **API Key**: Static keys stored in AgentCore
- **IAM Role**: For AWS service access
- **OAuth 2-legged**: Client credentials (service accounts)
- **OAuth 3-legged**: User-delegated access (user authorizes agent)

---

## 4.2 OAuth 2-Legged (Client Credentials) Flow

**Use case:** Agent accesses a service using **its own identity**, not a user's.

### When to Use

- Service-to-service communication
- Accessing shared resources (not user-specific)
- Background jobs, batch processing

### Flow

```
Your Agent              Auth Server              External API
   │                         │                        │
   │  1. Request token       │                        │
   │     (client_id +        │                        │
   │      client_secret)     │                        │
   │  ───────────────────▶   │                        │
   │                         │                        │
   │  2. Return access_token │                        │
   │  ◀───────────────────   │                        │
   │                         │                        │
   │  3. Call API with token │                        │
   │  ───────────────────────────────────────────▶    │
   │                         │                        │
   │            No user involved - Agent acts as itself
```

### Configuration

```python
client.create_credential_provider(
    name="service-api-credentials",
    credentialProviderType="OAUTH2_CLIENT_CREDENTIALS",
    oauth2ClientCredentialsConfiguration={
        "tokenEndpoint": "https://auth.service.com/oauth/token",
        "clientId": "your-client-id",
        "clientSecretArn": "arn:aws:secretsmanager:...:secret:client-secret",
        "scopes": ["read:data", "write:data"]
    }
)
```

---

## 4.3 OAuth 3-Legged (Authorization Code) Flow

**Use case:** Agent accesses a service **on behalf of a specific user** with their permission.

### When to Use

- Accessing user's private data (Gmail, Slack, GitHub)
- Acting as the user (posting, sending emails)
- Any action requiring user consent

### Flow

```
User        Your App       AgentCore       Auth Server    External
 │             │           Identity        (Google)        API
 │             │              │               │             │
 │  1. "Connect my Google"   │               │             │
 │  ─────────▶ │              │               │             │
 │             │              │               │             │
 │  2. Redirect to Google login              │             │
 │  ◀─────────────────────────────────────────             │
 │             │              │               │             │
 │  3. User logs in & consents               │             │
 │  ─────────────────────────────────────────▶             │
 │             │              │               │             │
 │  4-6. Code exchanged, tokens stored       │             │
 │             │              │               │             │
 │        ... LATER ...                                    │
 │             │              │               │             │
 │             │  7-9. Agent retrieves token, calls API    │
 │             │  ─────────────────────────────────────────▶
```

### Key Insight: Token Storage

AgentCore Identity **stores and manages tokens**:
- Encrypted at rest
- Automatic refresh when expired
- Per-user token isolation

### Configuration

```python
client.create_credential_provider(
    name="google-user-credentials",
    credentialProviderType="OAUTH2_AUTHORIZATION_CODE",
    oauth2AuthorizationCodeConfiguration={
        "authorizationEndpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "tokenEndpoint": "https://oauth2.googleapis.com/token",
        "clientId": "your-google-client-id",
        "clientSecretArn": "arn:aws:secretsmanager:...:secret:google-secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        "redirectUri": "https://your-app.com/oauth/callback"
    }
)
```

### Usage

```python
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()

# Get token for specific user
token = identity.get_user_token(
    credential_provider="google-user-credentials",
    user_id="user-123"
)

# Use token to access API on behalf of user
response = requests.get(
    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
    headers={"Authorization": f"Bearer {token}"}
)
```

---

## 4.4 Integration with Cognito, Okta, EntraID

### Amazon Cognito

```python
client.configure_inbound_auth(
    runtimeId="my-runtime",
    authConfiguration={
        "cognitoConfiguration": {
            "userPoolId": "us-east-1_xxxxx",
            "clientId": "your-cognito-client-id",
            "allowedGroups": ["agents-users"]
        }
    }
)
```

### Okta

```python
client.configure_inbound_auth(
    runtimeId="my-runtime",
    authConfiguration={
        "oidcConfiguration": {
            "issuer": "https://your-domain.okta.com",
            "audience": "your-api-audience",
            "jwksUri": "https://your-domain.okta.com/oauth2/v1/keys"
        }
    }
)
```

### Microsoft Entra ID

```python
client.configure_inbound_auth(
    runtimeId="my-runtime",
    authConfiguration={
        "oidcConfiguration": {
            "issuer": "https://login.microsoftonline.com/{tenant-id}/v2.0",
            "audience": "your-application-id",
            "jwksUri": "https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys"
        }
    }
)
```

---

## 4.5 Zero-Trust Security Model

### Every Request is Verified

```
❌ Traditional: "Request came from internal network, trust it"

✓ Zero Trust: Every request must prove:
  • Valid token (not expired, not revoked)
  • Correct issuer (from expected IdP)
  • Valid signature (not tampered)
  • Sufficient claims (user has required roles)
  • Valid scope (token allows this action)
```

### Token Validation Steps

1. **Token Structure** — Valid JWT format?
2. **Signature Verification** — Matches IdP's public key?
3. **Expiration Check** — exp claim in the future?
4. **Issuer Validation** — iss claim matches configured IdP?
5. **Audience Validation** — aud claim includes our app?
6. **Claims Verification** — User has required roles/groups?

---

## 4.6 Delegation vs Impersonation Patterns

### The Key Principle

AgentCore uses **delegation, NOT impersonation**:

| Aspect | Impersonation | Delegation |
|--------|---------------|------------|
| **What** | Agent pretends to BE user | Agent acts ON BEHALF OF user |
| **Audit** | "User did X" | "Agent did X for User" |
| **Scope** | Full user access | Only granted permissions |
| **Revocation** | Revoke user = revoke agent | Revoke agent separately |
| **Compliance** | Hard to prove who did what | Clear accountability |

### Delegation Token Example

```json
{
  "sub": "agent-service-account",     // Agent's identity
  "act": {
    "sub": "user-123@company.com"     // Acting for this user
  },
  "scope": "calendar.readonly",       // Limited scope
  "aud": "google-calendar-api"
}
```

External service sees: "Agent (not user) is requesting limited access for user-123"

---

## Module 4 Summary

### Key Points

1. **Inbound Auth** = Who's calling my agent?
2. **Outbound Auth** = How does agent access external services?
3. **2-Legged OAuth** = Agent acts as itself (no user)
4. **3-Legged OAuth** = Agent acts on behalf of user (user consents)
5. **Zero Trust** = Every request verified
6. **Delegation** = Agent carries user context, doesn't impersonate

### Auth Decision Tree

```
Need to authenticate?
│
├─► WHO is calling your agent?
│   └─► INBOUND AUTH (Cognito, Okta, EntraID)
│
└─► Agent needs to ACCESS external service?
    │
    ├─► Service-to-service (no specific user)?
    │   └─► 2-LEGGED OAUTH (Client Credentials)
    │
    └─► On behalf of a specific user?
        └─► 3-LEGGED OAUTH (Authorization Code)
```

---

## Comprehension Check

1. What is the difference between inbound and outbound authentication?

2. When would you use 2-legged OAuth vs 3-legged OAuth?

3. Why does AgentCore use delegation instead of impersonation?

4. What does "zero trust" mean in the context of AgentCore Identity?
