# Home Credit LAP Voice Agent — Requirements Analysis

## Source
This document is derived from the uploaded:
- `SalesAgents AI Hiring Assignment - AI_voice_agent_prep.pdf`
- `Pasted text(20261008-130255).txt`

The official assignment is the source of truth. The preparation guide is used to expand implementation guidance.

## 1. Objective

Build an AI Voice Agent for Home Credit that contacts existing valued customers about a pre-approved Loan Against Property (LAP) offer, performs a preliminary eligibility check, and hands qualified leads to a senior human loan expert.

The conversation must be natural, professional, and advisory.

## 2. Required Call Stages

1. Greeting and customer identification
2. Busy-customer handling
3. LAP offer presentation
4. Existing-loan / EMI-reduction detection
5. Sequential eligibility collection
6. Eligibility validation
7. Final handoff for qualified customers
8. Call termination

## 3. Seven Eligibility Data Points

| # | Data Point | Requirement |
|---|---|---|
| 1 | Property Type | Residential, Commercial, or Industrial |
| 2 | Ownership | Sole or Joint |
| 3 | Original Documents | Must be available for verification |
| 4 | Loan Amount | Maximum ₹75,00,000 |
| 5 | Occupation + Income Mode | Salaried/Self-employed; income must be through Bank |
| 6 | Market Value | Capture estimated current market value |
| 7 | Tenure | 3–15 years |

## 4. Mandatory Business Rules

### Property Type
- Residential: eligible
- Commercial: eligible
- Industrial: eligible
- Agricultural: not eligible

### Ownership
- Sole: eligible
- Joint: eligible

### Documents
- Original documents available: proceed
- Original documents unavailable: not eligible

### Loan Amount
- ≤ ₹75 lakh: proceed
- > ₹75 lakh: explain ₹75 lakh maximum and ask whether the customer wants to proceed with ₹75 lakh
- If customer declines: end call

### Occupation and Income
- Salaried + Bank: eligible
- Self-employed + Bank: eligible
- Salaried + Cash: not eligible
- Self-employed + Cash: not eligible

### Market Value
- Capture the estimate.
- The assignment does not specify a minimum market-value threshold.
- Do not invent one.

### Tenure
- 3–15 years: eligible
- Below 3 years: not eligible
- Above 15 years: not eligible

## 5. Conversation Requirements

The agent must:
- Handle natural full-sentence responses.
- Handle fillers and interruptions.
- Extract multiple facts from one customer response.
- Remember facts supplied out of order.
- Avoid asking for information already clearly provided.
- Return to the first unanswered checklist item after a diversion.

## 6. Transfer Branch

If the customer:
- already has an existing loan on the property, or
- wants to reduce an existing EMI,

the agent must:
1. Acknowledge the situation.
2. Explain that a loan-transfer specialist will contact them.
3. End the call.

The normal fresh-loan eligibility flow should not continue.

## 7. Busy Branch

If the customer is busy:
1. Acknowledge.
2. Ask for a convenient callback time.
3. Capture the callback time.
4. End the call.

## 8. Final Handoff Gate

The agent may hand off only when:
- all seven eligibility items are answered,
- no mandatory eligibility criterion has failed,
- the customer is not in the existing-loan/EMI-transfer branch.

The senior loan expert provides exact interest-rate details.

## 9. Prompt Variables

The System Prompt must account for:
- `company_name`
- `customer_name`
- `agent_name`
- `agent_gender`
- `current_date`
- `current_day`
- `current_time`
- `additional_context_from_rag`
- `language_to_speak`
- `conversation_history`
- `customer_utterance`

## 10. Submission Requirements

The official assignment requests:
1. System Prompt text
2. Public link to call recording and call logs
3. Audio
4. Transcript

An approach document is recommended by the preparation guide but is optional according to that guide.
