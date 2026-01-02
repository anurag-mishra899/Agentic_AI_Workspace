# Interview Agent - Technical Specification

## Overview

A real-time voice-based AI interview preparation system that provides adaptive, diagnostic interview practice across multiple domains. The system identifies candidate weaknesses, adapts to their level, and delivers comprehensive feedback.

---

## 1. Core Product Definition

### 1.1 Interview Modality
- **Primary**: Real-time voice conversation
- **Technology**: Azure OpenAI Realtime API (native multimodal, avoids STT→LLM→TTS latency)
- **No live coding**: Verbal explanation and drilling of implementation details only

### 1.2 Supported Domains
All three domains required for launch:

| Domain | Scope | Skill Tree Structure |
|--------|-------|---------------------|
| **Coding** | DSA + practical (APIs, debugging, testing) | Problem Types (arrays, strings, trees, graphs, DP, etc.) |
| **System Design** | Junior through Staff+ levels | Concepts (scaling, consistency, availability, etc.) |
| **ML/AI** | Theory + Applied + Production/MLOps | Problem Types (classification, regression, NLP, CV, etc.) |

### 1.3 Target Users
- Interview candidates preparing for technical roles
- Experience level inferred from resume
- English-only for MVP

---

## 2. Candidate-Guided Controls

### 2.1 Pre-Session Inputs
Candidate must provide **at least one** of:
- Resume (PDF upload)
- Explicit weak area declarations

These inputs are advisory but high-priority for session focus.

### 2.2 Weak Area Declaration
Candidates may specify:
- Topics they believe are weak (e.g., "Backpropagation intuition", "SQL window functions")
- Skills to improve (conceptual depth, explanation clarity, follow-up handling)

**Resolution Strategy:**
- System probes declared weak areas early
- Validates whether weakness is: Real / Overestimated / Underestimated
- Adjusts remaining session accordingly
- Candidate-flagged weaknesses take precedence unless strong evidence disproves them

### 2.3 Depth Level Configuration
Three modes available:

| Mode | Behavior |
|------|----------|
| **Surface Review** | High-level understanding, breadth over depth |
| **Interview-Ready** | Common follow-ups, typical traps |
| **Expert / Stress-Test** | Edge cases, theoretical limits, design tradeoffs |

**Dynamic Adjustment:**
- System may temporarily exceed requested depth if resume claims demand it or candidate excels
- System may reduce depth if foundational gaps detected
- All deviations documented in feedback

---

## 3. Interviewer Personas

### 3.1 Available Personas (5 total)
All five required for launch. Persona locked at session start (no mid-session switching).

| Persona | Tone | Question Selection | Follow-up Style | Special Characteristics |
|---------|------|-------------------|-----------------|------------------------|
| **Friendly / Coach** | Supportive | Standard | Gentle probing | Yields on interruption |
| **Neutral / Standard** | Professional | Standard | Balanced | Default behavior |
| **Aggressive / Stress** | Challenging | Standard | Intense drilling | Pushes back on interruption, as tough as real difficult interviews |
| **FAANG-style** | Structured | Bar-raiser format, higher difficulty | Leadership principles, behavioral hooks | Time pressure emphasis, structured format |
| **Startup / Rapid-fire** | Fast-paced | Breadth-focused, practical | "How would you ship this fast?" | Culture fit emphasis, adaptability questions |

### 3.2 Persona Implementation
- **Distinct system prompts per persona** (not parameterized)
- Full differentiation: tone + question selection + follow-up patterns
- Persona affects delivery, NOT diagnostic rigor (friendly still probes deeply)

### 3.3 Persona-Specific Behaviors
- **Interrupt handling**: Aggressive/FAANG push back, Friendly yields
- **Response length tolerance**: Aggressive interrupts ramblers, Friendly allows more space
- **Time pressure**: FAANG enforces strict timing, others more flexible

---

## 4. Weakness Detection System

### 4.1 Multi-Signal Fusion Model
Signals combined with weights:

| Signal | Weight | Notes |
|--------|--------|-------|
| **Semantic analysis of answers** | High | LLM grades correctness, depth, precision |
| **Follow-up failure rate** | High | Track drill-down failures |
| **Verbal cues** | Medium | Filler words, tone shifts |
| **Response latency** | Low | Downweighted - can't distinguish thinking vs confusion |

### 4.2 Ground Truth & Calibration
- Bootstrap with **LLM-as-judge** evaluation
- Refine with real outcome data over time (candidate self-reports)

### 4.3 Gaming Prevention
- If candidate declares everything as weak but performs well, system recalibrates
- Performance-based detection overrides declarations

---

## 5. Evaluation Rubrics

### 5.1 Structured Decomposition Scoring
Domain-specific dimensions, not generic rubric.

**Coding Domain:**
- Correctness of approach
- Optimization awareness
- Edge case handling
- Communication clarity
- Implementation detail accuracy (verbal)

**System Design Domain:**
- Requirements clarification
- Component selection rationale
- Scalability considerations
- Trade-off articulation
- Production readiness

**ML Domain (custom per sub-topic):**
- Mathematical foundation
- Intuition for why X works
- Model selection rationale
- Evaluation methodology
- Production/deployment concerns

### 5.2 Difficulty Levels
3 levels per skill: **Easy / Medium / Hard**

---

## 6. Session Flow

### 6.1 Onboarding (First 2 minutes)
1. Candidate uploads resume OR declares weak areas (at least one required)
2. Select persona
3. Select depth mode
4. Select domain focus (or let system choose)
5. Immediate start - no warm-up phase, straight to questions

### 6.2 Session Duration
- **Model**: Hybrid with max cap
- **Max cap**: 60 minutes
- **Early termination**: If declared weak areas exhausted and goals met, session ends early
- "Efficiency is the value" - time saved is the reward

### 6.3 Turn-Taking
- **Signal**: Silence detection (3-5 seconds threshold)
- Patient threshold allows thinking time
- Persona affects tolerance for verbose answers

### 6.4 Domain Transitions
- **Explicit transitions**: "Now let's move to system design"
- Clear delineation between domains
- Agent-guided structure for system design: "First describe the API, then the data model, then..."

### 6.5 Level Mismatch Handling
If resume suggests senior but performance is junior:
- Gradually reduce difficulty without commenting
- Note discrepancy in feedback report

### 6.6 Mid-Session Exit
- Immediate stop allowed at any time
- Partial feedback generated for whatever was covered
- Session state not preserved for later resumption

### 6.7 Session Constraints
- No concurrent sessions per user (second tab blocked)
- Instant start always (no scheduling)
- Booking flow: Click → Configure → Start immediately

---

## 7. Question Generation

### 7.1 Hybrid Approach
- **Core questions**: Curated question bank (vetted, reliable)
- **Follow-ups**: LLM-generated in real-time based on candidate responses

### 7.2 Question Bank Structure
- **Organization**: Skill-graph mapped (hierarchical tree)
- **Hierarchy**: Domain → Topic → Subtopic → Skill
- **Each skill has**: Multiple questions at Easy/Medium/Hard levels
- **Content creation**: LLM-generated then human-curated

### 7.3 Verbal Drilling for Coding
Since no live coding:
- "Walk me through the exact loop invariant"
- "What's the time complexity and why?"
- "How would you handle the edge case where...?"
- "Describe the memory layout of your solution"

### 7.4 Hallucination Handling
- Curated question bank reduces core question errors
- If candidate challenges ("I think that's incorrect"):
  - Agent acknowledges and pivots: "You may be right, let's move on to..."
  - Never defends potentially wrong claims
  - Challenge is logged as candidate signal

---

## 8. Conflict Resolution Logic

Priority order when inputs conflict:

1. **Confirmed weak areas** (from in-session evidence)
2. **Candidate-declared weak areas**
3. **Resume-derived risk areas** (lower weight)
4. **General interview coverage**

Candidate preference NEVER suppresses a confirmed weakness.

---

## 9. Learning Loop

### 9.1 Cross-Session Tracking
- **State**: Server-side per-user (SQLite)
- **Retention**: Structured summaries only (not full transcripts)
- Skills scores, key moments, performance trends

### 9.2 Weak Area Resolution
- **Method**: LLM judgment based on overall performance
- Resolved weak areas deprioritized in future sessions
- Persisting weak areas escalated

### 9.3 Carryover Rules
- Candidate can update weak-area list each session
- Progress measured by:
  - Reduction in candidate-declared weaknesses
  - Convergence between self-assessment and system diagnosis

### 9.4 Resume Handling
- Per-session only (re-upload each time, not stored permanently)
- Single profile per account (no multiple prep tracks)

---

## 10. Feedback Report

### 10.1 Timing & Delivery
- **Generation**: Immediate, synchronous (candidate waits)
- **Format**: Markdown (.md file)
- **Access**: Both in-browser view + download option

### 10.2 Report Contents

**A. Structured Scorecard**
- Per-dimension scores for each topic covered
- Overall session score
- Domain-specific breakdowns

**B. Detailed Narrative Analysis**
- Multiple paragraphs of comprehensive analysis
- Strengths identified
- Weaknesses confirmed/discovered
- Specific improvement recommendations

**C. Candidate-Declared Weak Area Assessment**
For each declared weak area:
- Status: Confirmed / Overestimated / Already Strong
- Evidence from session
- Recommendation

**D. Depth Assessment**
- Requested depth level
- Achieved / Exceeded / Reduced (with reason)

**E. Persona Impact**
- How chosen persona affected performance
- Recommendations for next session's persona

**F. Summarized Transcript Excerpts**
- Key moments only (not full transcript)
- Highlighted strong and weak exchanges
- Context around critical decision points

**G. Next Steps**
- What to change in next session's configuration
- Specific topics to study
- Suggested resources

---

## 11. Technical Architecture

### 11.1 Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python FastAPI |
| **Frontend** | React |
| **Database** | SQLite (local) |
| **Voice** | Azure OpenAI Realtime API |
| **Resume Parsing** | Azure Document Intelligence (raw text → LLM) |
| **Authentication** | Email/password only |

### 11.2 API Design
- **Structure**: Versioned endpoints (`/v1/sessions`, `/v1/users`, etc.)
- **REST**: Resource-based design
- **WebSocket**: For real-time voice session

### 11.3 Session State Management
- **Location**: In-memory on server
- **Scope**: Lost on server restart (acceptable for local dev)
- **Reconnection**: Auto-reconnect with context preservation

### 11.4 Azure OpenAI Realtime Integration
- **Routing**: Backend proxy (frontend does not connect directly)
- **Flow**: React → FastAPI WebSocket → Azure OpenAI Realtime
- **Benefits**: Auth control, logging, session management

### 11.5 Deployment
- **Target**: Local only (no cloud deployment for MVP)
- **Scale**: < 100 concurrent users

### 11.6 Error Handling
- Azure API outage: Show error message (no fallback)
- STT errors: Context-aware correction by LLM
- Network drops: Auto-reconnect, resume session

---

## 12. UI/UX Specification

### 12.1 Session Interface Layout
```
+---------------------------+---------------------------+
|                           |                           |
|    Audio Waveform /       |    Live Transcript        |
|    Avatar Animation       |    (Chat-like view)       |
|                           |                           |
|    [Mute] [End Session]   |    [Scrollable history]   |
|                           |                           |
+---------------------------+---------------------------+
```

- Left panel: Audio visualization or avatar
- Right panel: Real-time transcript of conversation

### 12.2 Pre-Session Configuration
1. Resume upload (drag-drop or file picker)
2. Weak areas input (free text or tag selection)
3. Persona selection (5 options with descriptions)
4. Depth mode selection (3 options)
5. Domain selection (optional - system can choose)

### 12.3 Post-Session
- Markdown report rendered in-browser
- Download button for .md file
- No dashboard - sessions are self-contained

### 12.4 Meta-Questions Handling
If candidate asks "How am I doing?" mid-session:
- Agent defers: "Let's discuss that at the end"
- Keeps session focused on practice

---

## 13. Skill Trees (Reference Structure)

### 13.1 Coding Domain
```
Coding
├── Arrays & Strings
│   ├── Two Pointers
│   ├── Sliding Window
│   └── Prefix Sums
├── Trees & Graphs
│   ├── Tree Traversals
│   ├── Graph Search (BFS/DFS)
│   └── Shortest Paths
├── Dynamic Programming
│   ├── 1D DP
│   ├── 2D DP
│   └── State Machine DP
├── System Coding
│   ├── API Design
│   ├── Testing Strategies
│   └── Debugging Approaches
└── [Additional categories...]
```

### 13.2 System Design Domain
```
System Design
├── Scaling Concepts
│   ├── Horizontal vs Vertical
│   ├── Load Balancing
│   └── Caching Strategies
├── Data Storage
│   ├── SQL vs NoSQL
│   ├── Sharding
│   └── Replication
├── Consistency & Availability
│   ├── CAP Theorem
│   ├── Eventual Consistency
│   └── Consensus Protocols
├── Reliability
│   ├── Fault Tolerance
│   ├── Circuit Breakers
│   └── Monitoring
└── [Additional categories...]
```

### 13.3 ML Domain
```
Machine Learning
├── Classification
│   ├── Logistic Regression
│   ├── Decision Trees
│   └── Neural Networks
├── Regression
│   ├── Linear Regression
│   ├── Regularization
│   └── Feature Engineering
├── NLP
│   ├── Text Preprocessing
│   ├── Embeddings
│   └── Transformers
├── Computer Vision
│   ├── CNNs
│   ├── Object Detection
│   └── Image Segmentation
├── MLOps
│   ├── Model Serving
│   ├── Monitoring & Drift
│   └── Pipeline Orchestration
└── [Additional categories...]
```

---

## 14. Persona System Prompts (Summary)

Each persona has a distinct system prompt controlling:

### 14.1 Friendly / Coach
- Warm, encouraging tone
- Yields immediately on interruption
- Allows longer answers
- Celebrates progress
- Still probes weak areas (supportively)

### 14.2 Neutral / Standard
- Professional, balanced
- Standard interrupt handling
- Moderate answer length tolerance
- Default behaviors

### 14.3 Aggressive / Stress
- Challenging, direct
- Pushes back on interruption
- Cuts off rambling
- As tough as real difficult interviews
- Never personal attacks, only idea challenges

### 14.4 FAANG-style
- Structured bar-raiser format
- Higher difficulty baseline
- Time pressure: "Let's move faster"
- Leadership principles integration
- Behavioral hooks

### 14.5 Startup / Rapid-fire
- Fast-paced, breadth-focused
- "How would you ship this fast?"
- Practical/scrappy emphasis
- Culture fit questions
- Adaptability assessment

---

## 15. Implementation Priority

All features are **launch-blocking** (full vision from day 1):

| Category | Features |
|----------|----------|
| **Domains** | All 3 (Coding, System Design, ML) |
| **Personas** | All 5 |
| **Learning Loop** | Cross-session tracking |
| **Feedback** | Full report with all sections |
| **Voice** | Real-time with Azure OpenAI |

---

## 16. Non-Requirements (Explicitly Out of Scope)

| Feature | Status |
|---------|--------|
| Live code execution | Not included |
| Diagram/whiteboard | Not included |
| Multi-language support | English only |
| Mobile apps | Web only |
| Dashboard / analytics | Not for MVP |
| Admin UI | Later phase |
| Scheduling system | Instant start only |
| Accessibility (WCAG) | Not for MVP |
| Cloud deployment | Local only |
| GDPR/SOC2 compliance | Not for MVP |
| Fallback voice providers | No fallback |
| Bad actor detection | System ignores, continues normally |

---

## 17. Success Metrics

### 17.1 Product Principle
> "The best prep system teaches candidates **what they misjudged about themselves** and **what to fix next with confidence**."

### 17.2 Key Metrics
- Convergence between self-assessment and system diagnosis
- Reduction in candidate-declared weaknesses over sessions
- Feedback report actionability (do recommendations lead to improvement?)
- Session completion rate
- Return usage

---

## 18. Technical Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Azure Realtime API latency | Native multimodal avoids hop latency |
| STT transcription errors | LLM context-aware correction |
| Question quality (hallucination) | Curated question bank for core questions |
| Session state loss | In-memory acceptable for local dev |
| Scale limitations (SQLite) | Migration path to Postgres when needed |

---

## 19. Future Considerations (Post-MVP)

- Cloud deployment (Azure Container Apps)
- Admin interface for question curation
- Dashboard with progress visualization
- Multi-language support
- Mobile applications
- Compliance certifications
- Alternative voice providers (failover)
- Live coding integration
- Whiteboard/diagram support

---

**End of Technical Specification**
