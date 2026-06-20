import unittest
from terafab_decision_twin.evidence import audit_evidence, summarize_statuses, unwrap, normalize_status

class EvidenceTests(unittest.TestCase):
    def test_verified_fact_requires_source(self):
        scenario = {"x": {"value": 1, "status": "verified_fact", "source": ""}}
        issues = audit_evidence(scenario)
        self.assertTrue(any(i.severity == "error" for i in issues))

    def test_unwrap(self):
        self.assertEqual(unwrap({"value": 3, "status": "assumption"}), 3)

    def test_status_counts_canonicalize_aliases(self):
        counts = summarize_statuses({"x": {"value": 1, "status": "assumption"}})
        self.assertEqual(counts["scenario_assumption"], 1)

    def test_status_normalization(self):
        self.assertEqual(normalize_status("verified_fact"), "verified_project_fact")
        self.assertEqual(normalize_status("filed_claim"), "filed_claimed")
        self.assertEqual(normalize_status("user_input"), "user_provided")

if __name__ == "__main__":
    unittest.main()
