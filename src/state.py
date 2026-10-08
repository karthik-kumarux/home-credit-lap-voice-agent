from typing import Dict, Any, List, Optional
import json

class EligibilityEngine:
    """
    Deterministic eligibility engine for Home Credit LAP Voice Agent.
    Serves as the test oracle for rule validation.
    """
    def __init__(self):
        self.state: Dict[str, Any] = {
            "customer_verified": "UNKNOWN",

            "property_type": "UNKNOWN",
            "ownership_status": "UNKNOWN",
            "documents_available": "UNKNOWN",
            "loan_amount": "UNKNOWN",
            "occupation": "UNKNOWN",
            "income_mode": "UNKNOWN",
            "market_value": "UNKNOWN",
            "tenure": "UNKNOWN",

            "existing_property_loan": "UNKNOWN",
            "emi_reduction_request": "UNKNOWN",

            "callback_requested": False,
            "callback_time": "UNKNOWN",

            "amount_limit_refused": False,

            "disqualified": False,
            "disqualification_reason": "UNKNOWN",
            "transfer_required": False,
            "transfer_reason": "UNKNOWN",

            "handoff_ready": False,
            "call_ended": False
        }

    def update(self, new_facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates internal state based on new facts extracted from the customer response.
        Applies strict precedent evaluation.
        """
        if self.state["call_ended"]:
            return self.state

        # 1. Update State (Corrections handled implicitly by overriding old values)
        for key, value in new_facts.items():
            if key in self.state and value is not None:
                self.state[key] = value

        # Evaluate rules based on precedence
        self._evaluate_disqualifications()
        if self.state["call_ended"]:
            return self.state

        self._evaluate_transfers()
        if self.state["call_ended"]:
            return self.state

        self._evaluate_busy_or_verification()
        if self.state["call_ended"]:
            return self.state

        self._evaluate_handoff()

        return self.state

    def _disqualify(self, reason: str):
        self.state["disqualified"] = True
        self.state["disqualification_reason"] = reason
        self.state["call_ended"] = True

    def _evaluate_disqualifications(self):
        """Immediately disqualifies if any strict rule is broken."""
        # Property
        if self.state["property_type"] == "Agricultural":
            self._disqualify("Agricultural property")
            return

        # Documents
        if self.state["documents_available"] is False:
            self._disqualify("Original documents mandatory")
            return

        # Income / Occupation
        if self.state["income_mode"] == "Cash":
            self._disqualify("Cash income not allowed")
            return

        occ = self.state["occupation"]
        if occ not in ["UNKNOWN", "Salaried", "Self-employed"]:
            self._disqualify("Occupation not Salaried/Self-employed")
            return

        # Tenure
        t = self.state["tenure"]
        if isinstance(t, (int, float)):
            if t < 3:
                self._disqualify("Tenure below 3 years")
                return
            if t > 15:
                self._disqualify("Tenure above 15 years")
                return

        # Negotiation fall-through
        if self.state["amount_limit_refused"] is True:
            self._disqualify("Amount above limit refused")
            return

    def _evaluate_transfers(self):
        """Routes existing clients to specialist."""
        if self.state["existing_property_loan"] is True:
            self.state["transfer_required"] = True
            self.state["transfer_reason"] = "Existing loan on property"
            self.state["call_ended"] = True
            return

        if self.state["emi_reduction_request"] is True:
            self.state["transfer_required"] = True
            self.state["transfer_reason"] = "EMI reduction request"
            self.state["call_ended"] = True
            return

    def _evaluate_busy_or_verification(self):
        """Ends call if customer is busy or unverified after attempt."""
        if self.state["customer_verified"] is False:
            self.state["call_ended"] = True
            return

        if self.state["callback_requested"] is True:
            self.state["call_ended"] = True
            return

    def _evaluate_handoff(self):
        """Checks if all 7 criteria are met for a successful senior handoff."""
        if self.state["customer_verified"] is not True:
            return

        checklist = [
            "property_type",
            "ownership_status",
            "documents_available",
            "loan_amount",
            "occupation",
            "income_mode",
            "market_value",
            "tenure"
        ]

        for item in checklist:
            val = self.state[item]
            if val == "UNKNOWN" or val is None:
                return

        # All criteria filled, none failed
        self.state["handoff_ready"] = True
        self.state["call_ended"] = True

    def get_next_question(self) -> Optional[str]:
        """
        Determines the next missing checklist item if the state is not terminated.
        Primarily for testing clarity.
        """
        if self.state["call_ended"] or self.state["handoff_ready"]:
            return None

        if self.state["customer_verified"] == "UNKNOWN":
            return "customer_verified"

        checklist = [
            "property_type",
            "ownership_status",
            "documents_available",
            "loan_amount",
            "occupation",
            "income_mode",
            "market_value",
            "tenure"
        ]
        for item in checklist:
            if self.state[item] == "UNKNOWN":
                return item
        return None

if __name__ == "__main__":
    # Test basic integration
    engine = EligibilityEngine()
    engine.update({"customer_verified": True})
    print(f"Next: {engine.get_next_question()}")
    engine.update({"property_type": "Agricultural"})
    print(json.dumps(engine.state, indent=2))
