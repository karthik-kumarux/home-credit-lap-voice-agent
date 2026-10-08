import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
import anthropic

from state import EligibilityEngine

# Load environment variables
load_dotenv()

class ConversationSimulator:
    def __init__(self, prompt_path: str = "../prompts/system_prompt_v1.md"):
        self.engine = EligibilityEngine()
        self.history: List[Dict[str, str]] = []

        # Determine paths relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompt_path = os.path.join(base_dir, prompt_path)

        with open(self.prompt_path, 'r', encoding='utf-8') as f:
            self.base_prompt_template = f.read()

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("WARNING: ANTHROPIC_API_KEY not found in environment.")

        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def render_prompt(self, customer_utterance: str) -> str:
        """Hydrates the Jinja-like variables in the prompt."""
        # Clean history for prompt context
        history_str = ""
        for turn in self.history:
            role = turn["role"].capitalize()
            history_str += f"{role}: {turn['content']}\n"

        render = self.base_prompt_template

        # Hardcoded context for simulation
        replacements = {
            "{{company_name}}": "Home Credit",
            "{{customer_name}}": "Rahul",
            "{{agent_name}}": "Aisha",
            "{{agent_gender}}": "Female",
            "{{current_day}}": "Thursday",
            "{{current_date}}": "2026-10-08",
            "{{current_time}}": "14:30",
            "{{additional_context_from_rag}}": "Our current fixed LAP interest rate ranges between 10.5% - 12% annually. Processing fee is 1%.",
            "{{language_to_speak}}": "English",
            "{{conversation_history}}": history_str.strip() or "No previous history.",
            "{{customer_utterance}}": customer_utterance
        }

        for k, v in replacements.items():
            render = render.replace(k, str(v))

        return render

    def parse_llm_json(self, text: str) -> Dict[str, Any]:
        """Safely extract the JSON block from the LLM output."""
        try:
            # First try parsing it as pure raw JSON
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown block
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception as e:
                print(f"Error parsing regex extracted JSON: {e}")

        # Fallback to empty if parse fails
        print("Failed to parse LLM JSON output. Raw output was:")
        print(text)
        return {"extracted_facts": {}, "reply_to_customer": "I'm sorry, I encountered an internal processing error."}

    def process_turn(self, customer_input: str) -> Dict[str, Any]:
        """Runs a single interaction turn."""
        if not self.client:
             raise ValueError("Anthropic client not initialized (missing API key).")

        # Add to local history
        self.history.append({"role": "customer", "content": customer_input})

        prompt = self.render_prompt(customer_input)

        # Call LLM
        response = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        llm_text = response.content[0].text

        # Parse JSON and Extract Facts
        parsed_output = self.parse_llm_json(llm_text)

        reply = parsed_output.get("reply_to_customer", "Sorry, internal error.")
        extracted_facts = parsed_output.get("extracted_facts", {})

        # Add agent reply to history
        self.history.append({"role": "agent", "content": reply})

        # Pump facts into strict oracle engine
        new_state = self.engine.update(extracted_facts)

        return {
            "reply": reply,
            "facts_extracted": extracted_facts,
            "engine_state": new_state,
            "call_ended": new_state.get("call_ended", False),
            "disqualified": new_state.get("disqualified", False),
            "handoff_ready": new_state.get("handoff_ready", False)
        }

def run_interactive():
    print("=========================================")
    print(" Home Credit LAP Voice Agent - Simulator ")
    print("=========================================")
    print("Initializing...")

    try:
        sim = ConversationSimulator()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return

    print(f"Loaded Prompt: {os.path.basename(sim.prompt_path)}")
    print("Type 'quit' or 'exit' to stop.")
    print("Agent is initiating the call. (e.g. 'Hello, am I speaking with Rahul?')")
    print("-----------------------------------------")

    # We prime the conversation manually as if the agent called.
    sim.history.append({"role": "agent", "content": "Hello, am I speaking with Rahul?"})
    print("Agent: Hello, am I speaking with Rahul?")

    while True:
        try:
            user_input = input("\nCustomer: ")
            if user_input.strip().lower() in ['quit', 'exit']:
                break

            result = sim.process_turn(user_input)

            print(f"\nAgent: {result['reply']}")

            # Print Oracle overlay for debugging
            state = result['engine_state']
            print("\n--- ORACLE DIAGNOSTICS ---")
            print(f"Extracted Facts: {result['facts_extracted']}")
            print(f"Call Ended: {result['call_ended']} | Disqualified: {result['disqualified']} | Handoff Ready: {result['handoff_ready']}")
            if state.get('disqualified'):
                print(f"Reason: {state.get('disqualification_reason')}")
            print("--------------------------")

            if result['call_ended']:
                print("\n[CALL TERMINATED BY ENGINE RULES]")
                break

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")
            break

if __name__ == "__main__":
    run_interactive()
