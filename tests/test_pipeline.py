"""
Unit Tests for @AppleSupport AI Agent Pipeline.
"""

import unittest
from src.data_processor import clean_tweet_text
from src.intent_classifier import IntentClassifier, train_intent_classifier, INTENT_TAXONOMY
from src.escalation_engine import EscalationEngine
from src.retriever import HistoricalRetriever
from src.response_generator import ResponseGenerator
from src.agent import AppleSupportAgent
from src.baselines import TrivialBaselineAgent, SimpleBaselineAgent
from src.evaluator import BenchmarkEvaluator
from src.llm_judge import LLMJudge
import json
import os


class TestAppleSupportPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.classifier = train_intent_classifier(max_historical_train=1000)
        cls.retriever = HistoricalRetriever(max_entries=500)
        cls.escalation_engine = EscalationEngine()
        cls.generator = ResponseGenerator()
        cls.agent = AppleSupportAgent(
            classifier=cls.classifier,
            retriever=cls.retriever,
            escalation_engine=cls.escalation_engine,
            response_generator=cls.generator
        )

    def test_zero_data_leakage(self):
        """Verifies strict 3-way isolation between Train/Retrieval, Validation, and Final Holdout."""
        final_test_path = "data/splits/final_test_200.jsonl"
        val_path = "data/splits/val_set.jsonl"

        final_ids = set()
        if os.path.exists(final_test_path):
            with open(final_test_path, "r", encoding="utf-8") as f:
                final_ids = set(json.loads(line)["tweet_id"] for line in f if line.strip())

        val_ids = set()
        if os.path.exists(val_path):
            with open(val_path, "r", encoding="utf-8") as f:
                val_ids = set(json.loads(line)["tweet_id"] for line in f if line.strip())

        retrieval_ids = set(r.get("customer_tweet_id") for r in self.retriever.records)

        # Pairwise disjointness checks
        self.assertEqual(len(final_ids.intersection(retrieval_ids)), 0, "Leakage between Final Test and Retrieval!")
        self.assertEqual(len(val_ids.intersection(retrieval_ids)), 0, "Leakage between Validation and Retrieval!")
        self.assertEqual(len(val_ids.intersection(final_ids)), 0, "Leakage between Validation and Final Test!")

    def test_clean_tweet_text(self):
        raw = "@AppleSupport my phone is slow! I️ hate this update @115854 https://t.co/abc"
        cleaned = clean_tweet_text(raw, remove_handles=True, remove_urls=False)
        self.assertNotIn("@AppleSupport", cleaned)
        self.assertNotIn("@115854", cleaned)
        self.assertIn("my phone is slow", cleaned)
        self.assertIn("I", cleaned)  # Fixed unicode 'I️' glitch

    def test_intent_classifier_taxonomy(self):
        query = "My battery drains 20% in an hour after iOS 11"
        intent, conf, dist = self.classifier.predict_single(query)
        self.assertIn(intent, INTENT_TAXONOMY.keys())
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)
        self.assertEqual(len(dist), len(INTENT_TAXONOMY))

    def test_escalation_engine_safety_hazard(self):
        hazard_query = "My iPhone battery is burning hot and swelling pushing the screen out!"
        res = self.escalation_engine.evaluate(hazard_query, predicted_intent="BATTERY_PERFORMANCE")
        self.assertEqual(res["decision"], "ESCALATE")
        self.assertIn("safety", res["reason"].lower())

    def test_escalation_engine_routine_self_serve(self):
        routine_query = "How do I clear app cache on my iPhone?"
        res = self.escalation_engine.evaluate(routine_query, predicted_intent="THIRD_PARTY_APP_ISSUES")
        self.assertEqual(res["decision"], "AUTO_HANDLE")
        self.assertTrue(len(res["reason"]) > 10)

    def test_retriever(self):
        res = self.retriever.retrieve("wifi dropping", top_k=2)
        self.assertIsInstance(res, list)
        if res:
            self.assertIn("customer_text", res[0])
            self.assertIn("apple_reply", res[0])

    def test_agent_end_to_end(self):
        query = "Why does my iPhone replace the letter I with a question mark box?"
        result = self.agent.process(query)
        self.assertEqual(result["intent"], "SOFTWARE_UPDATE_OS")
        self.assertEqual(result["escalation_decision"], "AUTO_HANDLE")
        self.assertTrue(len(result["drafted_reply"]) > 20)
        self.assertIn("latency_ms", result)
        self.assertIn("retrieval_score", result)
        self.assertIn("evidence_ids", result)
        self.assertLess(result["latency_ms"], 500.0)

    def test_baselines(self):
        b1 = TrivialBaselineAgent()
        out1 = b1.process("Short query")
        self.assertEqual(out1["intent"], "SOFTWARE_UPDATE_OS")
        self.assertEqual(out1["escalation_decision"], "AUTO_HANDLE")

        b2 = SimpleBaselineAgent(classifier=self.classifier, retriever=self.retriever)
        out2 = b2.process("I need a refund for an unauthorized charge")
        self.assertEqual(out2["escalation_decision"], "ESCALATE")

    def test_evaluator_and_judge(self):
        evaluator = BenchmarkEvaluator(intents=list(INTENT_TAXONOMY.keys()))
        res = evaluator.evaluate_intent_classification(["BATTERY_PERFORMANCE"], ["BATTERY_PERFORMANCE"])
        self.assertEqual(res["accuracy"], 1.0)

        judge = LLMJudge()
        j_out = judge.evaluate_response(
            customer_query="battery dying",
            predicted_intent="BATTERY_PERFORMANCE",
            escalation_decision="AUTO_HANDLE",
            drafted_reply="Check Settings > Battery to see which apps are using the most power.",
            ground_truth_intent="BATTERY_PERFORMANCE",
            ground_truth_escalation="AUTO_HANDLE",
            ground_truth_resolution="Guide user to Settings > Battery."
        )
        self.assertGreaterEqual(j_out["composite_score"], 4.0)


if __name__ == "__main__":
    unittest.main()
