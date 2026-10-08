# Home Credit LAP Voice Agent — State Model

## 1. Purpose

This document defines the internal state the voice agent should maintain while conducting the qualification call.

## 2. Customer and Call State

```text
customer_verified = UNKNOWN
customer_busy = UNKNOWN
callback_time = UNKNOWN

existing_property_loan = UNKNOWN
emi_reduction_request = UNKNOWN

disqualified = FALSE
transfer_required = FALSE
handoff_ready = FALSE
call_ended = FALSE
```

## 3. Qualification State

```text
property_type = UNKNOWN
ownership_status = UNKNOWN
documents_available = UNKNOWN
loan_amount = UNKNOWN
occupation = UNKNOWN
income_mode = UNKNOWN
market_value = UNKNOWN
tenure = UNKNOWN
```

Although the assignment describes seven checklist items, occupation and income mode are represented as separate internal fields because they are two facts within checklist item 5.

## 4. State Values

Use `UNKNOWN` until the customer provides enough information to establish a value.

Examples:

```text
property_type = RESIDENTIAL
ownership_status = JOINT
documents_available = TRUE
loan_amount = 5000000
occupation = SELF_EMPLOYED
income_mode = BANK
market_value = 10000000
tenure = 10
```

## 5. Information Extraction

After every customer response:

1. Extract every eligibility fact that is clearly stated.
2. Extract transfer intent.
3. Extract busy/callback information where applicable.
4. Validate newly extracted information.
5. Update the internal state.
6. Apply priority rules.
7. Ask the next required question only if the call remains active.

## 6. Multiple Facts in One Response

Example:

> “I have a residential house, it is jointly owned with my wife, and it is worth about ₹80 lakh.”

Update:

```text
property_type = RESIDENTIAL
ownership_status = JOINT
market_value = 8000000
```

Do not ask those questions again.

## 7. Corrections

If the customer corrects an earlier answer, use the latest clear answer.

Example:

> “Ten years — actually, make that twelve.”

Final state:

```text
tenure = 12
```

## 8. Ambiguity

Do not convert uncertain language into a confirmed state.

Example:

> “The papers are probably somewhere.”

Do not set:

```text
documents_available = TRUE
```

Ask a clarification instead.

## 9. Contradictions

If a customer gives conflicting information, the latest clear statement should replace the earlier value.

Example:

> “It is residential... actually no, it is agricultural.”

Final state:

```text
property_type = AGRICULTURAL
```

This causes disqualification.

## 10. Completion

The seven checklist items are complete only when all required information is known:

```text
property_type != UNKNOWN
ownership_status != UNKNOWN
documents_available != UNKNOWN
loan_amount != UNKNOWN
occupation != UNKNOWN
income_mode != UNKNOWN
market_value != UNKNOWN
tenure != UNKNOWN
```

Do not hand off merely because the customer appears likely to qualify.
