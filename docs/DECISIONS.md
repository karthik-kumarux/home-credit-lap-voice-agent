# Decisions Log

| Date       | Topic                            | Decision / Assumption |
|------------|----------------------------------|-----------------------|
| 2026-10-08 | Amount Limit > 75 lakh           | Gap decision: Uses negotiation flow. The Section 8 disqualifier applies only after the customer actively refuses 75 lakh. |
| 2026-10-08 | Verification Failure             | Gap decision: If wrong person/fails verification, reveal nothing, apologize, offer to note a callback time for the right person, and end the call. Add `customer_verified = FALSE` handling to the state model. |
| 2026-10-08 | Occupation Not Detailed          | Gap decision: If occupation is other than salaried or self-employed, do not guess. Ask one clarifying question about income source. If it clearly doesn't fit, end politely as not matching this offer's criteria. |
| 2026-10-08 | Section 24 Precedence            | Gap decision: Section 24 precedence is an implementation decision. Encode it explicitly in the prompt and in the eligibility engine. |
