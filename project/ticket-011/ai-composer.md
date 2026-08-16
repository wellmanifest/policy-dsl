---
participant-id: agent:composer
participant: composer
role: agent
ticket: ticket-011
---
# Participant: composer (AI agent)

## Understanding

To be completed after reading human-owned input and the ticket preprompt.

## Execution plan

1. Validate the ticket scope and acceptance evidence before implementation.

## Actual changes

- Bumped `wellmanifest.dsl` standardsLock revision and `$schema` pin to
  `0e088f9efa06a903d1674f42b8ac6afaa0fdf071`; kept contract digest.
- Extended `tests/test_manifest.py` to fail closed on lock/contract drift
  and reject an invented wellm pin.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
