"""
Define expected outcomes for the 22 test scenarios and adversarial cases.
This will serve as the contract for the determinististic eligibility engine.
"""

from typing import Dict, Any, List

# Each scenario outlines the sequential customer prompts and the expected FINAL state.
SCENARIOS = {
    "T01_Happy_Path": {
        "inputs": [
            "Yes, this is Rahul.",
            "I'm free to talk.",
            "It's a residential property.",
            "I am the sole owner.",
            "Yes, I have the original documents.",
            "I need a loan of 50 lakh.",
            "I'm salaried, get paid in my bank account.",
            "It's worth 1 crore.",
            "I want it for 10 years."
        ],
        "expected_state": {
            "customer_verified": True,
            "property_type": "Residential",
            "ownership_status": "Sole",
            "documents_available": True,
            "loan_amount": 5000000,
            "occupation": "Salaried",
            "income_mode": "Bank",
            "market_value": 10000000,
            "tenure": 10,
            "disqualified": False,
            "handoff_ready": True,
            "call_ended": True
        }
    },
    "T02_Agricultural": {
        "inputs": [
            "Yes, speaking.",
            "Yes, tell me.",
            "It's agricultural land."
        ],
        "expected_state": {
            "property_type": "Agricultural",
            "disqualified": True,
            "disqualification_reason": "Agricultural property",
            "call_ended": True
        }
    },
    "T03_Cash_Income": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Joint", "Yes original docs",
            "20 lakhs", "I'm salaried but I get cash in hand."
        ],
        "expected_state": {
            "occupation": "Salaried",
            "income_mode": "Cash",
            "disqualified": True,
            "disqualification_reason": "Cash income not allowed",
            "call_ended": True
        }
    },
    "T04_Self_Employed_Cash": {
        "inputs": [
            "Yes.", "Yes.", "Commercial", "Sole", "Yes original docs",
            "20 lakhs", "I run my own business and just take cash."
        ],
        "expected_state": {
            "occupation": "Self-employed",
            "income_mode": "Cash",
            "disqualified": True,
            "call_ended": True
        }
    },
    "T05_Missing_Originals": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "I only have photocopies."
        ],
        "expected_state": {
            "documents_available": False,
            "disqualified": True,
            "disqualification_reason": "Original documents mandatory",
            "call_ended": True
        }
    },
    "T06_Tenure_Too_Short": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes originals", "50 lakh", "Salaried to bank", "1 crore",
            "I want it paid off in 2 years."
        ],
        "expected_state": {
            "tenure": 2,
            "disqualified": True,
            "disqualification_reason": "Tenure below 3 years",
            "call_ended": True
        }
    },
    "T07_Tenure_Too_Long": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes originals", "50 lakh", "Salaried to bank", "1 crore",
            "I want it for 20 years."
        ],
        "expected_state": {
            "tenure": 20,
            "disqualified": True,
            "disqualification_reason": "Tenure above 15 years",
            "call_ended": True
        }
    },
    "T08_Maximum_Amount": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes", "75 lakh", "Salaried bank", "1 crore", "5 years"
        ],
        "expected_state": {
            "loan_amount": 7500000,
            "handoff_ready": True
        }
    },
    "T09_Amount_Above_Max_Accepts": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes",
            "I need 90 lakhs.",
            "Okay, 75 lakh works for me."
        ],
        "expected_state": {
            "loan_amount": 7500000,
            "disqualified": False,
            "call_ended": False
        }
    },
    "T10_Amount_Above_Max_Refuses": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes",
            "I need 90 lakhs.",
            "No, I specifically need 90 lakh or I'm not interested."
        ],
        "expected_state": {
            "loan_amount": 9000000,
            "disqualified": True,
            "disqualification_reason": "Amount above limit refused",
            "call_ended": True
        }
    },
    "T11_Joint_Ownership": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "It's jointly owned with my spouse."
        ],
        "expected_state": {
            "ownership_status": "Joint",
            "disqualified": False
        }
    },
    "T12_Existing_Loan": {
        "inputs": [
            "Yes.", "Yes.", "I already have a loan running on this house."
        ],
        "expected_state": {
            "existing_property_loan": True,
            "transfer_required": True,
            "transfer_reason": "Existing loan on property",
            "handoff_ready": False,
            "call_ended": True
        }
    },
    "T13_EMI_Reduction": {
        "inputs": [
            "Yes.", "Yes.", "Can you lower my current EMI?"
        ],
        "expected_state": {
            "emi_reduction_request": True,
            "transfer_required": True,
            "transfer_reason": "EMI reduction request",
            "call_ended": True
        }
    },
    "T14_Busy_Customer": {
        "inputs": [
            "Yes.", "I'm in a meeting, call back later."
        ],
        "expected_state": {
            "customer_verified": True,
            "callback_requested": True,
            "call_ended": True
        }
    },
    "T15_Out_of_Order_Info": {
        "inputs": [
            "Yes.", "Yes.", "It's my residential house, I am the joint owner, and it's worth 80 lakh."
        ],
        "expected_state": {
            "property_type": "Residential",
            "ownership_status": "Joint",
            "market_value": 8000000,
            # Next should ask about documents or loan amount
        }
    },
    "T16_Correction": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes documents", "40 lakh", "Salaried bank", "1 crore",
            "10 years... actually make that 12 years."
        ],
        "expected_state": {
            "tenure": 12,
            "handoff_ready": True
        }
    },
    "T17_Contradiction": {
        "inputs": [
            "Yes.", "Yes.", "It's a residential plot... no wait, it's agricultural land."
        ],
        "expected_state": {
            "property_type": "Agricultural",
            "disqualified": True,
            "call_ended": True
        }
    },
    "T18_Ambiguous_Documents": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole",
            "The papers are probably somewhere."
        ],
        "expected_state": {
            "documents_available": "UNKNOWN",
            # Agent should ask for clarification next
            "disqualified": False
        }
    },
    "T19_Interest_Rate_Diversion": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Before that, what exactly is the interest rate you are offering?"
        ],
        "expected_state": {
            "property_type": "Residential",
            "disqualified": False
            # Agent should answer briefly without inventing and return to checklist (documents)
        }
    },
    "T20_Interruption": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Wait, what documents do you need?"
        ],
        "expected_state": {
            "property_type": "Residential",
            "disqualified": False
            # Needs to address question and resume state
        }
    },
    "T21_Unrelated_Question": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Where is your nearest branch?"
        ],
        "expected_state": {
            "property_type": "Residential",
            # Will be handled gracefully, returning to qualification
        }
    },
    "T22_Multi_Fact_Response": {
        "inputs": [
            "Yes.", "Yes.", "It's a commercial shop, solely owned, market value 50L, need 20L."
        ],
        "expected_state": {
            "property_type": "Commercial",
            "ownership_status": "Sole",
            "market_value": 5000000,
            "loan_amount": 2000000,
            "disqualified": False
        }
    },
    "ADV01_Verification_Failure": {
        "inputs": [
            "No, Rahul doesn't live here."
        ],
        "expected_state": {
            "customer_verified": False,
            "call_ended": True
        }
    },
    "ADV02_Occupation_Gap": {
        "inputs": [
            "Yes.", "Yes.", "Residential", "Sole", "Yes", "50 lakh",
            "I am retired.",
            "Yes I get pension in my bank."
        ],
        "expected_state": {
           # Retired is not accepted. Ask clarifying, then politely drop.
           "disqualified": True,
           "disqualification_reason": "Occupation not Salaried/Self-employed",
           "call_ended": True
        }
    }
}
