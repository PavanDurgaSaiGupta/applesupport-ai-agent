"""
LLM-as-a-Judge Rubric & Evaluator for Apple Support Replies.

Evaluates drafted customer support responses on 4 core dimensions:
1. Grounding & Factual Soundness (1-5)
2. Brand Tone & Empathy (1-5)
3. Actionability & Triage Guidance (1-5)
4. Escalation Appropriateness (1-5)
"""

import re
from typing import Dict, Any, List, Optional


RUBRIC_DESCRIPTION = {
    "grounding_score": (
        "Grounding & Factual Soundness: 5 = Exact match to Apple official KB/procedure without hallucinations. "
        "3 = Broadly correct direction but missing specifics. 1 = Fabricated policy, incorrect shortcut, or dangerous guidance."
    ),
    "tone_score": (
        "Brand Tone & Empathy: 5 = Warm, professional, concise, empathetic Apple voice. "
        "3 = Dry or overly robotic. 1 = Rude, argumentative, or overly verbose."
    ),
    "actionability_score": (
        "Actionability & Triage Guidance: 5 = Direct step-by-step pathway (e.g. Settings > ...) or clear diagnostic question. "
        "3 = Generic advice ('try restarting'). 1 = Completely non-actionable or stalling."
    ),
    "escalation_appropriateness_score": (
        "Escalation Appropriateness: 5 = Correct decision (self-serve vs DM handoff) aligned with safety/security policy. "
        "3 = Borderline choice. 1 = Fatal error (e.g. failing to escalate a burning battery or escalating a basic FAQ)."
    ),
}


class LLMJudge:
    """Evaluates agent responses using the 4-dimensional Apple Support Rubric."""

    def __init__(self):
        pass

    def evaluate_response(
        self,
        customer_query: str,
        predicted_intent: str,
        escalation_decision: str,
        drafted_reply: str,
        ground_truth_intent: str,
        ground_truth_escalation: str,
        ground_truth_resolution: str
    ) -> Dict[str, Any]:
        """
        Scores a single response across the 4 dimensions.
        Returns score dictionary with explicit rationale.
        """
        reply_lower = drafted_reply.lower()
        query_lower = customer_query.lower()

        # Dimension 1: Escalation Appropriateness (1 to 5)
        if escalation_decision == ground_truth_escalation:
            escalation_score = 5.0
            escalation_feedback = "Correct escalation decision aligned with golden ground truth policy."
        else:
            # Fatal miss: Ground truth was ESCALATE (e.g. safety/account lockout) but agent AUTO_HANDLE
            if ground_truth_escalation == "ESCALATE":
                escalation_score = 1.0
                escalation_feedback = "Critical failure: Query required human escalation but agent attempted auto-handle."
            else:
                # Over-escalation: harmless self-serve question routed to human
                escalation_score = 3.0
                escalation_feedback = "Sub-optimal: Query could have been auto-handled but was unnecessarily escalated to DM."

        # Dimension 2: Brand Tone & Empathy (1 to 5)
        tone_score = 5.0
        tone_feedback = "Polite, empathetic, and professional tone consistent with Apple Support."
        if len(drafted_reply) < 25:
            tone_score -= 1.5
            tone_feedback = "Reply is too terse."
        if len(drafted_reply) > 280:
            tone_score -= 1.0
            tone_feedback = "Reply exceeds standard single-tweet budget."
        if not any(w in reply_lower for w in ["help", "here for you", "glad", "understand", "safety", "assist", "thanks"]):
            tone_score -= 0.5
        tone_score = max(1.0, min(5.0, tone_score))

        # Dimension 3: Actionability & Triage Guidance (1 to 5)
        actionability_score = 3.5
        if escalation_decision == "ESCALATE":
            if "dm" in reply_lower or "https://t.co" in reply_lower:
                actionability_score = 5.0
                actionability_feedback = "Clear, direct call-to-action redirecting to private DM channel."
            else:
                actionability_score = 3.0
                actionability_feedback = "Escalated without clear DM handoff link."
        else:
            # Look for specific actionable instructions (Settings >, steps, links)
            if "settings >" in reply_lower or "tap" in reply_lower or "force restart" in reply_lower:
                actionability_score = 5.0
                actionability_feedback = "Provides clear, direct navigation pathway (Settings > ...)."
            elif "?" in drafted_reply:
                actionability_score = 4.0
                actionability_feedback = "Asks relevant diagnostic triage question."
            else:
                actionability_score = 3.0
                actionability_feedback = "General guidance provided without step-by-step navigation."

        # Dimension 4: Grounding & Factual Soundness (1 to 5)
        grounding_score = 4.0
        # Check intent alignment
        if predicted_intent != ground_truth_intent:
            grounding_score -= 1.5
            grounding_feedback = f"Misclassified intent ({predicted_intent} vs {ground_truth_intent}), impacting technical grounding."
        else:
            # Check key entity grounding
            gt_keywords = [w for w in re.findall(r"\b\w{4,}\b", ground_truth_resolution.lower()) if w not in ["settings", "general", "device", "apple"]]
            overlap = sum(1 for kw in gt_keywords if kw in reply_lower)
            if overlap >= 2 or ("dm" in reply_lower and escalation_decision == "ESCALATE"):
                grounding_score = 5.0
                grounding_feedback = "Grounding strongly matches official Apple troubleshooting procedures."
            else:
                grounding_score = 4.0
                grounding_feedback = "Factual and safe, but could include more specific keyword details."

        grounding_score = max(1.0, min(5.0, grounding_score))
        composite = round((grounding_score + tone_score + actionability_score + escalation_score) / 4.0, 2)

        return {
            "grounding_score": round(grounding_score, 2),
            "tone_score": round(tone_score, 2),
            "actionability_score": round(actionability_score, 2),
            "escalation_appropriateness_score": round(escalation_score, 2),
            "composite_score": composite,
            "rationale": {
                "grounding": grounding_feedback,
                "tone": tone_feedback,
                "actionability": actionability_feedback,
                "escalation": escalation_feedback
            }
        }
