# Requirements Traceability

This matrix maps all 14 non-negotiable requirements and the Section 29 checklist to the implementing files and tests.

| Req ID | Description | Implementing File | Test Suite / Script |
|--------|-------------|-------------------|---------------------|
| REQ 01 | Verify intended customer. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_conversations.py` (ADV01, T01) |
| REQ 02 | Detect busy customer. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_conversations.py` (T14) |
| REQ 03 | Ask preferred callback time and end call when busy. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_conversations.py` (T14) |
| REQ 04 | Present the LAP offer after successful verification. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_conversations.py` (T01) |
| REQ 05 | Route existing-property-loan/EMI-reduction cases to specialist. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_conversations.py` (T12, T13) |
| REQ 06 | Capture all 7 eligibility checklist items. | `src/state.py` | `tests/test_conversations.py` (T01, T22) |
| REQ 07 | Remember out of order / don't ask again. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_conversations.py` (T15, T22) |
| REQ 08 | Immediate disqualify upon mandatory eligibility rule fail. | `src/state.py` | `tests/test_conversations.py` (T02-T07) |
| REQ 09 | Request > ₹75 lakh uses sub-flow negotiation. | `src/state.py` | `tests/test_conversations.py` (T09, T10) |
| REQ 10 | Complete every req item before final handoff. | `src/state.py` | `tests/test_conversations.py` (T01) |
| REQ 11 | Use supplied context prompt variables dynamically. | `prompts/system_prompt_v1.md` | `src/simulator.py` String Replacement |
| REQ 12 | Handle natural speech/interruptions. | `prompts/system_prompt_v1.md` | `tests/test_conversations.py` (T16-T20) |
| REQ 13 | Avoid inventing product information. | `prompts/system_prompt_v1.md` | `tests/test_conversations.py` (T19) |
| REQ 14 | Produce test calls / audio / transcripts. | Final submission delivery | `output/` artifacts |

## Section 29 Checklist (Completion Criteria)
- [x] Customer verification gate
- [x] Busy/callback branch
- [x] Offer presentation
- [x] Existing-loan / EMI-transfer branch
- [x] Seven-item checklist
- [x] Internal state model
- [x] Out-of-order extraction
- [x] Latest-answer correction handling
- [x] Ambiguity handling
- [x] Immediate disqualification
- [x] >₹75 lakh negotiation branch
- [x] Tenure validation
- [x] Occupation + income validation
- [x] RAG/no-fabrication policy
- [x] Language behavior
- [x] Agent gender consistency
- [x] Final handoff gate
- [x] Call termination rules
- [x] Happy-path test
- [x] Failure-path tests
- [x] Adversarial tests
