import json
import random
from pathlib import Path
from typing import List, Optional, Dict

from app.skill_trees import get_skill_tree


QUESTIONS_DIR = Path(__file__).parent.parent.parent / "data" / "questions"


def load_questions(domain: str) -> List[dict]:
    """Load questions for a domain from JSON file."""
    file_path = QUESTIONS_DIR / f"{domain}.json"
    if not file_path.exists():
        return []

    with open(file_path, "r") as f:
        return json.load(f)


def get_question(
    domain: str,
    topic: Optional[str] = None,
    subtopic: Optional[str] = None,
    difficulty: Optional[str] = None,
    exclude_ids: Optional[List[str]] = None
) -> Optional[dict]:
    """
    Get a question matching the specified criteria.

    Args:
        domain: The domain (coding, system_design, ml)
        topic: Optional topic filter
        subtopic: Optional subtopic filter
        difficulty: Optional difficulty (easy, medium, hard)
        exclude_ids: Question IDs to exclude (already asked)

    Returns:
        A question dict or None if no matching question found
    """
    questions = load_questions(domain)
    exclude_ids = exclude_ids or []

    # Filter questions
    candidates = []
    for q in questions:
        if q.get("id") in exclude_ids:
            continue
        if topic and q.get("topic") != topic:
            continue
        if subtopic and q.get("subtopic") != subtopic:
            continue
        if difficulty and q.get("difficulty") != difficulty:
            continue
        candidates.append(q)

    if not candidates:
        return None

    return random.choice(candidates)


def get_questions_for_weak_area(
    domain: str,
    weak_area: str,
    count: int = 3
) -> List[dict]:
    """
    Get questions targeting a declared weak area.

    Args:
        domain: The domain
        weak_area: The weak area description
        count: Number of questions to return

    Returns:
        List of relevant questions
    """
    questions = load_questions(domain)

    # Simple keyword matching for now
    # In production, this would use semantic search
    weak_area_lower = weak_area.lower()
    relevant = []

    for q in questions:
        text = f"{q.get('topic', '')} {q.get('subtopic', '')} {q.get('question', '')}".lower()
        if any(word in text for word in weak_area_lower.split()):
            relevant.append(q)

    # Shuffle and return requested count
    random.shuffle(relevant)
    return relevant[:count]


def get_follow_up_questions(question_id: str) -> List[str]:
    """Get follow-up questions for a given question."""
    # Search all domains for the question
    for domain in ["coding", "system_design", "ml"]:
        questions = load_questions(domain)
        for q in questions:
            if q.get("id") == question_id:
                return q.get("follow_ups", [])
    return []


def generate_follow_up(
    question: str,
    answer: str,
    domain: str
) -> str:
    """
    Generate a contextual follow-up question based on the answer.

    This is a placeholder - in production this would use LLM generation.
    """
    follow_ups = {
        "coding": [
            "What's the time complexity of your approach?",
            "How would you handle edge cases?",
            "Can you optimize this further?",
            "What data structure would make this more efficient?",
            "How would you test this solution?"
        ],
        "system_design": [
            "How would this scale to 10x the users?",
            "What happens if this component fails?",
            "How would you ensure data consistency?",
            "What are the tradeoffs of this approach?",
            "How would you monitor this system?"
        ],
        "ml": [
            "Why did you choose this model over alternatives?",
            "How would you handle class imbalance?",
            "What metrics would you use to evaluate this?",
            "How would you handle overfitting?",
            "How would you deploy this to production?"
        ]
    }

    domain_follow_ups = follow_ups.get(domain, follow_ups["coding"])
    return random.choice(domain_follow_ups)


def get_rubric(question_id: str) -> Optional[Dict]:
    """Get the evaluation rubric for a question."""
    for domain in ["coding", "system_design", "ml"]:
        questions = load_questions(domain)
        for q in questions:
            if q.get("id") == question_id:
                return q.get("rubric")
    return None
