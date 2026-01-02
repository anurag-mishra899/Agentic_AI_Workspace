# Interview Agent

A real-time voice-based AI interview preparation system that provides adaptive, diagnostic interview practice across multiple domains.

## Features

- **Real-time Voice Interviews**: Uses Azure OpenAI Realtime API for natural voice conversations
- **3 Domains**: Coding (DSA + practical), System Design, ML/AI
- **5 Interview Personas**: Friendly Coach, Neutral, Aggressive/Stress, FAANG-style, Startup Rapid-fire
- **3 Depth Levels**: Surface Review, Interview-Ready, Expert/Stress-Test
- **Adaptive Difficulty**: Adjusts based on candidate performance
- **Resume Parsing**: Upload PDF resumes for personalized sessions
- **Weakness Detection**: Multi-signal fusion to identify knowledge gaps
- **Comprehensive Feedback**: Detailed Markdown reports after each session

## Architecture

![High-Level Architecture](high-level-architecture.png)

### Project Structure

```
interview_agent/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── models/    # SQLAlchemy database models
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   ├── personas/  # 5 distinct interviewer personas
│   │   └── skill_trees/ # Domain skill hierarchies
│   └── data/
│       └── questions/ # Curated question bank
└── frontend/          # React TypeScript frontend
    └── src/
        ├── pages/     # Route pages
        ├── components/ # UI components
        └── services/  # API clients
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Azure OpenAI resource with Realtime API access
- Azure Document Intelligence resource (optional, for resume parsing)

## Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

4. Run the server:
```bash
python run.py
```

The API will be available at http://localhost:8000

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/auth/register` | POST | Create new account |
| `/v1/auth/login` | POST | Get JWT token |
| `/v1/users/me` | GET | Get current user |
| `/v1/sessions` | POST | Start new interview session |
| `/v1/sessions` | GET | List user sessions |
| `/v1/sessions/{id}` | GET | Get session details |
| `/v1/sessions/{id}` | DELETE | End session early |
| `/v1/resume/parse` | POST | Upload and parse resume |
| `/v1/ws/session/{id}` | WS | Real-time voice WebSocket |

## Session Flow

1. **Configure Session**: Select persona, depth level, domains, upload resume/declare weak areas
2. **Interview**: Real-time voice conversation with AI interviewer
3. **Feedback**: Receive comprehensive Markdown report

## Development Notes

### Without Azure Credentials

The system includes mock responses for development without Azure credentials:
- Resume parsing returns a placeholder message
- Voice interview provides a text-based mock interaction

### Database

SQLite is used for local development. The database file (`interview_agent.db`) is created automatically on first run.

### WebSocket Protocol

The voice WebSocket uses a simple JSON protocol:
- Client sends: `{"type": "audio", "data": "<base64>"}` for audio
- Client sends: `{"type": "control", "action": "mute|unmute|end"}`
- Server sends: `{"type": "audio", "data": "<base64>"}` for AI audio
- Server sends: `{"type": "transcript", "role": "user|assistant", "text": "..."}`

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Azure OpenAI SDK
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **Database**: SQLite (local development)
- **Voice**: Azure OpenAI Realtime API
- **Resume Parsing**: Azure Document Intelligence

## License

Private - Interview preparation tool
