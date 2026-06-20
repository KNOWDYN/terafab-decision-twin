import unittest
from terafab_decision_twin.evidence import audit_evidence, summarize_statuses, unwrap

class EvidenceTests(unittest.TestCase):
    def test_verified_fact_requires_source(self):
        scenario = {"x": {"value": 1, "status": "verified_fact", "source": ""}}
        issues = audit_evidence(scenario)
        self.assertTrue(any(i.severity == "error" for i in issues))

    def test_unwrap(self):
        self.assertEqual(unwrap({"value": 3, "status": "assumption"}), 3)

    def test_status_counts(self):
        counts = summarize_statuses({"x": {"value": 1, "status": "assumption"}})
        self.assertEqual(counts["assumption"], 1)

if __name__ == "__main__":
    unittest.main()
