# Home Credit LAP AI Voice Agent — Conversation Logic Blueprint

**Purpose:** Source-of-truth design document for building and testing the Home Credit Loan Against Property (LAP) AI Voice Agent.

**Based on:** SalesAgents AI Voice Agent Design assignment and the supplied assignment preparation/reference guide.

---

## 1. Objective

Build an AI Voice Agent that contacts existing Home Credit customers about a pre-approved Loan Against Property (LAP) offer, performs a preliminary eligibility check, handles natural conversation and interruptions, identifies transfer/EMI-reduction cases, and hands qualified customers to a senior human loan expert.

The agent is a **preliminary qualification assistant**, not the final loan decision-maker.

---

## 2. Non-Negotiable Assignment Requirements

The agent must:

1. Verify the intended customer.
2. Detect whether the customer is busy.
3. Ask for a preferred callback time and end the call when the customer is unavailable.
4. Present the LAP offer after successful verification.
5. Detect existing-property-loan or EMI-reduction cases and route them to the loan-transfer specialist flow.
6. Capture all 7 eligibility checklist items.
7. Remember information supplied out of order and never unnecessarily ask for the same information again.
8. Immediately disqualify the customer when a mandatory eligibility rule fails.
9. Handle requests above ₹75 lakh using the special maximum-limit flow.
10. Complete every required eligibility item before final handoff.
11. Use the supplied prompt variables dynamically.
12. Handle natural speech, full sentences, interruptions, fillers, and corrections.
13. Avoid inventing product information that is not supplied through context.
14. Produce test calls with recordings and transcripts.

---

# 3. High-Level Call State Machine

```text
START
  |
  v
CUSTOMER VERIFICATION
  |
  +---- Customer busy? ---- YES ----> Ask callback time ----> END
  |
  NO
  |
  v
PRESENT LAP OFFER
  |
  v
CHECK EXISTING LOAN / EMI REDUCTION
  |
  +---- YES ----> Loan-transfer specialist message ----> END
  |
  NO
  |
  v
QUALIFICATION CHECKLIST
  |
  +--> 1. Property Type
  +--> 2. Ownership Status
  +--> 3. Original Documents
  +--> 4. Loan Amount
  +--> 5. Occupation + Income Mode
  +--> 6. Market Value
  +--> 7. Tenure
  |
  v
ELIGIBILITY DECISION
  |
  +---- FAIL ----> Explain specific-offer criteria ----> END
  |
  PASS
  |
  v
FINAL HANDOFF GATE
  |
  +---- All 7 answered? ---- NO ----> Ask first missing item
  |
  YES
  |
  v
Senior Loan Expert Callback / Handoff
  |
  v
END
```

---

# 4. Internal Qualification State

The internal state should persist throughout the call and be updated whenever the customer supplies valid information.

```text
customer_verified: UNKNOWN

property_type: UNKNOWN
ownership_status: UNKNOWN
documents_available: UNKNOWN
loan_amount: UNKNOWN
occupation: UNKNOWN
income_mode: UNKNOWN
market_value: UNKNOWN
tenure: UNKNOWN

existing_property_loan: UNKNOWN
emi_reduction_request: UNKNOWN

callback_requested: FALSE
callback_time: UNKNOWN

disqualified: FALSE
disqualification_reason: UNKNOWN
transfer_required: FALSE
transfer_reason: UNKNOWN

handoff_ready: FALSE
call_ended: FALSE
```

## State values

Use `UNKNOWN` until a fact has been clearly established.

For boolean-type fields, use:

```text
TRUE / FALSE / UNKNOWN
```

For categorical fields, normalize customer language into a controlled value.

Example:

```text
"It's my own house" -> property_type = Residential
"Me and my wife own it" -> ownership_status = Joint
```

---

# 5. Qualification Checklist

The official checklist contains 7 items. Item 5 contains two values internally: occupation and income mode.

| Order | Checklist Item | Internal State |
|---|---|---|
| 1 | Property Type | `property_type` |
| 2 | Ownership Status | `ownership_status` |
| 3 | Original Documents Availability | `documents_available` |
| 4 | Desired Loan Amount | `loan_amount` |
| 5 | Occupation + Income Mode | `occupation`, `income_mode` |
| 6 | Estimated Property Market Value | `market_value` |
| 7 | Desired Tenure | `tenure` |

### Core rule

Always ask the **earliest unanswered checklist item** unless a higher-priority branch is triggered.

Never ask again for an item that has already been clearly answered.

---

# 6. Information Extraction Rule

After **every customer response**, perform this logical sequence internally:

```text
1. Read the complete customer response.
2. Extract every eligibility fact present in the response.
3. Normalize the values.
4. Store/update all valid information.
5. Check for immediate disqualification.
6. Check for transfer conditions.
7. Check whether a clarification is needed for any ambiguous value.
8. Identify the earliest missing checklist item.
9. Ask only that next required question.
```

### Priority formula

```text
EXTRACT
  -> VALIDATE
  -> UPDATE STATE
  -> DISQUALIFICATION CHECK
  -> TRANSFER CHECK
  -> CLARIFICATION CHECK
  -> FIRST MISSING QUESTION
```

This prevents the agent from behaving like a rigid questionnaire.

---

# 7. Eligibility Rules

## 7.1 Property Type

### Allowed

```text
Residential
Commercial
Industrial
```

### Not allowed

```text
Agricultural
```

### Rule

If the customer clearly states that the property is agricultural, immediately disqualify.

Do not continue asking eligibility questions after disqualification.

### Example

**Customer:**
> It is agricultural land.

**Agent behavior:**

- Set `property_type = Agricultural`.
- Set `disqualified = TRUE`.
- Set `disqualification_reason = Agricultural property`.
- Politely explain that the customer does not meet the criteria for this specific offer at this time.
- End the call.

---

## 7.2 Ownership Status

### Allowed

```text
Sole ownership
Joint ownership
```

Both are eligible.

Do **not** disqualify a customer because the property is jointly owned.

---

## 7.3 Original Documents

The customer must have the **original property documents available for verification**.

### Clearly eligible

```text
"I have the originals."
"The original papers are available at home."
```

### Clearly ineligible

```text
"I only have photocopies."
"I don't have the original documents."
```

### Ambiguous

```text
"The papers should be somewhere."
"I think I have them."
```

For ambiguous answers, do not assume eligibility. Ask a concise clarification.

---

## 7.4 Loan Amount

### Maximum amount

```text
₹75,00,000 (₹75 lakh)
```

### Requested amount <= ₹75 lakh

Continue the qualification flow.

### Requested amount > ₹75 lakh

Do **not** immediately reject.

Use this sequence:

```text
Customer requests > ₹75 lakh
        |
        v
Explain maximum available amount = ₹75 lakh
        |
        v
Ask whether customer would like to proceed with ₹75 lakh
        |
        +---- YES ----> set loan_amount = ₹75,00,000 -> continue
        |
        +---- NO -----> end call
```

The customer's original requested amount may be retained for context, but the qualification amount should be updated to ₹75 lakh only after explicit acceptance.

---

## 7.5 Occupation + Income Mode

### Occupation — allowed

```text
Salaried
Self-employed
```

### Income mode — allowed

```text
Bank
```

### Income mode — disallowed

```text
Cash
```

### Decision table

| Occupation | Income Mode | Result |
|---|---|---|
| Salaried | Bank | Eligible |
| Salaried | Cash | Disqualify |
| Self-employed | Bank | Eligible |
| Self-employed | Cash | Disqualify |

If income is clearly received in cash, immediately disqualify.

---

## 7.6 Market Value

Capture the customer's estimated current market value.

### Important boundary

The assignment does **not** specify a minimum market-value threshold.

Therefore:

```text
Capture the value.
Do not invent a minimum value.
Do not create an eligibility rule that does not exist in the assignment.
```

---

## 7.7 Tenure

Allowed range:

```text
3 to 15 years inclusive
```

### Decision table

| Tenure | Result |
|---|---|
| < 3 years | Disqualify |
| 3 years | Eligible |
| 4–14 years | Eligible |
| 15 years | Eligible |
| > 15 years | Disqualify |

---

# 8. Immediate Disqualification Logic

At any point during the call, if the customer clearly provides an ineligible value:

```text
1. Stop normal qualification.
2. Do not ask additional eligibility questions.
3. Politely explain the specific-offer eligibility outcome.
4. End the call.
```

### Disqualifying conditions explicitly defined by the assignment

```text
property_type = Agricultural
income_mode = Cash
original documents unavailable
requested/accepted loan amount outside the permitted limit
accepted tenure < 3 years
accepted tenure > 15 years
```

### Do not override business rules

The agent must not persuade the customer into an ineligible case and must not invent exceptions.

---

# 9. Existing Loan / EMI Reduction Transfer Logic

The standard flow is for a **fresh loan**.

If the customer says that:

- they already have an existing loan on the property, or
- they want to reduce their current EMI,

then do **not** continue the fresh-loan eligibility checklist.

### Flow

```text
Existing loan / EMI reduction detected
        |
        v
Acknowledge customer
        |
        v
Explain that a loan-transfer specialist will contact them
        |
        v
END CALL
```

### Example intent signals

```text
"I already have a loan on this property."
"This property is already mortgaged."
"I want to reduce my EMI."
"Can you transfer my existing loan?"
```

These examples are intent signals, not an exhaustive keyword list. The agent should recognize natural variations.

---

# 10. Busy Customer Flow

At the start of the call, if the customer indicates they are unavailable:

```text
Busy detected
   -> Acknowledge
   -> Ask preferred callback time
   -> Capture callback time
   -> End call
```

### Example

**Customer:**
> I'm in a meeting right now.

**Agent behavior:**

> Certainly, I understand. What would be a convenient time for us to call you back?

Do not continue the offer or qualification while the customer is unavailable.

---

# 11. Customer Verification Gate

The intended customer must be verified before presenting the offer.

### Example

**Agent:**
> Hello, may I speak with Rahul?

**Customer:**
> Yes, this is Rahul.

Then:

```text
customer_verified = TRUE
```

If the identity is not established, do not unnecessarily reveal detailed product information or sensitive customer information.

---

# 12. Offer Presentation

After successful verification:

1. Explain why the customer is being contacted.
2. Frame the offer around customer loyalty/value.
3. Mention that the special LAP offer is available for up to ₹75 lakh.
4. Explain that a few questions are needed for preliminary qualification.

The tone should be natural, professional, and advisory — not like a scripted advertisement.

### Example intent

> As one of our valued customers, you may be eligible for a special Loan Against Property offer of up to ₹75 lakh. I'd like to ask a few questions to check whether the offer is suitable for you.

---

# 13. Out-of-Order Information Handling

The customer may answer multiple future checklist questions before they are asked.

### Example

**Agent:**
> What type of property do you have?

**Customer:**
> It's a residential house, jointly owned with my wife, and it is worth around ₹80 lakh.

Update:

```text
property_type = Residential
ownership_status = Joint
market_value = ₹80 lakh
```

The next unanswered item is documents.

Therefore ask:

> Do you have the original property documents available for verification?

### Never do this

```text
Customer already gave ownership -> ask ownership again
Customer already gave market value -> ask market value again
```

---

# 14. Multiple Facts in One Utterance

The agent must extract all useful facts from one customer turn.

### Example

**Customer:**
> It's my own residential property, the original documents are available, and I need around ₹40 lakh.

Capture:

```text
property_type = Residential
ownership_status = Sole
documents_available = TRUE
loan_amount = ₹40 lakh
```

Then continue with the first remaining missing checklist item.

---

# 15. Corrections and Contradictions

Customers may correct themselves.

### Example

> It's 10 years — actually, make that 12.

Latest clear answer wins:

```text
tenure = 12 years
```

### Contradiction rule

If the customer provides a clear correction, overwrite the previous value with the latest valid value.

### Example

> It's residential... actually, it's agricultural land.

Final state:

```text
property_type = Agricultural
disqualified = TRUE
```

Do not continue the eligibility flow.

---

# 16. Ambiguous Answers

Do not guess when a required eligibility field is unclear.

### Example

**Customer:**
> The original papers are probably somewhere.

Do not set:

```text
documents_available = TRUE
```

Instead ask a concise clarification:

> Just to confirm, do you have the original property documents available for verification?

---

# 17. Interruptions

When the customer interrupts with an eligibility or process question:

```text
1. Stop speaking naturally.
2. Address the customer's immediate question briefly.
3. Do not lose already captured state.
4. Return to the first missing checklist item.
```

### Example

Agent begins asking about documents.

Customer:
> Wait, what documents do you need?

Agent should briefly explain the requirement and then continue from the document step rather than restarting the flow.

---

# 18. Product Questions and RAG Handling

The system receives:

```text
additional_context_from_rag
```

Use this context for product-specific information when available.

### Rules

```text
Use supplied RAG/product context when relevant.
Never invent rates, fees, policies, limits, or benefits.
If exact information is not available, defer the exact detail to the senior loan expert.
Return to the qualification flow after answering a diversion.
```

### Interest-rate example

Customer:
> What interest rate will I get?

Agent should not invent an exact rate if none is supplied.

A suitable response is to explain that the exact interest rate will be provided by the senior loan expert after preliminary qualification, then return to the checklist.

---

# 19. Unrelated Questions

If the customer asks something unrelated:

```text
If the answer exists in supplied RAG/context:
    Answer briefly.

Otherwise:
    Do not fabricate.
    Explain that the appropriate expert can provide the exact information.
    Return to the qualification flow.
```

The agent should remain focused without sounding dismissive.

---

# 20. Language Behavior

The agent receives:

```text
language_to_speak
```

The conversation should be conducted in the configured language.

Supported assignment languages:

```text
English
Hindi
```

Do not randomly switch languages. If the customer explicitly requests another supported language and the platform allows it, follow the platform's supported language behavior; otherwise remain in the configured language.

---

# 21. Agent Identity and Gender

The agent receives:

```text
agent_name
agent_gender
```

The configured agent identity and gender must remain consistent throughout the call.

Where language grammar includes gendered forms, use forms consistent with the configured agent gender.

---

# 22. Dynamic Prompt Variables

The final System Prompt must account for:

```text
{{company_name}}
{{customer_name}}
{{agent_name}}
{{agent_gender}}
{{current_date}}
{{current_day}}
{{current_time}}
{{additional_context_from_rag}}
{{language_to_speak}}
{{conversation_history}}
{{customer_utterance}}
```

Do not hard-code customer or agent information when variables are provided.

---

# 23. Final Handoff Gate

The customer can be handed to the senior loan expert **only when all conditions below are true**:

```text
customer_verified = TRUE
AND
all 7 checklist items are answered
AND
no disqualifying condition exists
AND
no transfer condition exists
AND
customer remains in the fresh-loan flow
```

### Handoff action

Tell the customer that a senior loan expert will contact them shortly to discuss the next steps and provide exact interest-rate details.

Do not claim that the loan is finally approved. The voice agent only performs preliminary qualification.

---

# 24. Branch Priority / Decision Precedence

The agent must evaluate customer responses consistently.

## Normal response processing

```text
Customer response
      |
      v
Extract all information
      |
      v
Apply latest clear corrections
      |
      v
Check immediate disqualification
      |
      v
Check transfer/loan-transfer intent
      |
      v
Check ambiguity requiring clarification
      |
      v
Find earliest missing checklist item
      |
      v
Ask exactly one next question
```

## Important design note

The official assignment does not define precedence for every possible response containing multiple conflicting branches (for example, an existing loan plus a separate disqualifying condition in the same utterance).

For the first implementation, use this documented precedence consistently:

```text
1. Explicit correction in the latest customer statement
2. Clear disqualification
3. Clear existing-loan / EMI-transfer branch
4. Required clarification
5. Continue qualification
```

This precedence is an implementation decision for consistency, not an additional requirement stated verbatim by the assignment.

---

# 25. Example Complete Happy Path

### Customer profile

```text
Property: Residential
Ownership: Sole
Documents: Original documents available
Loan amount: ₹50 lakh
Occupation: Salaried
Income: Bank
Market value: ₹1 crore
Tenure: 10 years
```

### Expected behavior

```text
Verify customer
-> Confirm customer is available
-> Present LAP offer
-> No existing-loan/EMI-transfer request
-> Ask property type
-> Ask ownership
-> Ask documents
-> Ask loan amount
-> Ask occupation + income mode
-> Ask market value
-> Ask tenure
-> Validate all criteria
-> Handoff to senior loan expert
-> End
```

Expected result:

```text
QUALIFIED FOR PRELIMINARY HANDOFF
```

---

# 26. Test Scenario Matrix

At minimum, test the following scenarios.

| ID | Scenario | Key Input | Expected Result |
|---|---|---|---|
| T01 | Happy path | All eligible values | Final handoff |
| T02 | Agricultural | Agricultural property | Immediate disqualification |
| T03 | Cash income | Salaried + Cash | Immediate disqualification |
| T04 | Cash income | Self-employed + Cash | Immediate disqualification |
| T05 | Missing originals | No original documents | Immediate disqualification |
| T06 | Tenure too short | 2 years | Disqualification |
| T07 | Tenure too long | 20 years | Disqualification |
| T08 | Maximum amount | ₹75 lakh | Continue |
| T09 | Amount above max | ₹90 lakh | Offer ₹75 lakh alternative |
| T10 | Reject max alternative | ₹90 lakh then refuses ₹75 lakh | End call |
| T11 | Joint ownership | Jointly owned | Continue |
| T12 | Existing loan | Existing property loan | Transfer specialist -> End |
| T13 | EMI reduction | Wants EMI reduction | Transfer specialist -> End |
| T14 | Busy customer | In meeting | Callback time -> End |
| T15 | Out-of-order info | Multiple eligibility facts in one answer | Store all; ask first missing |
| T16 | Correction | 10 years -> 12 years | Latest answer replaces prior |
| T17 | Contradiction | Residential -> Agricultural | Latest clear answer -> disqualify |
| T18 | Ambiguous documents | "Probably somewhere" | Clarify |
| T19 | Interest-rate diversion | Asks exact rate | No fabrication; return to flow |
| T20 | Interruption | Customer interrupts | Address briefly; resume from state |
| T21 | Unrelated question | Branch/location question | RAG answer if available; otherwise no fabrication |
| T22 | Multi-fact response | Property + ownership + value + amount together | Extract all and skip repeats |

---

# 27. Adversarial Testing

The agent should also be tested against natural, messy customer speech.

## Fillers

```text
"Umm... yeah, it's residential."
```

Expected: identify Residential.

## Multiple facts

```text
"It's my own house, original papers are at home, and I need 40 lakhs."
```

Expected: extract all three relevant facts.

## Correction

```text
"I want 10 years... actually 12."
```

Expected: tenure = 12.

## Contradiction

```text
"It's residential... no, sorry, agricultural."
```

Expected: latest clear answer = Agricultural -> disqualify.

## Diversion

```text
"Before we continue, what's the interest rate?"
```

Expected: brief answer from available context or defer to senior expert; resume qualification.

## Interruption

```text
"Wait, what documents do you need?"
```

Expected: answer document requirement, preserve state, continue.

---

# 28. Conversation Style Rules

The voice agent should:

- Sound professional, warm, and advisory.
- Use short conversational turns.
- Ask one primary question at a time.
- Avoid sounding like a survey or interrogation.
- Acknowledge useful customer information before moving forward.
- Avoid repeating information the customer already supplied.
- Avoid unnecessary explanations.
- Avoid inventing facts.
- Never claim final loan approval.
- Never continue the fresh-loan checklist after a confirmed transfer branch.
- Never continue the checklist after immediate disqualification.

---

# 29. Completion Criteria

The solution is ready for prompt implementation only when all of the following are defined and tested:

```text
[ ] Customer verification gate
[ ] Busy/callback branch
[ ] Offer presentation
[ ] Existing-loan / EMI-transfer branch
[ ] Seven-item checklist
[ ] Internal state model
[ ] Out-of-order extraction
[ ] Latest-answer correction handling
[ ] Ambiguity handling
[ ] Immediate disqualification
[ ] >₹75 lakh negotiation branch
[ ] Tenure validation
[ ] Occupation + income validation
[ ] RAG/no-fabrication policy
[ ] Language behavior
[ ] Agent gender consistency
[ ] Final handoff gate
[ ] Call termination rules
[ ] Happy-path test
[ ] Failure-path tests
[ ] Adversarial tests
```

---

# 30. Recommended Build Sequence

```text
PHASE 1 — Requirements
    |
    v
PHASE 2 — Business Rules
    |
    v
PHASE 3 — State Model
    |
    v
PHASE 4 — Decision Precedence
    |
    v
PHASE 5 — System Prompt
    |
    v
PHASE 6 — Voice Platform Implementation
    |
    v
PHASE 7 — Happy-Path Testing
    |
    v
PHASE 8 — Failure-Path Testing
    |
    v
PHASE 9 — Adversarial Testing
    |
    v
PHASE 10 — Prompt Refinement
    |
    v
PHASE 11 — Recordings + Transcripts
    |
    v
PHASE 12 — Final Submission
```

---

# 31. Submission Package

## Required

1. Complete System Prompt text.
2. Public link to call recording and call logs.
3. Audio recordings.
4. Transcripts.

## Recommended additional artifact

A short approach document describing:

- conversation architecture,
- state management,
- eligibility logic,
- edge-case handling,
- testing methodology,
- major prompt-design decisions.

---

# 32. Source-of-Truth Rule

When designing the actual agent, use the **official assignment** as the final authority for hard requirements.

The preparation guide can be used for implementation ideas, examples, test cases, and design recommendations, but it must not introduce unsupported business rules.

### Explicit examples

```text
Supported:
- Agricultural property -> disqualify
- Cash income -> disqualify
- Tenure 3–15 years -> eligible
- Joint ownership -> eligible
- Loan amount above ₹75 lakh -> offer ₹75 lakh alternative
- Existing loan / EMI reduction -> specialist branch

Not supported by assignment:
- Inventing a minimum property market value
- Inventing an exact interest rate
- Claiming final loan approval during qualification
```

---

# 33. Core Principle

> **Extract first. Validate second. Update state third. Ask the next missing question fourth.**

This principle should guide the final System Prompt and the testing strategy.

