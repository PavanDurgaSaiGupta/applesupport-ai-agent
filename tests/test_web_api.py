"""
Unit and Integration Tests for web_api.py.
Verifies health, status, benchmark endpoints, static file serving,
and end-to-end agent triage analysis across multiple real queries.
"""

import unittest
from fastapi.testclient import TestClient
from web_api import app


class TestWebApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["backend"], "online")

    def test_status_endpoint_data_integrity(self):
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Verify genuine repository provenance
        self.assertEqual(data["backend_status"], "online")
        self.assertEqual(data["dataset"], "AppleSupport")
        self.assertEqual(data["golden_total"], 200)
        self.assertEqual(data["human_reviewed"], 200)
        self.assertEqual(data["manual_review_status"], "COMPLETE")
        self.assertEqual(data["leakage_status"], "PASS")
        self.assertEqual(data["train_validation_overlap"], 0)
        self.assertEqual(data["train_final_overlap"], 0)
        self.assertEqual(data["validation_final_overlap"], 0)

    def test_benchmark_endpoint(self):
        res = self.client.get("/api/benchmark")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Must have separate final and validation blocks
        self.assertIn("final", data)
        self.assertIn("validation", data)
        self.assertIsNotNone(data["final"])
        self.assertIsNotNone(data["validation"])
        
        # Verify final holdout results structure
        final_bench = data["final"]
        self.assertIn("Proposed System: Grounded AI Agent", final_bench)
        proposed = final_bench["Proposed System: Grounded AI Agent"]
        self.assertAlmostEqual(proposed["intent"]["accuracy"], 0.665, places=2)
        self.assertAlmostEqual(proposed["escalation"]["accuracy"], 0.935, places=2)
        self.assertAlmostEqual(proposed["escalation"]["escalate_recall"], 0.793, places=2)

    def test_failures_endpoint(self):
        res = self.client.get("/api/failures")
        self.assertEqual(res.status_code, 200)
        failures = res.json()
        self.assertEqual(len(failures), 5)
        for f in failures:
            self.assertIn("id", f)
            self.assertIn("title", f)
            self.assertIn("example", f)
            self.assertIn("observed", f)
            self.assertIn("root_cause", f)
            self.assertIn("mitigation", f)

    def test_static_files_served(self):
        # Root index.html
        res_index = self.client.get("/")
        self.assertEqual(res_index.status_code, 200)
        self.assertIn("AppleSupport AI Support Agent", res_index.text)
        
        # CSS
        res_css = self.client.get("/style.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn("--bg-canvas", res_css.text)
        
        # JS
        res_js = self.client.get("/app.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertIn("handleAnalyzeSubmit", res_js.text)

    def test_analyze_query_1_battery(self):
        query = "My iPhone battery is draining very quickly since the latest update."
        res = self.client.post("/api/analyze", json={"message": query})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["intent"], "BATTERY_PERFORMANCE")
        self.assertEqual(data["escalation_decision"], "AUTO_HANDLE")
        self.assertIn("Settings > Battery", data["drafted_reply"])
        self.assertLessEqual(len(data["drafted_reply"]), 280)
        self.assertGreater(len(data["retrieved_contexts"]), 0)
        self.assertIn("similarity_score", data["retrieved_contexts"][0])

    def test_analyze_query_2_billing(self):
        query = "Why is my card charged $9.99 for an in-app subscription I didn't purchase?"
        res = self.client.post("/api/analyze", json={"message": query})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["intent"], "STORE_ORDER_BILLING")
        self.assertLessEqual(len(data["drafted_reply"]), 280)
        self.assertGreater(len(data["retrieved_contexts"]), 0)

    def test_analyze_query_3_hazard_escalate(self):
        query = "My iPhone is burning hot, smoking, and the battery is visibly swollen!"
        res = self.client.post("/api/analyze", json={"message": query})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["escalation_decision"], "ESCALATE")
        self.assertIn("Thermal event", data["escalation_reason"])
        self.assertLessEqual(len(data["drafted_reply"]), 280)

    def test_analyze_empty_message_validation(self):
        res = self.client.post("/api/analyze", json={"message": "   "})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
