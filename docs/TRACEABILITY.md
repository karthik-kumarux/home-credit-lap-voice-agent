# Requirements Traceability

This matrix maps all 14 non-negotiable requirements and the Section 29 checklist to the implementing files and tests.

| Req ID | Description | Implementing File | Test Suite / Script |
|--------|-------------|-------------------|---------------------|
| REQ 01 | Verify intended customer. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_verification.py` (Draft) |
| REQ 02 | Detect busy customer. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_busy.py` (Draft) |
| REQ 03 | Ask preferred callback time and end call when busy. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_busy.py` (Draft) |
| REQ 04 | Present the LAP offer after successful verification. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_offer.py` (Draft) |
| REQ 05 | Route existing-property-loan/EMI-reduction cases to specialist. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_transfer.py` (Draft) |
| REQ 06 | Capture all 7 eligibility checklist items. | `src/state.py` | `tests/test_7_items.py` (Draft) |
| REQ 07 | Remember out of order / don't ask again. | `prompts/system_prompt_v1.md`, `src/state.py` | `tests/test_out_of_order.py` (Draft) |
| REQ 08 | Immediate disqualify upon mandatory eligibility rule fail. | `src/state.py` | `tests/test_disqualify.py` (Draft) |
| REQ 09 | Request > ₹75 lakh uses sub-flow negotiation. | `src/state.py` | `tests/test_amounts.py` (Draft) |
| REQ 10 | Complete every req item before final handoff. | `src/state.py` | `tests/test_handoff.py` (Draft) |
| REQ 11 | Use supplied context prompt variables dynamically. | `prompts/system_prompt_v1.md` | `tests/test_variables.py` (Draft) |
| REQ 12 | Handle natural speech/interruptions. | `prompts/system_prompt_v1.md` | Adversarial chat tests |
| REQ 13 | Avoid inventing product information. | `prompts/system_prompt_v1.md` | Adversarial chat tests |
| REQ 14 | Produce test calls / audio / transcripts. | Final submission delivery | `output/` artifacts |

## Section 29 Checklist (Completion Criteria)
- [ ] Customer verification gate
- [ ] Busy/callback branch
- [ ] Offer presentation
- [ ] Existing-loan / EMI-transfer branch
- [ ] Seven-item checklist
- [ ] Internal state model
- [ ] Out-of-order extraction
- [ ] Latest-answer correction handling
- [ ] Ambiguity handling
- [ ] Immediate disqualification
- [ ] >₹75 lakh negotiation branch
- [ ] Tenure validation
- [ ] Occupation + income validation
- [ ] RAG/no-fabrication policy
- [ ] Language behavior
- [ ] Agent gender consistency
- [ ] Final handoff gate
- [ ] Call termination rules
- [ ] Happy-path test
- [ ] Failure-path tests
- [ ] Adversarial tests
