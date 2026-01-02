from app.personas.friendly import FRIENDLY_PROMPT
from app.personas.neutral import NEUTRAL_PROMPT
from app.personas.aggressive import AGGRESSIVE_PROMPT
from app.personas.faang import FAANG_PROMPT
from app.personas.startup import STARTUP_PROMPT


PERSONA_PROMPTS = {
    "friendly": FRIENDLY_PROMPT,
    "neutral": NEUTRAL_PROMPT,
    "aggressive": AGGRESSIVE_PROMPT,
    "faang": FAANG_PROMPT,
    "startup": STARTUP_PROMPT
}


def get_persona_prompt(persona: str) -> str:
    """Get the system prompt for a given persona."""
    return PERSONA_PROMPTS.get(persona, NEUTRAL_PROMPT)


__all__ = [
    "get_persona_prompt",
    "PERSONA_PROMPTS",
    "FRIENDLY_PROMPT",
    "NEUTRAL_PROMPT",
    "AGGRESSIVE_PROMPT",
    "FAANG_PROMPT",
    "STARTUP_PROMPT"
]
