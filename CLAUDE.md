# Project Conventions & Rules

## Core Rules
1. **Source of Truth**: `HOME_CREDIT_LAP_VOICE_AGENT_LOGIC.md` is the absolute source of truth. Do NOT invent business rules, rates, min/max values, approvals, or exceptions not specified there.
2. **Conversation Precedence**: Treat the following precedence as strict implementation rules: 
   (1) Correction -> (2) Immediate Disqualification -> (3) Specialist Transfer -> (4) Clarification -> (5) Missing checklist item.
3. **Latest Correction Wins**: If a customer contradicts themselves, always use their latest clear answer.
4. **No invented facts**: Do not invent rates, metrics, or pretend the loan is finally approved.
5. **No guessing occupations**: If an occupation is not strictly "Salaried" or "Self-employed", do not guess. Ask one clarifying question about income source; if it fails to match criteria, politely disqualify them.

## Definition of Done
A feature or phase is only "done" when:
- It maps exactly to the blueprint.
- It passes the deterministic Python eligibility engine (acts as an infallible oracle).
- Edge cases (T01-T22 paths) have tests that assert against the `src/` core state and pass.

## Git Protocol
- Use small, atomic, conventional commits (e.g., `feat:`, `fix:`, `chore:`, `test:`).
