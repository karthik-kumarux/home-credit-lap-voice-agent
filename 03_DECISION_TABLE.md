# Home Credit LAP Voice Agent — Decision Table

## 1. Core Decision Priority

For every customer response, use this conceptual order:

```text
EXTRACT INFORMATION
        ↓
VALIDATE INFORMATION
        ↓
UPDATE STATE
        ↓
CHECK DISQUALIFICATION
        ↓
CHECK TRANSFER CONDITION
        ↓
FIND FIRST MISSING CHECKLIST ITEM
        ↓
ASK NEXT QUESTION
```

The exact interaction priority should remain consistent throughout the call.

## 2. Call Entry

| Condition | Action | End? |
|---|---|---|
| Correct customer verified | Continue | No |
| Customer busy | Ask callback time | Yes |
| Customer cannot be verified | Do not expose unnecessary information; handle safely | Depends on platform flow |

## 3. Existing Loan / EMI Reduction

| Condition | Action | End? |
|---|---|---|
| Existing property loan | Transfer specialist message | Yes |
| Wants EMI reduction | Transfer specialist message | Yes |
| Neither | Continue fresh-loan flow | No |

## 4. Property Type

| Input | Result |
|---|---|
| Residential | Continue |
| Commercial | Continue |
| Industrial | Continue |
| Agricultural | Immediate disqualification |

## 5. Ownership

| Input | Result |
|---|---|
| Sole | Continue |
| Joint | Continue |

## 6. Documents

| Input | Result |
|---|---|
| Original documents available | Continue |
| Original documents unavailable | Immediate disqualification |
| Ambiguous / uncertain | Clarify |

## 7. Loan Amount

| Input | Result |
|---|---|
| ≤ ₹75 lakh | Continue |
| > ₹75 lakh | Explain limit and ask whether to proceed with ₹75 lakh |
| Customer accepts ₹75 lakh | Store ₹75 lakh and continue |
| Customer declines | End call |

## 8. Occupation + Income Mode

| Occupation | Income Mode | Result |
|---|---|---|
| Salaried | Bank | Continue |
| Self-employed | Bank | Continue |
| Salaried | Cash | Immediate disqualification |
| Self-employed | Cash | Immediate disqualification |

## 9. Market Value

| Input | Result |
|---|---|
| Clear estimate | Store and continue |
| Unclear estimate | Clarify |
| Any value | Do not invent a minimum threshold |

## 10. Tenure

| Input | Result |
|---|---|
| 3–15 years | Continue |
| <3 years | Immediate disqualification |
| >15 years | Immediate disqualification |

## 11. Final Handoff

Handoff only if:

```text
all 7 checklist items answered
AND
no disqualification
AND
no transfer branch
```

Then tell the customer that a senior loan expert will call back and provide exact interest-rate details.

## 12. Unsupported Assumptions

Do not invent:
- minimum market value
- exact interest rate
- additional eligibility criteria
- unsupported product terms
