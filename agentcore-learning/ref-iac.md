# AgentCore Infrastructure as Code - Reference

## Overview

Deploy Amazon Bedrock AgentCore resources using your preferred IaC approach:
- **CloudFormation**: YAML/JSON templates
- **CDK**: Python programmatic infrastructure
- **Terraform**: HCL with state management

## Available Templates

### 1. Basic Agent Runtime

**What it deploys:**
- AgentCore Runtime with simple Strands agent
- ECR Repository with automated Docker builds
- IAM roles with least-privilege policies

**Use case**: Learning AgentCore basics
**Estimated cost**: ~$50-100/month

### 2. MCP Server on AgentCore Runtime

**What it deploys:**
- AgentCore Runtime hosting MCP server
- Amazon Cognito for JWT authentication
- Automated ARM64 Docker builds

**Sample tools**: `add_numbers`, `multiply_numbers`, `greet_user`
**Estimated cost**: ~$50-100/month

### 3. Multi-Agent Runtime

**What it deploys:**
- Two AgentCore Runtimes with A2A communication
- IAM roles with agent-to-agent invocation permissions
- Separate ECR repositories per agent

**Architecture**: Orchestrator agent delegates to specialist agent
**Estimated cost**: ~$100-200/month

### 4. End-to-End Weather Agent

**What it deploys:**
- AgentCore Runtime with Strands agent
- Browser Tool for web scraping
- Code Interpreter Tool for analysis
- Memory for user preferences
- S3 bucket for results

**Features**: Weather scraping, analysis, recommendations
**Estimated cost**: ~$100-150/month

## Repository Structure

```
04-infrastructure-as-code/
├── cloudformation/
│   ├── basic-runtime/
│   ├── mcp-server-agentcore-runtime/
│   ├── multi-agent-runtime/
│   └── end-to-end-weather-agent/
├── cdk/
│   ├── basic-runtime/
│   ├── mcp-server-agentcore-runtime/
│   ├── multi-agent-runtime/
│   └── end-to-end-weather-agent/
└── terraform/
    ├── basic-runtime/
    ├── mcp-server-agentcore-runtime/
    ├── multi-agent-runtime/
    └── end-to-end-weather-agent/
```

## Prerequisites

### All Approaches
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Access to Amazon Bedrock AgentCore

### CDK Specific
- Python 3.8+
- AWS CDK v2.218.0 or later

### Terraform Specific
- Terraform >= 1.6 (use tfenv for version management)

## IAM Permissions Required

- CloudFormation stack creation
- IAM roles and policies
- ECR repositories
- Lambda functions
- AgentCore resources
- S3 buckets (for weather agent)

## Deployment Commands

### CloudFormation
```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name my-agent-stack \
  --capabilities CAPABILITY_IAM
```

### CDK
```bash
cd cdk/basic-runtime
pip install -r requirements.txt
cdk deploy
```

### Terraform
```bash
cd terraform/basic-runtime
terraform init
terraform plan
terraform apply
```
