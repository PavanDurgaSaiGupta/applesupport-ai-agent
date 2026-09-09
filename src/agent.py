"""
Unified AppleSupportAgent Pipeline.

Combines intent classification, historical resolution retrieval,
reasoned escalation evaluation, and grounded reply drafting into
a single production-ready agent.
"""

import time
import logging
from typing import Dict, Any, Optional

from src.data_processor import clean_tweet_text
from src.intent_classifier import IntentClassifier, train_intent_classifier
from src.retriever import HistoricalRetriever, get_retriever
from src.escalation_engine import EscalationEngine
from src.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class AppleSupportAgent:
    """End-to-End AI Customer Support Agent for @AppleSupport."""

    def __init__(
        self,
        classifier: Optional[IntentClassifier] = None,
        retriever: Optional[HistoricalRetriever] = None,
        escalation_engine: Optional[EscalationEngine] = None,
        response_generator: Optional[ResponseGenerator] = None,
    ):
        if classifier is None:
            self.classifier = train_intent_classifier()
        else:
            self.classifier = classifier

        self.retriever = retriever if retriever is not None else get_retriever()
        self.escalation_engine = escalation_engine if escalation_engine is not None else EscalationEngine()
        self.response_generator = response_generator if response_generator is not None else ResponseGenerator()

    def process(self, raw_customer_tweet: str) -> Dict[str, Any]:
        """
        Executes the full triage and drafting pipeline for an incoming customer tweet.
        
        Returns:
            {
                "input_text": str,
                "cleaned_text": str,
                "intent": str,
                "intent_confidence": float,
                "intent_distribution": Dict[str, float],
                "escalation_decision": "AUTO_HANDLE" | "ESCALATE",
                "escalation_reason": str,
                "escalation_confidence": float,
                "drafted_reply": str,
                "retrieved_contexts": List[Dict[str, Any]],
                "latency_ms": float
            }
        """
        t0 = time.time()
        
        # 1. Cleaning & Preprocessing
        cleaned_text = clean_tweet_text(raw_customer_tweet, remove_handles=True)
        if not cleaned_text:
            cleaned_text = raw_customer_tweet.strip()

        # 2. Intent Classification
        intent, intent_conf, prob_dist = self.classifier.predict_single(cleaned_text)

        # 3. Grounded Historical Resolution Retrieval
        retrieved_contexts = self.retriever.retrieve(cleaned_text, top_k=3)

        # 4. Escalation Evaluation with Stated Reason
        escalation_res = self.escalation_engine.evaluate(
            customer_query=cleaned_text,
            predicted_intent=intent,
            intent_confidence=intent_conf
        )

        # 5. Brand-Aligned Grounded Reply Drafting
        drafted_reply = self.response_generator.generate_reply(
            customer_query=cleaned_text,
            predicted_intent=intent,
            escalation_decision=escalation_res["decision"],
            escalation_reason=escalation_res["reason"],
            retrieved_contexts=retrieved_contexts
        )

        latency_ms = round((time.time() - t0) * 1000, 2)
        top_score = retrieved_contexts[0]["similarity_score"] if retrieved_contexts else 0.0
        evidence_ids = [ctx.get("tweet_id") for ctx in retrieved_contexts if ctx.get("tweet_id")]

        return {
            "intent": intent,
            "intent_confidence": round(intent_conf, 4),
            "retrieval_score": round(top_score, 4),
            "escalation_decision": escalation_res["decision"],
            "escalation_reason": escalation_res["reason"],
            "evidence_ids": evidence_ids,
            "drafted_reply": drafted_reply,
            "input_text": raw_customer_tweet,
            "cleaned_text": cleaned_text,
            "intent_distribution": {k: round(v, 4) for k, v in prob_dist.items()},
            "escalation_confidence": round(escalation_res["confidence"], 4),
            "retrieved_contexts": retrieved_contexts,
            "latency_ms": latency_ms
        }

    def process_query(self, raw_customer_tweet: str) -> Dict[str, Any]:
        """Alias for process() for API compatibility."""
        return self.process(raw_customer_tweet)
