from typing import List, Optional
from datetime import datetime

from app.services.evaluation import SessionEvaluation, DomainScore


class FeedbackReportGenerator:
    """Generates comprehensive feedback reports in Markdown format."""

    def generate_report(
        self,
        evaluation: SessionEvaluation,
        persona: str,
        depth_mode: str,
        declared_weak_areas: List[str],
        transcript_summary: str,
        resume_provided: bool
    ) -> str:
        """
        Generate a complete feedback report.

        Args:
            evaluation: Session evaluation results
            persona: Persona used for the session
            depth_mode: Requested depth level
            declared_weak_areas: Candidate-declared weak areas
            transcript_summary: Summarized transcript
            resume_provided: Whether resume was uploaded

        Returns:
            Markdown-formatted feedback report
        """
        sections = [
            self._header(),
            self._session_summary(evaluation, persona, depth_mode),
            self._scorecard(evaluation),
            self._narrative_analysis(evaluation),
            self._weak_area_assessment(evaluation, declared_weak_areas),
            self._depth_assessment(evaluation, depth_mode),
            self._persona_impact(persona, evaluation),
            self._key_moments(transcript_summary),
            self._next_steps(evaluation, declared_weak_areas),
            self._footer()
        ]

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Generate report header."""
        return f"""# Interview Practice Feedback Report

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

---"""

    def _session_summary(
        self,
        evaluation: SessionEvaluation,
        persona: str,
        depth_mode: str
    ) -> str:
        """Generate session summary section."""
        domains = ", ".join(d.domain.replace("_", " ").title() for d in evaluation.domain_scores)
        overall_pct = int(evaluation.overall_score * 100)

        return f"""## Session Summary

| Metric | Value |
|--------|-------|
| **Overall Score** | {overall_pct}% |
| **Domains Covered** | {domains} |
| **Persona** | {persona.title()} |
| **Depth Mode** | {depth_mode.replace("_", " ").title()} |
| **Duration** | {evaluation.time_spent_minutes:.0f} minutes |"""

    def _scorecard(self, evaluation: SessionEvaluation) -> str:
        """Generate structured scorecard section."""
        lines = ["## Structured Scorecard"]

        for domain_score in evaluation.domain_scores:
            domain_name = domain_score.domain.replace("_", " ").title()
            score_pct = int(domain_score.overall_score * 100)
            score_bar = self._score_bar(domain_score.overall_score)

            lines.append(f"\n### {domain_name}: {score_pct}%")
            lines.append(f"{score_bar}")

            if domain_score.topic_scores:
                lines.append("\n| Topic | Score | Confidence |")
                lines.append("|-------|-------|------------|")
                for topic in domain_score.topic_scores:
                    topic_pct = int(topic.score * 100)
                    conf_pct = int(topic.confidence * 100)
                    lines.append(f"| {topic.topic} | {topic_pct}% | {conf_pct}% |")

        return "\n".join(lines)

    def _score_bar(self, score: float) -> str:
        """Generate a visual score bar."""
        filled = int(score * 20)
        empty = 20 - filled
        return f"`[{'█' * filled}{'░' * empty}]`"

    def _narrative_analysis(self, evaluation: SessionEvaluation) -> str:
        """Generate detailed narrative analysis."""
        lines = ["## Detailed Analysis"]

        # Strengths
        all_strengths = []
        for domain_score in evaluation.domain_scores:
            all_strengths.extend(domain_score.strengths)

        if all_strengths:
            lines.append("\n### Strengths Identified")
            for strength in all_strengths:
                lines.append(f"- {strength}")

        # Weaknesses
        all_weaknesses = []
        for domain_score in evaluation.domain_scores:
            all_weaknesses.extend(domain_score.weaknesses)

        if all_weaknesses:
            lines.append("\n### Areas for Improvement")
            for weakness in all_weaknesses:
                lines.append(f"- {weakness}")

        # Overall analysis
        overall_pct = evaluation.overall_score * 100
        if overall_pct >= 80:
            assessment = "You demonstrated strong technical competence across the covered domains. Your answers showed depth of understanding and you handled follow-up questions well."
        elif overall_pct >= 60:
            assessment = "You showed solid foundational knowledge with some areas for improvement. Focus on the specific topics identified below to strengthen your preparation."
        else:
            assessment = "There are several areas that need focused practice. Review the recommendations below and consider additional study in the identified weak areas."

        lines.append(f"\n### Overall Assessment\n\n{assessment}")

        return "\n".join(lines)

    def _weak_area_assessment(
        self,
        evaluation: SessionEvaluation,
        declared_weak_areas: List[str]
    ) -> str:
        """Assess declared weak areas against performance."""
        lines = ["## Declared Weak Areas Assessment"]

        if not declared_weak_areas:
            lines.append("\n*No weak areas were declared for this session.*")
            return "\n".join(lines)

        lines.append("\n| Declared Area | Assessment | Evidence |")
        lines.append("|---------------|------------|----------|")

        for area in declared_weak_areas:
            assessment = evaluation.declared_vs_actual.get(area, "unknown")
            if assessment == "confirmed":
                icon = "🔴"
                desc = "Confirmed Weakness"
                evidence = "Performance below expected level"
            elif assessment == "overestimated":
                icon = "🟢"
                desc = "Stronger Than Expected"
                evidence = "Performed well in this area"
            else:
                icon = "⚪"
                desc = "Not Assessed"
                evidence = "Insufficient data"

            lines.append(f"| {area} | {icon} {desc} | {evidence} |")

        return "\n".join(lines)

    def _depth_assessment(self, evaluation: SessionEvaluation, requested: str) -> str:
        """Assess depth level achieved."""
        achieved = evaluation.depth_achieved

        if achieved == requested:
            status = "✅ Achieved"
            explanation = "You successfully handled questions at your requested depth level."
        elif achieved == "expert" and requested != "expert":
            status = "⬆️ Exceeded"
            explanation = "You demonstrated capability beyond your requested depth level."
        else:
            status = "⬇️ Adjusted"
            explanation = "The depth was adjusted based on your performance."

        return f"""## Depth Assessment

**Requested Level:** {requested.replace("_", " ").title()}
**Achieved Level:** {achieved.replace("_", " ").title()}
**Status:** {status}

{explanation}"""

    def _persona_impact(self, persona: str, evaluation: SessionEvaluation) -> str:
        """Analyze how the persona affected performance."""
        persona_insights = {
            "friendly": "The supportive coaching style may have helped you feel more comfortable exploring ideas. Consider trying a more challenging persona to build stress resilience.",
            "neutral": "The balanced interview style provided a realistic baseline experience. Your performance reflects your abilities under normal conditions.",
            "aggressive": "You practiced under high-pressure conditions. Any discomfort you felt is normal - this persona simulates the toughest real interviews.",
            "faang": "You experienced the structured, high-bar format used at top tech companies. This preparation is valuable for competitive interviews.",
            "startup": "The fast-paced, practical focus tested your ability to think quickly and prioritize. This reflects real startup interview dynamics."
        }

        insight = persona_insights.get(persona, "")

        recommendation = ""
        if evaluation.overall_score < 0.6:
            if persona in ["aggressive", "faang"]:
                recommendation = "Consider practicing with a friendlier persona to build confidence before returning to challenging formats."
            else:
                recommendation = "Focus on strengthening fundamentals before increasing difficulty."
        else:
            if persona in ["friendly", "neutral"]:
                recommendation = "You may be ready for more challenging personas like FAANG or Aggressive to further stretch your abilities."

        return f"""## Persona Impact

**Persona Used:** {persona.title()}

{insight}

**Recommendation:** {recommendation}"""

    def _key_moments(self, transcript_summary: str) -> str:
        """Include key transcript moments."""
        if not transcript_summary:
            return """## Key Moments

*Transcript summary not available.*"""

        # Truncate if too long
        if len(transcript_summary) > 2000:
            transcript_summary = transcript_summary[:2000] + "\n\n*[Truncated for brevity]*"

        return f"""## Key Moments

<details>
<summary>Click to expand transcript excerpts</summary>

{transcript_summary}

</details>"""

    def _next_steps(
        self,
        evaluation: SessionEvaluation,
        declared_weak_areas: List[str]
    ) -> str:
        """Generate actionable next steps."""
        lines = ["## Next Steps"]

        # Session configuration suggestions
        lines.append("\n### For Your Next Session")

        if evaluation.overall_score < 0.6:
            lines.append("- Consider focusing on a single domain for deeper practice")
            lines.append("- Start with Surface Review depth to build foundations")
        elif evaluation.overall_score < 0.8:
            lines.append("- Continue with Interview-Ready depth")
            lines.append("- Focus sessions on identified weak areas")
        else:
            lines.append("- Try Expert/Stress-Test depth for additional challenge")
            lines.append("- Explore less familiar domains")

        # Study recommendations
        lines.append("\n### Topics to Study")

        all_weaknesses = []
        for domain_score in evaluation.domain_scores:
            all_weaknesses.extend(domain_score.weaknesses)

        if all_weaknesses:
            for weakness in all_weaknesses[:5]:  # Top 5
                lines.append(f"- {weakness}")
        else:
            lines.append("- Continue practicing across all domains")
            lines.append("- Focus on edge cases and optimization")

        # Confirmed weak areas
        confirmed_weak = [
            area for area, status in evaluation.declared_vs_actual.items()
            if status == "confirmed"
        ]
        if confirmed_weak:
            lines.append("\n### Confirmed Weak Areas (Prioritize)")
            for area in confirmed_weak:
                lines.append(f"- {area}")

        return "\n".join(lines)

    def _footer(self) -> str:
        """Generate report footer."""
        return """---

*This report was generated by Interview Agent. Continue practicing to track your progress over time.*

**Remember:** The goal is not perfection, but continuous improvement. Each session helps you identify what to work on next.
"""


# Global feedback generator instance
feedback_generator = FeedbackReportGenerator()
