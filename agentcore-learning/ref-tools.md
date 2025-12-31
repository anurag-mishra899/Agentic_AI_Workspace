# AgentCore Tools - Reference

## Overview

Amazon Bedrock AgentCore Tools provide enterprise-grade capabilities that enhance AI agents' ability to perform complex tasks securely and efficiently. Two primary tools are available:

1. **Code Interpreter** - Secure code execution
2. **Browser Tool** - Web automation

---

## Code Interpreter

### Key Features

| Feature | Description |
|---------|-------------|
| Secure Execution | Isolated sandbox environments with internal data access |
| Fully Managed | Integrates with Strands, LangGraph, CrewAI |
| Advanced Config | Large file support (S3), internet access |
| Multi-Language | JavaScript, TypeScript, Python runtimes |

### Benefits

- **Enhanced Accuracy**: Complex calculations and data processing
- **Enterprise Security**: Isolated environments meet security requirements
- **Efficient Data Processing**: Handle gigabyte-scale data via S3 references

### Use Cases
- Data analysis and visualization
- Complex calculations
- File processing and transformation
- Dynamic code generation and execution

---

## Browser Tool

### Key Features

| Feature | Description |
|---------|-------------|
| Model Agnostic | Supports Claude, OpenAI, Nova command syntaxes |
| Enterprise Security | VM-level isolation, VPC connectivity, SSO integration |
| Audit Capabilities | CloudTrail logging, session recording |

### Capabilities

- **Live View**: Real-time monitoring for immediate intervention
- **Session Replay**: Debugging and auditing of browser sessions
- **Form Automation**: Multi-step form filling
- **Data Extraction**: Scraping and data collection
- **Web Navigation**: Complex multi-page workflows

### Benefits

- **End-to-End Automation**: Automate workflows requiring manual intervention
- **Enhanced Security**: Enterprise-grade security features
- **Real-Time Monitoring**: Live intervention and replay

---

## Tutorial Structure (from repository)

```
05-AgentCore-tools/
├── 01-Agent-Core-code-interpreter/
│   └── [Notebooks for code interpreter usage]
└── 02-Agent-Core-browser-tool/
    └── [Notebooks for browser automation]
```

## Combined Use Cases

- Complex data analysis with visualization in secure environments
- Automated web interactions for form filling and data extraction
- Large-scale data processing with web-based monitoring
- Secure code execution for AI agents in enterprise settings

## Integration Example

```python
from strands import Agent
from strands.tools import code_interpreter, browser

agent = Agent(
    tools=[code_interpreter, browser]
)

# Agent can now:
# 1. Execute code securely
# 2. Navigate and interact with websites
```
