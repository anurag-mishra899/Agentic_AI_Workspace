from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class SkillStatus(str, Enum):
    WEAK = "weak"
    IMPROVING = "improving"
    STRONG = "strong"
    UNKNOWN = "unknown"


@dataclass
class TopicScore:
    topic: str
    subtopic: Optional[str]
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    evidence: List[str]  # Key observations


@dataclass
class DomainScore:
    domain: str
    overall_score: float
    topic_scores: List[TopicScore]
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class SessionEvaluation:
    session_id: int
    domain_scores: List[DomainScore]
    overall_score: float
    declared_vs_actual: Dict[str, str]  # weak_area -> assessment
    depth_achieved: str  # surface, interview_ready, expert
    time_spent_minutes: float


class EvaluationService:
    """
    Evaluates candidate performance using multi-signal fusion.

    Signals:
    - Semantic analysis of answers (high weight)
    - Follow-up failure rate (high weight)
    - Verbal cues - filler words, tone (medium weight)
    - Response latency (low weight)
    """

    # Signal weights
    WEIGHTS = {
        "semantic": 0.45,
        "follow_up": 0.30,
        "verbal_cues": 0.15,
        "latency": 0.10
    }

    def __init__(self):
        pass

    def evaluate_session(
        self,
        session_id: int,
        transcript: List[dict],
        declared_weak_areas: List[str],
        domains: List[str],
        depth_mode: str,
        session_state: dict
    ) -> SessionEvaluation:
        """
        Evaluate the complete session and generate scores.

        Args:
            session_id: The session ID
            transcript: List of transcript entries
            declared_weak_areas: Candidate-declared weak areas
            domains: Domains covered
            depth_mode: Requested depth level
            session_state: In-memory session state data

        Returns:
            SessionEvaluation with comprehensive scoring
        """
        domain_scores = []

        for domain in domains:
            domain_score = self._evaluate_domain(
                domain, transcript, session_state
            )
            domain_scores.append(domain_score)

        # Calculate overall score
        if domain_scores:
            overall_score = sum(d.overall_score for d in domain_scores) / len(domain_scores)
        else:
            overall_score = 0.0

        # Compare declared vs actual weak areas
        declared_vs_actual = self._compare_declared_actual(
            declared_weak_areas, domain_scores
        )

        # Determine depth achieved
        depth_achieved = self._assess_depth(transcript, depth_mode)

        # Calculate time spent
        time_spent = self._calculate_time(transcript)

        return SessionEvaluation(
            session_id=session_id,
            domain_scores=domain_scores,
            overall_score=overall_score,
            declared_vs_actual=declared_vs_actual,
            depth_achieved=depth_achieved,
            time_spent_minutes=time_spent
        )

    def _evaluate_domain(
        self,
        domain: str,
        transcript: List[dict],
        session_state: dict
    ) -> DomainScore:
        """Evaluate performance for a specific domain."""
        # Extract relevant exchanges for this domain
        # In production, this would use LLM-as-judge

        # Mock evaluation for development
        topic_scores = []
        strengths = []
        weaknesses = []

        # Calculate follow-up failure rate
        total_follow_ups = session_state.get("total_follow_ups", 0)
        follow_up_failures = session_state.get("follow_up_failures", 0)

        if total_follow_ups > 0:
            follow_up_success_rate = 1 - (follow_up_failures / total_follow_ups)
        else:
            follow_up_success_rate = 0.5  # Neutral if no follow-ups

        # Mock scores based on signals
        overall_score = (
            0.6 * follow_up_success_rate +  # Base on follow-up performance
            0.4 * 0.7  # Placeholder for semantic analysis
        )

        # Determine strengths and weaknesses
        if follow_up_success_rate > 0.7:
            strengths.append(f"Strong follow-up handling in {domain}")
        else:
            weaknesses.append(f"Struggled with follow-up questions in {domain}")

        return DomainScore(
            domain=domain,
            overall_score=overall_score,
            topic_scores=topic_scores,
            strengths=strengths,
            weaknesses=weaknesses
        )

    def _compare_declared_actual(
        self,
        declared_weak_areas: List[str],
        domain_scores: List[DomainScore]
    ) -> Dict[str, str]:
        """
        Compare declared weak areas against actual performance.

        Returns assessment for each declared area:
        - confirmed: Weakness was real
        - overestimated: Performed better than expected
        - unknown: Not enough data
        """
        results = {}

        for weak_area in declared_weak_areas:
            # In production, this would use semantic matching
            # to find relevant topic scores and assess
            results[weak_area] = "confirmed"  # Placeholder

        return results

    def _assess_depth(self, transcript: List[dict], requested_depth: str) -> str:
        """Assess the depth level achieved in the session."""
        # Count follow-up depth (how many levels of drilling)
        # In production, analyze conversation structure

        # Mock: return requested depth for now
        return requested_depth

    def _calculate_time(self, transcript: List[dict]) -> float:
        """Calculate session duration in minutes."""
        if not transcript:
            return 0.0

        # In production, use actual timestamps
        # Mock: estimate based on transcript length
        return len(transcript) * 0.5  # Assume 30 seconds per exchange


class LLMJudge:
    """
    LLM-based evaluation of answers.

    Uses GPT to assess answer quality against rubrics.
    """

    EVALUATION_PROMPT = """You are an expert technical interviewer evaluating a candidate's answer.

Question: {question}
Candidate's Answer: {answer}

Rubric:
{rubric}

Evaluate the answer on each rubric dimension on a scale of 1-5.
Provide specific evidence for your scores.

Output format:
{{
  "scores": {{
    "dimension1": {{"score": X, "evidence": "..."}},
    ...
  }},
  "overall_score": X.X,
  "strengths": ["...", "..."],
  "areas_for_improvement": ["...", "..."]
}}
"""

    def __init__(self):
        pass

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        rubric: Dict[str, str]
    ) -> dict:
        """
        Evaluate a single answer using LLM.

        In production, this calls Azure OpenAI GPT-4.
        """
        # Placeholder for LLM call
        # In production:
        # 1. Format prompt with question, answer, rubric
        # 2. Call GPT-4 for evaluation
        # 3. Parse structured response

        return {
            "scores": {},
            "overall_score": 0.7,
            "strengths": [],
            "areas_for_improvement": []
        }


# Global evaluation service instance
evaluation_service = EvaluationService()
