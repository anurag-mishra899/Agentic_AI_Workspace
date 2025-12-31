# Module 10: Production Deployment

## 10.1 From Development to Production

### The Production Checklist

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION READINESS CHECKLIST                    │
│                                                                      │
│  Infrastructure                                                      │
│  □ Infrastructure as Code (not manual console clicks)               │
│  □ Multi-environment setup (dev, staging, prod)                     │
│  □ VPC configuration for network security                           │
│                                                                      │
│  Security                                                           │
│  □ IAM roles with least-privilege                                   │
│  □ Secrets in AWS Secrets Manager                                   │
│  □ Identity provider configured (Cognito, Okta, etc.)               │
│  □ Policy Engine with ENFORCE mode                                  │
│                                                                      │
│  Observability                                                      │
│  □ Tracing enabled (CloudWatch or partner)                          │
│  □ Alerts configured for errors and latency                         │
│  □ Dashboard for key metrics                                        │
│                                                                      │
│  Quality                                                            │
│  □ Online evaluations running                                       │
│  □ Quality thresholds defined                                       │
│  □ Alerting on quality drops                                        │
│                                                                      │
│  Operations                                                         │
│  □ CI/CD pipeline for deployments                                   │
│  □ Rollback strategy defined                                        │
│  □ Cost monitoring and budgets                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10.2 Infrastructure as Code Options

### Three IaC Approaches

| Approach | Language | Best For |
|----------|----------|----------|
| **CloudFormation** | YAML/JSON | AWS-native, declarative |
| **CDK** | Python/TypeScript | Programmatic, reusable constructs |
| **Terraform** | HCL | Multi-cloud, state management |

### CloudFormation Example

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: AgentCore Runtime Deployment

Resources:
  AgentRuntime:
    Type: AWS::BedrockAgentCore::Runtime
    Properties:
      RuntimeName: my-production-agent
      ContainerImage: !Sub ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/my-agent:latest
      ExecutionRoleArn: !GetAtt AgentExecutionRole.Arn
      MemorySize: 2048
      Timeout: 300

  AgentExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: agentcore.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSBedrockAgentCoreExecutionPolicy
```

**Deploy:**
```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name my-agent-prod \
  --capabilities CAPABILITY_IAM
```

### CDK Example (Python)

```python
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_iam as iam,
)
from constructs import Construct

class AgentCoreStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ECR Repository
        repo = ecr.Repository(
            self, "AgentRepo",
            repository_name="my-agent"
        )

        # Execution Role
        role = iam.Role(
            self, "AgentRole",
            assumed_by=iam.ServicePrincipal("agentcore.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBedrockAgentCoreExecutionPolicy"
                )
            ]
        )

        # AgentCore Runtime (using CfnResource for preview)
        runtime = CfnResource(
            self, "AgentRuntime",
            type="AWS::BedrockAgentCore::Runtime",
            properties={
                "RuntimeName": "my-production-agent",
                "ContainerImage": repo.repository_uri,
                "ExecutionRoleArn": role.role_arn,
                "MemorySize": 2048,
                "Timeout": 300
            }
        )
```

**Deploy:**
```bash
cd cdk/my-agent
pip install -r requirements.txt
cdk deploy
```

### Terraform Example

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_ecr_repository" "agent_repo" {
  name = "my-agent"
}

resource "aws_iam_role" "agent_role" {
  name = "agent-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "agentcore.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "agent_policy" {
  role       = aws_iam_role.agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBedrockAgentCoreExecutionPolicy"
}

# AgentCore Runtime resource (when available in provider)
```

**Deploy:**
```bash
cd terraform/my-agent
terraform init
terraform plan
terraform apply
```

---

## 10.3 Multi-Agent Architectures

### Pattern: Orchestrator + Specialists

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT ARCHITECTURE                          │
│                                                                      │
│                        User Request                                  │
│                             │                                        │
│                             ▼                                        │
│                   ┌─────────────────┐                               │
│                   │  ORCHESTRATOR   │                               │
│                   │     AGENT       │                               │
│                   │                 │                               │
│                   │  "Route to      │                               │
│                   │   specialist"   │                               │
│                   └────────┬────────┘                               │
│                            │                                        │
│          ┌─────────────────┼─────────────────┐                     │
│          ▼                 ▼                 ▼                     │
│   ┌────────────┐   ┌────────────┐   ┌────────────┐                │
│   │  FLIGHT    │   │   HOTEL    │   │ ACTIVITIES │                │
│   │  AGENT     │   │   AGENT    │   │   AGENT    │                │
│   │            │   │            │   │            │                │
│   │ Specialist │   │ Specialist │   │ Specialist │                │
│   │ in flights │   │ in hotels  │   │ in tours   │                │
│   └────────────┘   └────────────┘   └────────────┘                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### IAM for Agent-to-Agent Communication

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeAgent",
      "Resource": [
        "arn:aws:bedrock-agentcore:*:*:agent/flight-agent-id",
        "arn:aws:bedrock-agentcore:*:*:agent/hotel-agent-id",
        "arn:aws:bedrock-agentcore:*:*:agent/activities-agent-id"
      ]
    }
  ]
}
```

### When to Use Multi-Agent

| Scenario | Single Agent | Multi-Agent |
|----------|--------------|-------------|
| Simple Q&A | ✓ | |
| Single domain | ✓ | |
| Multiple domains | | ✓ |
| Complex workflows | | ✓ |
| Independent scaling | | ✓ |
| Team ownership boundaries | | ✓ |

---

## 10.4 VPC Integration & Network Security

### Why VPC?

```
Without VPC:
┌─────────────┐     Internet     ┌─────────────┐
│   Agent     │◄───────────────►│  External   │
│  (Public)   │                  │   APIs      │
└─────────────┘                  └─────────────┘
     ⚠️ All traffic traverses public internet

With VPC:
┌──────────────────────────────────────────────┐
│                   YOUR VPC                    │
│  ┌─────────────┐         ┌─────────────┐    │
│  │   Agent     │◄───────►│  Internal   │    │
│  │ (Private)   │         │   APIs      │    │
│  └──────┬──────┘         └─────────────┘    │
│         │                                    │
│         │ NAT Gateway (if needed)           │
└─────────┼────────────────────────────────────┘
          │
          ▼ (controlled egress only)
     ┌─────────────┐
     │  External   │
     │   APIs      │
     └─────────────┘
```

### VPC Configuration

```python
# CDK Example
from aws_cdk import aws_ec2 as ec2

# Create VPC
vpc = ec2.Vpc(
    self, "AgentVpc",
    max_azs=2,
    nat_gateways=1,
    subnet_configuration=[
        ec2.SubnetConfiguration(
            name="Private",
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        ),
        ec2.SubnetConfiguration(
            name="Public",
            subnet_type=ec2.SubnetType.PUBLIC
        )
    ]
)

# Security Group
security_group = ec2.SecurityGroup(
    self, "AgentSG",
    vpc=vpc,
    description="Security group for AgentCore Runtime",
    allow_all_outbound=False  # Explicit egress rules
)

# Allow HTTPS egress only
security_group.add_egress_rule(
    ec2.Peer.any_ipv4(),
    ec2.Port.tcp(443),
    "Allow HTTPS outbound"
)
```

### VPC Endpoints for AWS Services

```python
# VPC Endpoints to avoid public internet
vpc.add_gateway_endpoint(
    "S3Endpoint",
    service=ec2.GatewayVpcEndpointAwsService.S3
)

vpc.add_interface_endpoint(
    "BedrockEndpoint",
    service=ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME
)

vpc.add_interface_endpoint(
    "SecretsManagerEndpoint",
    service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER
)
```

---

## 10.5 Cost Optimization Strategies

### Cost Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENTCORE COST BREAKDOWN                          │
│                                                                      │
│   ┌──────────────────┐                                              │
│   │  LLM Calls       │  ████████████████████████  ~60-70%           │
│   │  (Bedrock)       │  Tokens (input + output)                     │
│   └──────────────────┘                                              │
│                                                                      │
│   ┌──────────────────┐                                              │
│   │  Runtime         │  ████████  ~15-20%                           │
│   │  (Compute)       │  Memory × Duration                           │
│   └──────────────────┘                                              │
│                                                                      │
│   ┌──────────────────┐                                              │
│   │  Tools           │  ████  ~5-10%                                │
│   │  (Browser/Code)  │  Session time                                │
│   └──────────────────┘                                              │
│                                                                      │
│   ┌──────────────────┐                                              │
│   │  Storage/Network │  ██  ~5%                                     │
│   │  (S3, Transfer)  │                                              │
│   └──────────────────┘                                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Optimization Strategies

**1. Model Selection**
```python
# Use smaller models for simple tasks
from strands import Agent

# Complex reasoning → Larger model
complex_agent = Agent(model="anthropic.claude-3-opus")

# Simple classification → Smaller model
simple_agent = Agent(model="anthropic.claude-3-haiku")

# Route based on task complexity
def route_request(payload):
    if is_complex(payload):
        return complex_agent(payload["prompt"])
    else:
        return simple_agent(payload["prompt"])
```

**2. Semantic Tool Search**
```python
# Don't send all 100 tool descriptions to LLM
gateway = GatewayClient(gateway_id="my-gateway")

# Search for relevant tools only
relevant_tools = gateway.search_tools(
    query=payload["prompt"],
    max_results=5  # Only top 5 relevant tools
)

agent = Agent(tools=relevant_tools)  # Fewer tokens
```

**3. Caching**
```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_agent_call(prompt_hash):
    return agent(original_prompt)

def invoke(payload):
    prompt = payload["prompt"]
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()

    # Check if similar prompt was answered before
    return cached_agent_call(prompt_hash)
```

**4. Memory Strategy**
```python
# Don't retrieve ALL memories - use semantic search
memories = memory.search_memories(
    memoryStoreId="my-store",
    actorId=user_id,
    query=payload["prompt"],
    maxResults=3  # Only most relevant
)
```

### Cost Monitoring

```python
# CloudWatch cost dashboard
import boto3

cloudwatch = boto3.client('cloudwatch')

# Set up billing alarm
cloudwatch.put_metric_alarm(
    AlarmName='AgentCore-Daily-Spend',
    MetricName='EstimatedCharges',
    Namespace='AWS/Billing',
    Statistic='Maximum',
    Period=86400,  # Daily
    EvaluationPeriods=1,
    Threshold=100,  # $100/day
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:...']
)
```

---

## 10.6 Scaling Patterns

### AgentCore Runtime Scaling

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTO-SCALING BEHAVIOR                             │
│                                                                      │
│   Traffic: ▁▂▃▅▆▇█▇▆▅▃▂▁                                           │
│                                                                      │
│   Instances:                                                        │
│   ┌───┐                                                             │
│   │ 1 │──▶ Low traffic (baseline)                                  │
│   └───┘                                                             │
│                                                                      │
│   ┌───┐ ┌───┐ ┌───┐                                                │
│   │ 1 │ │ 2 │ │ 3 │──▶ Medium traffic (scale out)                  │
│   └───┘ └───┘ └───┘                                                │
│                                                                      │
│   ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                                   │
│   │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │──▶ Peak traffic                   │
│   └───┘ └───┘ └───┘ └───┘ └───┘                                   │
│                                                                      │
│   AgentCore Runtime handles scaling automatically                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Scaling Configuration

```python
# Configure scaling behavior
runtime_config = {
    "minInstances": 1,        # Minimum warm instances
    "maxInstances": 10,       # Maximum scale out
    "targetConcurrency": 10,  # Requests per instance before scaling
    "scaleInCooldown": 300,   # Seconds before scaling in
    "scaleOutCooldown": 60    # Seconds before scaling out
}
```

### Load Testing

```bash
# Use artillery or locust for load testing
artillery run load-test.yaml

# load-test.yaml
config:
  target: "https://your-agent-endpoint.aws"
  phases:
    - duration: 60
      arrivalRate: 5
    - duration: 120
      arrivalRate: 20
    - duration: 60
      arrivalRate: 50

scenarios:
  - flow:
      - post:
          url: "/invoke"
          json:
            prompt: "What is the weather in Seattle?"
```

---

## 10.7 CI/CD Pipeline

### Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE                                    │
│                                                                      │
│   Code Push                                                         │
│       │                                                             │
│       ▼                                                             │
│   ┌─────────────────┐                                               │
│   │  1. Build       │  Docker build, unit tests                     │
│   └────────┬────────┘                                               │
│            ▼                                                        │
│   ┌─────────────────┐                                               │
│   │  2. Test        │  Integration tests, evaluation suite          │
│   └────────┬────────┘                                               │
│            ▼                                                        │
│   ┌─────────────────┐                                               │
│   │  3. Deploy Dev  │  Deploy to development environment            │
│   └────────┬────────┘                                               │
│            ▼                                                        │
│   ┌─────────────────┐                                               │
│   │  4. Eval Gate   │  Run evaluations, check quality thresholds    │
│   └────────┬────────┘                                               │
│            ▼                                                        │
│   ┌─────────────────┐                                               │
│   │  5. Deploy Prod │  Blue/green deployment to production          │
│   └─────────────────┘                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yaml
name: Deploy Agent

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - name: Build and push Docker image
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker build -t $ECR_REGISTRY/my-agent:$GITHUB_SHA .
          docker push $ECR_REGISTRY/my-agent:$GITHUB_SHA

      - name: Deploy to AgentCore
        run: |
          agentcore configure -e agent.py --image $ECR_REGISTRY/my-agent:$GITHUB_SHA
          agentcore launch

      - name: Run evaluations
        run: |
          python run_evaluations.py --threshold 0.8

      - name: Notify on failure
        if: failure()
        run: |
          aws sns publish --topic-arn $SNS_TOPIC --message "Deployment failed"
```

---

## Module 10 Summary

### Key Points

1. **Infrastructure as Code** — CloudFormation, CDK, or Terraform
2. **Multi-agent architectures** — Orchestrator + specialists for complex domains
3. **VPC integration** — Network isolation, VPC endpoints
4. **Cost optimization** — Model selection, semantic search, caching
5. **Auto-scaling** — Handled by AgentCore Runtime
6. **CI/CD** — Automated testing, evaluation gates, blue/green deploys

### Production Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                                  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                         VPC                                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │  │
│  │  │  Agent 1   │  │  Agent 2   │  │  Gateway   │             │  │
│  │  │ (Runtime)  │  │ (Runtime)  │  │  (Tools)   │             │  │
│  │  └────────────┘  └────────────┘  └────────────┘             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│         ┌────────────────────┼────────────────────┐                │
│         ▼                    ▼                    ▼                │
│   ┌──────────┐         ┌──────────┐         ┌──────────┐          │
│   │ Identity │         │ Memory   │         │ Policy   │          │
│   │ (Auth)   │         │ (State)  │         │ (Guard)  │          │
│   └──────────┘         └──────────┘         └──────────┘          │
│                              │                                      │
│         ┌────────────────────┼────────────────────┐                │
│         ▼                    ▼                    ▼                │
│   ┌──────────┐         ┌──────────┐         ┌──────────┐          │
│   │Observ-   │         │ Evals    │         │CloudWatch│          │
│   │ability   │         │ (Score)  │         │ (Alerts) │          │
│   └──────────┘         └──────────┘         └──────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Comprehension Check

1. What are the three IaC options for deploying AgentCore resources?

2. When would you use a multi-agent architecture instead of a single agent?

3. What is the biggest cost component in AgentCore, and how can you optimize it?

4. Why would you deploy AgentCore Runtime inside a VPC?

