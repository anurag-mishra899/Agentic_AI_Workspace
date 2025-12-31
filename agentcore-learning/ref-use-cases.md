# AgentCore Use Cases - Reference

## Featured Use Cases

| Use Case | Description | Key Components |
|----------|-------------|----------------|
| **AWS Operations Agent** | AWS operations assistant | Okta auth, monitoring |
| **Customer Support Assistant** | Production customer service | Memory, KB, Google OAuth |
| **DB Performance Analyzer** | Database monitoring/analysis | PostgreSQL integration |
| **Device Management Agent** | IoT device management | Cognito auth, real-time |
| **Enterprise Web Intelligence** | Web research/analysis | Browser tools |
| **Farm Management Advisor** | Agricultural advisory | Plant detection, weather |
| **Finance Personal Assistant** | Budget management | Multi-agent, guardrails |
| **Healthcare Appointment Agent** | FHIR-compliant scheduling | Patient data integration |
| **Market Trends Agent** | Financial market analysis | Browser tools, memory |
| **SRE Agent** | Site reliability engineering | Multi-agent LangGraph |
| **Text to Python IDE** | Code generation/execution | Code Interpreter |
| **Video Games Sales Assistant** | Data analysis | Amplify frontend, CDK |

## Architecture Patterns Demonstrated

### Single Agent
Focused solutions for specific tasks:
- Customer Support Assistant
- DB Performance Analyzer
- Farm Management Advisor

### Multi-Agent
Collaborative agent workflows:
- SRE Agent (LangGraph)
- Finance Personal Assistant
- A2A Multi-Agent Incident Response

### Full-Stack
Complete applications with frontend/backend:
- Video Games Sales Assistant (Amplify + CDK)
- Customer Support Assistant (Streamlit)
- Healthcare Appointment Agent

### Integration Patterns
Connecting with external systems:
- Device Management (IoT)
- Healthcare (FHIR)
- Enterprise Web Intelligence

### Authentication Patterns
Various identity providers:
- **Cognito**: Device Management, Healthcare
- **Okta**: AWS Operations
- **Google**: Customer Support
- **EntraID**: Enterprise scenarios

## Repository Structure

```
02-use-cases/
├── A2A-multi-agent-incident-response/
├── AWS-operations-agent/
├── customer-support-assistant/
├── customer-support-assistant-vpc/
├── DB-performance-analyzer/
├── device-management-agent/
├── enterprise-web-intelligence-agent/
├── farm-management-advisor/
├── finance-personal-assistant/
├── gateway-schema-support-agent/
├── healthcare-appointment-agent/
├── local-prototype-to-agentcore/
├── market-trends-agent/
├── site-reliability-agent-workshop/
├── slide-deck-generator-memory-agent/
├── SRE-agent/
├── text-to-python-ide/
└── video-games-sales-assistant/
```

## What Each Use Case Includes

- Complete source code and configuration
- Step-by-step deployment instructions
- Architecture diagrams and explanations
- Testing and validation scripts
- Cleanup procedures

## Blueprints (Full-Stack Reference Apps)

Location: `05-blueprints/`

| Blueprint | Description |
|-----------|-------------|
| **Shopping Concierge Agent** | E-commerce assistant |
| **Travel Concierge Agent** | Travel planning assistant |

These provide deployment-ready foundations with integrated services, authentication, and business logic.

## End-to-End Tutorial (Recommended Starting Point)

Location: `01-tutorials/09-AgentCore-E2E/`

**Customer Support Agent Journey:**
1. Lab 1: Create Agent Prototype (20 mins)
2. Lab 2: Add Memory (20 mins)
3. Lab 3: Gateway & Identity (30 mins)
4. Lab 4: Deploy to Runtime (30 mins)
5. Lab 5: Evaluations (10 mins)
6. Lab 6: Frontend (20 mins)
7. Lab 7: Cleanup

This lab series takes a single use case from prototype to production, demonstrating all AgentCore services.
