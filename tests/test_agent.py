import json
import tempfile
import unittest
from pathlib import Path

from creative_intelligence.engine import CreativeAgent
from creative_intelligence.llm import parse_json_text
from creative_intelligence.memory import ExperimentLedger
from creative_intelligence.rubric import CRITERIA, normalize_audit


class FakeClient:
    def __init__(self):
        self.calls = []

    def complete_json(self, system, user, images=None):
        self.calls.append((system, user, images))
        if "TASK: CREATIVE AUDIT" in user:
            high = '"content": "' in user and 'Revised final work' in user
            score = 9 if high else 6
            return {
                "summary": "Specific editorial diagnosis",
                "confidence": "medium",
                "rubric": {key: {"score": score, "reason": f"Observed issue with {key}", "improvement": "Improve it"} for key in CRITERIA},
                "strengths": ["Understandable"],
                "weaknesses": ["Generic hook"],
                "improvement_plan": ["Make a more specific hook"],
                "risk_flags": [],
                "needs_verification": [],
                "test_variants": [],
            }
        if "Act as expert creative director" in system:
            return {"revised_content": "Revised final work", "revision_notes": ["More compelling"], "production_checklist": ["Check text"], "alternative_hooks": []}
        if "Invent a production-ready" in system:
            return {"content": "Revised final work", "concept": "Bold opener"}
        raise AssertionError("Unexpected model call")


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.model = FakeClient()
        self.agent = CreativeAgent(client=self.model)
        self.brief = {"medium": "reel", "goal": "Story completion", "content": "A robot goes outside"}

    def test_evaluate_computed_score(self):
        result = self.agent.evaluate(self.brief)
        self.assertEqual(result["score"], 60)
        self.assertEqual(result["decision"], "REVISE")
        self.assertEqual(len(result["rubric"]), 7)

    def test_improve_rechecks(self):
        result = self.agent.improve(self.brief)
        self.assertEqual(result["original_audit"]["score"], 60)
        self.assertEqual(result["revised_audit"]["score"], 90)
        self.assertEqual(result["score_change"], 30)
        self.assertEqual(len(self.model.calls), 3)

    def test_generate(self):
        result = self.agent.generate({"medium": "shorts", "goal": "Entertainment"})
        self.assertEqual(result["audit"]["decision"], "PASS")

    def test_compare(self):
        result = self.agent.compare({"goal": "CTR", "medium": "caption", "alternatives": [
            {"name": "A", "content": "A line"},
            {"name": "B", "content": "Revised final work"}]})
        self.assertEqual(result["recommended"], "B")

    def test_risks_override(self):
        raw = {"rubric": {k: {"score": 10, "reason": "fine"} for k in CRITERIA},
               "risk_flags": [{"severity": "critical", "issue": "false claim", "unresolved": True}]}
        self.assertEqual(normalize_audit(raw)["decision"], "HUMAN_REVIEW")

    def test_missing_rubric_rejected(self):
        with self.assertRaises(ValueError):
            normalize_audit({"rubric": {}})

    def test_json_code_fence(self):
        self.assertEqual(parse_json_text('```json\n{"a":1}\n```'), {"a": 1})

    def test_track_insights(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ExperimentLedger(str(Path(tmp) / "results.sqlite"))
            self.assertTrue(store.record({"creative_id": "x1", "platform": "ig", "variant": "B", "metric": "retention", "value": 77.5})["recorded"])
            self.assertEqual(store.insights()["group_summaries"][0]["unweighted_mean"], 77.5)

    def test_requires_content(self):
        with self.assertRaises(ValueError):
            self.agent.evaluate({"medium": "reel", "goal": "Whatever"})


if __name__ == "__main__":
    unittest.main()
