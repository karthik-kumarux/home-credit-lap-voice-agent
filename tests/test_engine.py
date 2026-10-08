import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.state import EligibilityEngine

class TestEligibilityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EligibilityEngine()

    def test_happy_path(self):
        self.engine.update({
            "customer_verified": True,
            "property_type": "Residential",
            "ownership_status": "Joint",
            "documents_available": True,
            "loan_amount": 5000000,
            "occupation": "Salaried",
            "income_mode": "Bank",
            "market_value": 8000000,
            "tenure": 10
        })
        self.assertTrue(self.engine.state["handoff_ready"])
        self.assertFalse(self.engine.state["disqualified"])

    def test_agricultural_disqualification(self):
        self.engine.update({
             "property_type": "Agricultural"
        })
        self.assertTrue(self.engine.state["disqualified"])
        self.assertEqual(self.engine.state["disqualification_reason"], "Agricultural property")
        self.assertTrue(self.engine.state["call_ended"])

    def test_cash_income_disqualification(self):
        self.engine.update({
            "occupation": "Self-employed",
            "income_mode": "Cash"
        })
        self.assertTrue(self.engine.state["disqualified"])
        self.assertEqual(self.engine.state["disqualification_reason"], "Cash income not allowed")

    def test_tenure_limits(self):
        # Too low
        self.engine.update({"tenure": 2})
        self.assertTrue(self.engine.state["disqualified"])
        self.assertEqual(self.engine.state["disqualification_reason"], "Tenure below 3 years")

        # Reset engine and test too high
        e2 = EligibilityEngine()
        e2.update({"tenure": 20})
        self.assertTrue(e2.state["disqualified"])
        self.assertEqual(e2.state["disqualification_reason"], "Tenure above 15 years")

        # Edge cases 3 and 15
        e3 = EligibilityEngine()
        e3.update({"tenure": 3})
        self.assertFalse(e3.state["disqualified"])

        e4 = EligibilityEngine()
        e4.update({"tenure": 15})
        self.assertFalse(e4.state["disqualified"])

    def test_missing_originals(self):
        self.engine.update({"documents_available": False})
        self.assertTrue(self.engine.state["disqualified"])

    def test_amount_limit_refusal(self):
        self.engine.update({"amount_limit_refused": True})
        self.assertTrue(self.engine.state["disqualified"])
        self.assertEqual(self.engine.state["disqualification_reason"], "Amount above limit refused")

    def test_transfer_rules(self):
        self.engine.update({"existing_property_loan": True})
        self.assertTrue(self.engine.state["transfer_required"])
        self.assertTrue(self.engine.state["call_ended"])

        e2 = EligibilityEngine()
        e2.update({"emi_reduction_request": True})
        self.assertTrue(e2.state["transfer_required"])
        self.assertEqual(e2.state["transfer_reason"], "EMI reduction request")

    def test_busy_customer(self):
        self.engine.update({"callback_requested": True})
        self.assertTrue(self.engine.state["call_ended"])
        self.assertFalse(self.engine.state["disqualified"])

    def test_verification_failure(self):
        self.engine.update({"customer_verified": False})
        self.assertTrue(self.engine.state["call_ended"])
        self.assertFalse(self.engine.state["disqualified"])

if __name__ == "__main__":
    unittest.main()
