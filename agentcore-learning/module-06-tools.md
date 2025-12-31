# Module 6: AgentCore Tools

## 6.1 Code Interpreter: Secure Sandboxed Code Execution

### The Problem: Agents Need to Execute Code

Many agent tasks require actual code execution:
- "Analyze this CSV and create a chart"
- "Calculate the compound interest on this loan"
- "Parse this JSON and extract specific fields"

Without a secure execution environment:

```
❌ Execute on user's machine → Security nightmare
❌ Execute on your servers → Resource management, isolation issues
❌ Don't execute at all → Limited agent capabilities
```

### Code Interpreter Solution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CODE INTERPRETER SANDBOX                          │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  Isolated Environment                                        │   │
│   │  • Own filesystem      • Memory limits                       │   │
│   │  • Network isolation   • CPU limits                          │   │
│   │  • No access to host   • Time limits                         │   │
│   └────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│   │   Python    │   │ JavaScript  │   │ TypeScript  │              │
│   │   Runtime   │   │   Runtime   │   │   Runtime   │              │
│   └─────────────┘   └─────────────┘   └─────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### How It Works

```
User Query: "Analyze sales.csv and create a bar chart"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         LLM                                          │
│  1. Understands task                                                 │
│  2. Generates Python code:                                           │
│     import pandas as pd                                              │
│     import matplotlib.pyplot as plt                                  │
│     df = pd.read_csv('sales.csv')                                    │
│     df.plot(kind='bar')                                              │
│     plt.savefig('chart.png')                                         │
└─────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CODE INTERPRETER                                   │
│  • Creates sandbox session                                           │
│  • Executes code safely                                              │
│  • Returns results + output files                                    │
└─────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
            Response + chart.png
```

### Basic Usage

```python
from bedrock_agentcore.tools import CodeInterpreterClient

# Create client
code_interpreter = CodeInterpreterClient()

# Start a session (persists across multiple executions)
session = code_interpreter.create_session(
    runtime="python",  # or "javascript", "typescript"
    timeout=300  # seconds
)

# Execute code
result = code_interpreter.execute(
    sessionId=session["sessionId"],
    code="""
import pandas as pd
import matplotlib.pyplot as plt

# Create sample data
data = {'Product': ['A', 'B', 'C'], 'Sales': [100, 150, 80]}
df = pd.DataFrame(data)

# Create chart
df.plot(kind='bar', x='Product', y='Sales')
plt.savefig('sales_chart.png')
print("Chart created!")
"""
)

print(result["stdout"])  # "Chart created!"
print(result["files"])   # ["sales_chart.png"]
```

### With Strands Agent

```python
from strands import Agent
from bedrock_agentcore.tools import code_interpreter

agent = Agent(
    tools=[code_interpreter],
    system_prompt="You are a data analyst. Use code execution to analyze data."
)

result = agent("""
Analyze this data and tell me the average:
[45, 67, 23, 89, 12, 56, 78, 34, 90, 11]
""")

# Agent automatically:
# 1. Generates Python code
# 2. Executes in sandbox
# 3. Returns result with explanation
```

---

## 6.2 Session Persistence

### Why Sessions Matter

```
Without Sessions (Stateless):
┌──────────────┐
│ Execute:     │    ┌──────────────┐
│ x = 10       │───▶│ x = 10       │ ✓
└──────────────┘    └──────────────┘

┌──────────────┐
│ Execute:     │    ┌──────────────┐
│ print(x)     │───▶│ Error: x     │ ✗  (x doesn't exist!)
└──────────────┘    │ not defined  │
                    └──────────────┘

With Sessions (Stateful):
┌──────────────┐
│ Session: A   │    ┌──────────────┐
│ x = 10       │───▶│ x = 10       │ ✓
└──────────────┘    └──────────────┘
                           │
                           ▼ (state preserved)
┌──────────────┐    ┌──────────────┐
│ Session: A   │───▶│ print(x)     │ ✓
│ print(x)     │    │ Output: 10   │
└──────────────┘    └──────────────┘
```

### Session Management

```python
# Create session
session = code_interpreter.create_session(
    runtime="python",
    timeout=600,  # Session lives for 10 minutes
    memoryMb=512  # Memory allocation
)

session_id = session["sessionId"]

# First execution - define function
code_interpreter.execute(
    sessionId=session_id,
    code="""
def calculate_tax(amount, rate=0.1):
    return amount * rate
"""
)

# Second execution - use function (state preserved!)
result = code_interpreter.execute(
    sessionId=session_id,
    code="print(calculate_tax(1000))"
)
# Output: 100.0

# Clean up when done
code_interpreter.delete_session(sessionId=session_id)
```

---

## 6.3 S3 Integration for Large Files

### The Challenge: Gigabyte-Scale Data

Passing large files through API calls is impractical:

```
❌ API Payload: Limited to MBs
❌ Memory: Can't load GB files into context
```

### S3 Solution

```
┌─────────────────────────────────────────────────────────────────────┐
│                      S3 INTEGRATION                                  │
│                                                                      │
│   ┌─────────────┐                    ┌─────────────────────────┐   │
│   │    S3       │   S3 Reference     │   Code Interpreter      │   │
│   │  Bucket     │───────────────────▶│   Sandbox               │   │
│   │             │                    │                         │   │
│   │ large.csv   │   (Not the file    │   Downloads file        │   │
│   │ (5GB)       │    itself!)        │   directly from S3      │   │
│   └─────────────┘                    └─────────────────────────┘   │
│                                                │                     │
│                                                ▼                     │
│                                       ┌─────────────────────────┐   │
│                                       │   Process & Analyze     │   │
│                                       │   Upload results to S3  │   │
│                                       └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# Configure session with S3 access
session = code_interpreter.create_session(
    runtime="python",
    s3Configuration={
        "inputBucket": "my-data-bucket",
        "outputBucket": "my-results-bucket",
        "inputPrefix": "raw-data/",
        "outputPrefix": "processed/"
    }
)

# Execute with S3 file reference
result = code_interpreter.execute(
    sessionId=session["sessionId"],
    code="""
import pandas as pd

# File automatically available from S3
df = pd.read_csv('/input/sales_2024.csv')  # 5GB file

# Process
summary = df.groupby('region').sum()

# Save to output (automatically uploaded to S3)
summary.to_csv('/output/regional_summary.csv')
print(f"Processed {len(df)} rows")
""",
    inputFiles=[
        {"s3Uri": "s3://my-data-bucket/raw-data/sales_2024.csv"}
    ]
)

# Results uploaded to s3://my-results-bucket/processed/regional_summary.csv
```

---

## 6.4 Browser Tool: Automated Web Navigation

### The Problem: Agents Need Web Access

Many tasks require interacting with websites:
- "Fill out this form on the vendor portal"
- "Check the status of my order on the website"
- "Extract pricing data from competitor sites"

### Browser Tool Solution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BROWSER TOOL SANDBOX                              │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  VM-Level Isolation                                          │   │
│   │  • 1:1 session mapping   • No cross-session access           │   │
│   │  • VPC connectivity      • SSO integration                   │   │
│   └────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │                    Headless Browser                          │  │
│   │  • Playwright/Puppeteer                                      │  │
│   │  • Full browser capabilities                                 │  │
│   │  • Screenshot capture                                        │  │
│   └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### How Browser Tool Works

```
User: "Check my order status on shop.example.com"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         LLM                                          │
│  Translates to browser commands:                                     │
│  1. navigate("https://shop.example.com")                            │
│  2. click("Login button")                                           │
│  3. type("username", "user@email.com")                              │
│  4. click("Orders")                                                 │
│  5. extract("order status")                                         │
└─────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   BROWSER SANDBOX                                    │
│  • Executes commands in isolated browser                            │
│  • Captures screenshots for feedback                                 │
│  • Returns extracted data                                           │
└─────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
            "Your order #12345 is: Shipped"
```

### Basic Usage

```python
from bedrock_agentcore.tools import BrowserClient

browser = BrowserClient()

# Create browser session
session = browser.create_session(
    timeout=300,
    viewport={"width": 1920, "height": 1080}
)

# Navigate and interact
result = browser.execute(
    sessionId=session["sessionId"],
    commands=[
        {"action": "navigate", "url": "https://example.com"},
        {"action": "click", "selector": "#login-button"},
        {"action": "type", "selector": "#username", "text": "user@example.com"},
        {"action": "type", "selector": "#password", "text": "password123"},
        {"action": "click", "selector": "#submit"},
        {"action": "screenshot"},
        {"action": "extract", "selector": ".dashboard-data"}
    ]
)

print(result["extractedData"])
print(result["screenshots"])  # List of screenshot URLs
```

### Model-Agnostic Integration

Browser Tool supports multiple AI model command syntaxes:

```python
# Works with Claude
from anthropic import Anthropic

# Works with OpenAI
from openai import OpenAI

# Works with Amazon Nova
import boto3

# All can generate browser commands that Browser Tool understands
```

### With Strands Agent

```python
from strands import Agent
from bedrock_agentcore.tools import browser_tool

agent = Agent(
    tools=[browser_tool],
    system_prompt="""You are a web automation assistant.
    Use the browser tool to navigate websites and complete tasks."""
)

result = agent("""
Go to weather.com and tell me the current temperature in Seattle.
""")
```

---

## 6.5 Live View and Session Recording

### Real-Time Monitoring

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LIVE VIEW                                    │
│                                                                      │
│   Human Operator                    Browser Session                  │
│   ┌───────────────┐                ┌───────────────┐                │
│   │               │   Real-time    │               │                │
│   │   Monitoring  │◀───Stream─────│   Agent       │                │
│   │   Dashboard   │                │   Browsing    │                │
│   │               │                │               │                │
│   │   [Intervene] │───Override────▶│               │                │
│   └───────────────┘                └───────────────┘                │
│                                                                      │
│   Features:                                                          │
│   • Watch agent browse in real-time                                  │
│   • Take over control if needed                                      │
│   • Guide agent through complex steps                                │
└─────────────────────────────────────────────────────────────────────┘
```

### Session Replay for Debugging

```python
# Enable session recording
session = browser.create_session(
    recording={
        "enabled": True,
        "outputBucket": "my-recordings-bucket"
    }
)

# ... agent performs actions ...

# Later: Retrieve recording for debugging
recording = browser.get_session_recording(
    sessionId=session["sessionId"]
)

print(recording["videoUrl"])  # S3 URL to session recording
print(recording["commands"])  # List of all commands executed
print(recording["timestamps"])  # When each command was executed
```

### Use Cases for Live View

| Scenario | How Live View Helps |
|----------|-------------------|
| **Training** | Watch agent learn to navigate complex sites |
| **Debugging** | See exactly what went wrong |
| **Compliance** | Audit trail of all web interactions |
| **Human-in-the-Loop** | Take over for sensitive operations |

---

## 6.6 VPC Integration & Enterprise Security

### Accessing Internal Websites

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR VPC                                          │
│                                                                      │
│   ┌───────────────┐        ┌───────────────────────────────────┐   │
│   │  Internal     │        │  Browser Tool                      │   │
│   │  Web App      │◀───────│  (VPC-connected)                   │   │
│   │               │        │                                    │   │
│   │  (No public   │        │  Can access internal apps          │   │
│   │   access)     │        │  through VPC peering               │   │
│   └───────────────┘        └───────────────────────────────────┘   │
│                                                                      │
│   Security:                                                          │
│   • Browser runs in your VPC                                         │
│   • No data leaves your network                                      │
│   • Integrates with your security controls                           │
└─────────────────────────────────────────────────────────────────────┘
```

### VPC Configuration

```python
session = browser.create_session(
    vpcConfiguration={
        "vpcId": "vpc-12345",
        "subnetIds": ["subnet-abc", "subnet-def"],
        "securityGroupIds": ["sg-12345"]
    }
)

# Now browser can access internal URLs
browser.execute(
    sessionId=session["sessionId"],
    commands=[
        {"action": "navigate", "url": "https://internal-app.company.local"}
    ]
)
```

### Enterprise Security Features

| Feature | Description |
|---------|-------------|
| **VM Isolation** | Each session runs in dedicated VM |
| **1:1 Session Mapping** | One user = one browser session |
| **CloudTrail Logging** | All browser commands logged |
| **SSO Integration** | Use corporate identity |
| **Session Recording** | Full audit trail |

---

## 6.7 Combining Code Interpreter and Browser

### Powerful Combinations

```python
from strands import Agent
from bedrock_agentcore.tools import code_interpreter, browser_tool

agent = Agent(
    tools=[code_interpreter, browser_tool],
    system_prompt="""You are a data analyst with web access.
    Use browser to collect data, code interpreter to analyze it."""
)

result = agent("""
1. Go to finance.yahoo.com and extract the top 10 stock prices
2. Calculate the average price and standard deviation
3. Create a visualization showing the distribution
""")

# Agent:
# 1. Uses browser_tool to navigate and extract data
# 2. Uses code_interpreter to analyze and visualize
# 3. Returns comprehensive analysis
```

---

## Module 6 Summary

### Key Points

1. **Code Interpreter** = Secure sandbox for executing Python/JS/TS code
2. **Sessions** = Persistent state across multiple code executions
3. **S3 Integration** = Handle gigabyte-scale files efficiently
4. **Browser Tool** = Automated web navigation in isolated environment
5. **Live View** = Real-time monitoring and human intervention
6. **VPC Support** = Access internal applications securely

### Tool Selection Guide

```
Task requires...                    Use...
─────────────────────────────────────────────────────
Math, calculations                  Code Interpreter
Data analysis, visualization        Code Interpreter
File processing                     Code Interpreter + S3
Web scraping                        Browser Tool
Form filling                        Browser Tool
Login to websites                   Browser Tool
Both data + web                     Both tools together
```

### Security Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                                   │
│                                                                      │
│   1. Isolation    ──▶  Each session in separate sandbox             │
│   2. Limits       ──▶  Memory, CPU, time constraints                │
│   3. Network      ──▶  Controlled internet/VPC access               │
│   4. Audit        ──▶  CloudTrail logging, session recording        │
│   5. Identity     ──▶  Integrated with AgentCore Identity           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Comprehension Check

1. Why does Code Interpreter use isolated sandbox environments instead of executing code directly?

2. What is the benefit of session persistence in Code Interpreter?

3. How does S3 integration solve the large file problem?

4. What enterprise security features does Browser Tool provide?

