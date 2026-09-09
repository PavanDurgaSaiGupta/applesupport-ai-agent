"""
Baseline Models for Benchmark Comparison.

Baseline 1: Trivial Baseline (Majority intent + canned reply + length-based escalation).
Baseline 2: Simple Baseline (TF-IDF Naive Bayes + basic keyword escalation + raw nearest neighbor reply).
"""

import re
import time
from typing import Dict, Any, Optional
from src.data_processor import clean_tweet_text
from src.retriever import get_retriever

TRIVIAL_CANNED_REPLY = (
    "Thanks for reaching out to us. We are always happy to help. "
    "Send us a DM so we can look into this together. https://t.co/GDrqU22YpT"
)


class TrivialBaselineAgent:
    """
    Baseline 1: Trivial Heuristic Baseline.
    - Intent: Always predicts the dataset majority class ('SOFTWARE_UPDATE_OS')
    - Escalation: Arbitrary string length heuristic (> 100 chars -> ESCALATE)
    - Reply: Static canned Apple Support DM redirection tweet
    """

    def __init__(self, majority_intent: str = "SOFTWARE_UPDATE_OS"):
        self.majority_intent = majority_intent

    def process(self, query: str) -> Dict[str, Any]:
        t0 = time.time()
        cleaned = clean_tweet_text(query, remove_handles=True)

        # Length heuristic
        if len(cleaned) > 100:
            decision = "ESCALATE"
            reason = "Trivial heuristic: Message length exceeds 100 characters."
        else:
            decision = "AUTO_HANDLE"
            reason = "Trivial heuristic: Message length under 100 characters."

        return {
            "input_text": query,
            "intent": self.majority_intent,
            "intent_confidence": 0.5,
            "escalation_decision": decision,
            "escalation_reason": reason,
            "drafted_reply": TRIVIAL_CANNED_REPLY,
            "latency_ms": round((time.time() - t0) * 1000, 2)
        }


class SimpleBaselineAgent:
    """
    Baseline 2: Simple Standard Baseline.
    - Intent: Unigram TF-IDF Multinomial Naive Bayes without rule boosting
    - Escalation: Simple 5-keyword regex rule list
    - Reply: Raw top-1 nearest neighbor historical reply from retriever
    """

    def __init__(self, classifier=None, retriever=None):
        self.classifier = classifier
        self.retriever = retriever if retriever is not None else get_retriever()
        self.escalation_keywords = re.compile(
            r"\b(refund|stolen|broken|locked|urgent|charged|hack|fire|lawsuit)\b",
            re.IGNORECASE
        )

    def process(self, query: str) -> Dict[str, Any]:
        t0 = time.time()
        cleaned = clean_tweet_text(query, remove_handles=True)

        # Intent prediction via classifier (or fallback to unigram)
        if self.classifier:
            intent, conf, _ = self.classifier.predict_single(cleaned)
        else:
            intent = "SOFTWARE_UPDATE_OS"
            conf = 0.6

        # Keyword escalation rule
        if self.escalation_keywords.search(cleaned):
            decision = "ESCALATE"
            reason = "Simple keyword match on escalation term."
        else:
            decision = "AUTO_HANDLE"
            reason = "No escalation keyword detected."

        # Top-1 historical raw reply
        retrieved = self.retriever.retrieve(cleaned, top_k=1)
        if retrieved:
            reply = retrieved[0]["apple_reply"]
            if not reply:
                reply = TRIVIAL_CANNED_REPLY
        else:
            reply = TRIVIAL_CANNED_REPLY

        return {
            "input_text": query,
            "intent": intent,
            "intent_confidence": conf,
            "escalation_decision": decision,
            "escalation_reason": reason,
            "drafted_reply": reply,
            "latency_ms": round((time.time() - t0) * 1000, 2)
        }
