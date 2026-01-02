from typing import List, Optional, AsyncGenerator
import asyncio
import json
import base64

from app.config import get_settings
from app.personas import get_persona_prompt

settings = get_settings()


class AzureRealtimeClient:
    """
    Client for Azure OpenAI Realtime API.

    Handles WebSocket connection to Azure for real-time voice conversation.
    """

    def __init__(
        self,
        session_id: int,
        persona: str,
        depth_mode: str,
        domains: List[str],
        declared_weak_areas: List[str],
        resume_text: Optional[str] = None
    ):
        self.session_id = session_id
        self.persona = persona
        self.depth_mode = depth_mode
        self.domains = domains
        self.declared_weak_areas = declared_weak_areas
        self.resume_text = resume_text

        self._connection = None
        self._connected = False
        self._event_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self):
        """Establish connection to Azure OpenAI Realtime API."""
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            # Development mode - use mock responses
            self._connected = True
            asyncio.create_task(self._mock_interview())
            return

        try:
            from openai import AsyncOpenAI

            # Build WebSocket URL for Azure OpenAI
            endpoint = settings.azure_openai_endpoint.replace("https://", "wss://")
            base_url = f"{endpoint}/openai/realtime?api-version={settings.azure_openai_api_version}&deployment={settings.azure_openai_deployment}"

            client = AsyncOpenAI(
                base_url=base_url,
                api_key=settings.azure_openai_api_key
            )

            # Connect to realtime API
            self._connection = await client.realtime.connect(
                model=settings.azure_openai_deployment
            ).__aenter__()

            # Configure session
            system_prompt = self._build_system_prompt()
            await self._connection.session.update(session={
                "instructions": system_prompt,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": settings.silence_detection_ms
                },
                "tools": [],
                "voice": "alloy"
            })

            self._connected = True

            # Start receiving events
            asyncio.create_task(self._receive_loop())

        except ImportError:
            # openai package not installed with realtime support
            self._connected = True
            asyncio.create_task(self._mock_interview())
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Azure Realtime: {e}")

    async def disconnect(self):
        """Close the connection."""
        self._connected = False
        if self._connection:
            await self._connection.__aexit__(None, None, None)
            self._connection = None

    async def send_audio(self, audio_data: bytes):
        """Send audio data to Azure."""
        if not self._connected:
            return

        if self._connection:
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_data).decode("utf-8")
            await self._connection.input_audio_buffer.append(audio=audio_b64)

    async def receive_events(self) -> AsyncGenerator[dict, None]:
        """Receive events from Azure Realtime."""
        while self._connected:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                yield event
            except asyncio.TimeoutError:
                continue

    async def _receive_loop(self):
        """Background task to receive events from Azure."""
        if not self._connection:
            return

        try:
            async for event in self._connection:
                parsed_event = self._parse_event(event)
                if parsed_event:
                    await self._event_queue.put(parsed_event)
        except Exception as e:
            await self._event_queue.put({
                "type": "error",
                "message": str(e)
            })

    def _parse_event(self, event) -> Optional[dict]:
        """Parse Azure Realtime event into our protocol."""
        event_type = event.type

        if event_type == "response.audio.delta":
            return {
                "type": "audio",
                "data": event.delta
            }

        elif event_type == "response.audio_transcript.delta":
            return {
                "type": "transcript",
                "role": "assistant",
                "text": event.delta
            }

        elif event_type == "conversation.item.input_audio_transcription.completed":
            return {
                "type": "transcript",
                "role": "user",
                "text": event.transcript
            }

        elif event_type == "input_audio_buffer.speech_started":
            return {
                "type": "turn_detection",
                "is_speaking": True
            }

        elif event_type == "input_audio_buffer.speech_stopped":
            return {
                "type": "turn_detection",
                "is_speaking": False
            }

        elif event_type == "error":
            return {
                "type": "error",
                "message": event.error.message if hasattr(event, 'error') else "Unknown error"
            }

        return None

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the interview session."""
        # Get base persona prompt
        persona_prompt = get_persona_prompt(self.persona)

        # Add context about the session
        context_parts = [
            persona_prompt,
            "",
            "## Session Context",
            f"Depth Mode: {self.depth_mode}",
            f"Domains to cover: {', '.join(self.domains)}",
        ]

        if self.declared_weak_areas:
            context_parts.append(f"Candidate-declared weak areas: {', '.join(self.declared_weak_areas)}")
            context_parts.append("Prioritize probing these declared weak areas early in the session.")

        if self.resume_text:
            context_parts.append("")
            context_parts.append("## Candidate Resume")
            context_parts.append(self.resume_text[:2000])  # Truncate if too long
            context_parts.append("")
            context_parts.append("Use the resume to gauge experience level and tailor question difficulty.")

        context_parts.extend([
            "",
            "## Interview Guidelines",
            "- Start immediately with interview questions - no warm-up or small talk",
            "- Use verbal drilling for coding questions (no live coding)",
            "- Ask follow-up questions to probe depth of understanding",
            "- Track which topics have been covered",
            "- If candidate asks 'How am I doing?', defer: 'Let's discuss that at the end'",
            "- Adapt difficulty based on candidate performance",
        ])

        return "\n".join(context_parts)

    async def _mock_interview(self):
        """Mock interview for development without Azure."""
        await asyncio.sleep(1)

        # Send initial greeting based on persona
        greetings = {
            "friendly": "Hi there! I'm excited to practice with you today. Let's start with something interesting - tell me about a challenging technical problem you've solved recently.",
            "neutral": "Hello. Let's begin the interview. Can you describe your experience with data structures and algorithms?",
            "aggressive": "Let's get straight to it. Walk me through how you'd design a system to handle 10 million concurrent users. Go.",
            "faang": "Welcome to this technical interview. We have limited time, so let's dive right in. Tell me about a time you had to make a difficult technical decision under pressure.",
            "startup": "Hey! We move fast here. If I gave you a week to ship a user authentication system from scratch, how would you approach it?"
        }

        greeting = greetings.get(self.persona, greetings["neutral"])

        await self._event_queue.put({
            "type": "transcript",
            "role": "assistant",
            "text": greeting
        })

        # Keep connection alive
        while self._connected:
            await asyncio.sleep(1)
