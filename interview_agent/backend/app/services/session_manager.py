from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


@dataclass
class TranscriptEntry:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    audio_duration_ms: Optional[int] = None


@dataclass
class SessionState:
    session_id: int
    user_id: int
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Real-time state
    is_connected: bool = False
    is_speaking: bool = False
    current_topic: Optional[str] = None
    current_domain: Optional[str] = None

    # Transcript
    transcript: List[TranscriptEntry] = field(default_factory=list)

    # Evaluation signals
    follow_up_failures: int = 0
    total_follow_ups: int = 0
    response_latencies: List[int] = field(default_factory=list)  # in ms
    filler_word_count: int = 0

    # Topic tracking
    topics_covered: List[str] = field(default_factory=list)
    weak_signals: Dict[str, float] = field(default_factory=dict)  # topic -> weakness score


class SessionManager:
    """In-memory session state manager."""

    def __init__(self):
        self._sessions: Dict[int, SessionState] = {}
        self._user_sessions: Dict[int, int] = {}  # user_id -> session_id
        self._lock = asyncio.Lock()

    def create_session(self, session_id: int, user_id: int) -> SessionState:
        """Create a new session state."""
        state = SessionState(session_id=session_id, user_id=user_id)
        self._sessions[session_id] = state
        self._user_sessions[user_id] = session_id
        return state

    def get_session(self, session_id: int) -> Optional[SessionState]:
        """Get session state by ID."""
        return self._sessions.get(session_id)

    def get_user_session(self, user_id: int) -> Optional[SessionState]:
        """Get active session for a user."""
        session_id = self._user_sessions.get(user_id)
        if session_id:
            return self._sessions.get(session_id)
        return None

    def end_session(self, session_id: int) -> Optional[SessionState]:
        """End and remove a session."""
        state = self._sessions.pop(session_id, None)
        if state:
            self._user_sessions.pop(state.user_id, None)
        return state

    def add_transcript_entry(
        self,
        session_id: int,
        role: str,
        content: str,
        audio_duration_ms: Optional[int] = None
    ):
        """Add a transcript entry to the session."""
        state = self._sessions.get(session_id)
        if state:
            entry = TranscriptEntry(
                role=role,
                content=content,
                timestamp=datetime.utcnow(),
                audio_duration_ms=audio_duration_ms
            )
            state.transcript.append(entry)

    def update_speaking_state(self, session_id: int, is_speaking: bool):
        """Update whether the user is currently speaking."""
        state = self._sessions.get(session_id)
        if state:
            state.is_speaking = is_speaking

    def set_connection_state(self, session_id: int, is_connected: bool):
        """Update connection state."""
        state = self._sessions.get(session_id)
        if state:
            state.is_connected = is_connected

    def record_follow_up_result(self, session_id: int, success: bool):
        """Record whether a follow-up question was answered successfully."""
        state = self._sessions.get(session_id)
        if state:
            state.total_follow_ups += 1
            if not success:
                state.follow_up_failures += 1

    def record_response_latency(self, session_id: int, latency_ms: int):
        """Record response latency."""
        state = self._sessions.get(session_id)
        if state:
            state.response_latencies.append(latency_ms)

    def update_weak_signal(self, session_id: int, topic: str, score: float):
        """Update weakness signal for a topic."""
        state = self._sessions.get(session_id)
        if state:
            # Use exponential moving average
            current = state.weak_signals.get(topic, 0.5)
            state.weak_signals[topic] = 0.7 * score + 0.3 * current

    def mark_topic_covered(self, session_id: int, topic: str):
        """Mark a topic as covered."""
        state = self._sessions.get(session_id)
        if state and topic not in state.topics_covered:
            state.topics_covered.append(topic)

    def get_transcript_summary(self, session_id: int) -> str:
        """Get a summary of the transcript."""
        state = self._sessions.get(session_id)
        if not state:
            return ""

        lines = []
        for entry in state.transcript:
            prefix = "Candidate" if entry.role == "user" else "Interviewer"
            lines.append(f"{prefix}: {entry.content}")

        return "\n\n".join(lines)


# Global session manager instance
session_manager = SessionManager()
