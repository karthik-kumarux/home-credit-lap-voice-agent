import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.simulator import ConversationSimulator
from tests.test_scenarios import SCENARIOS

class TestConversations(unittest.TestCase):
    """
    Integration tests running actual LLM calls through the simulator.
    Requires ANTHROPIC_API_KEY to be set.
    """

    @classmethod
    def setUpClass(cls):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise unittest.SkipTest("ANTHROPIC_API_KEY not found. Skipping live LLM tests.")

    def run_scenario(self, scenario_name: str):
        data = SCENARIOS[scenario_name]
        inputs = data["inputs"]
        expected_state = data["expected_state"]

        print(f"\nRunning Scenario: {scenario_name}")
        sim = ConversationSimulator()
        sim.history.append({"role": "agent", "content": "Hello, am I speaking with Rahul?"})

        final_state = None
        for i, customer_input in enumerate(inputs):
            print(f"  Cust: {customer_input}")
            result = sim.process_turn(customer_input)
            print(f"  Agent: {result['reply']}")
            final_state = result["engine_state"]

            if result["call_ended"]:
                print("  [Call Ended Early]")
                break

        # Assertions
        for k, expected_v in expected_state.items():
            actual_v = final_state.get(k)
            self.assertEqual(
                actual_v,
                expected_v,
                f"{scenario_name} - State mismatch for '{k}'. Expected {expected_v}, got {actual_v}."
            )

        print(f"  ✓ {scenario_name} Passed.")

    # We can explicitly define test methods for the critical paths
    # to run them selectively or in parallel.
    def test_happy_path(self):
        self.run_scenario("T01_Happy_Path")

    def test_immediate_disqualify(self):
        self.run_scenario("T02_Agricultural")

    def test_correction(self):
        self.run_scenario("T16_Correction")

    def test_multi_fact(self):
        self.run_scenario("T22_Multi_Fact_Response")

    def test_existing_loan_transfer(self):
        self.run_scenario("T12_Existing_Loan")

if __name__ == "__main__":
    unittest.main()
