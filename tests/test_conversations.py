import os
import sys
import unittest
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.simulator import ConversationSimulator
from test_scenarios import SCENARIOS

# Filter scenarios if needed, or run all
ALL_SCENARIOS = list(SCENARIOS.keys())

class TestConversations(unittest.TestCase):
    """
    Integration tests running actual LLM calls through the simulator.
    Requires GROQ_API_KEY to be set.
    """

    @classmethod
    def setUpClass(cls):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise unittest.SkipTest("GROQ_API_KEY not found. Skipping live LLM tests.")

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

def generate_test(scenario_name):
    def test(self):
        self.run_scenario(scenario_name)
    return test

for scenario in ALL_SCENARIOS:
    test_method_name = f"test_{scenario.lower()}"
    setattr(TestConversations, test_method_name, generate_test(scenario))

if __name__ == "__main__":
    unittest.main()
