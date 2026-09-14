---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-017
---
# Participant: claude (AI agent)

## Understanding

A policy carrier must not lose normative text silently. The reference selector
needs a closed, deterministic classification for every `dsl` fence.

## Execution plan

1. Classify fences in `extract_markdown` and fail closed on the remainder.
2. Add valid and invalid carrier fixtures, unit tests and a self-test case.
3. Update section 3.2, the `POLICY-SYNTAX-001` runbook and manifest bindings.

## Actual changes

- `tests/policy_dsl_check.py`: fence classification, line-numbered diagnostics.
- `tests/test_policy_dsl.py`: four carrier tests.
- `examples/valid/mixed-carrier.md`, `examples/invalid/unclassified-dsl-fence.md`.
- `spec/POLICY_DSL.md` section 3.2 and `docs/ERROR/POLICY-SYNTAX-001.md`.
- `dsl-manifest.json`: new artifacts, conformance entries, refreshed digests.

## Publication

- Merged through PR #22 as `d723271` after Validator approval of head `90558cb`.

## Blockers

- None. Follow-ups: the manifest's LLM boundary gap; stale offer pin (#23).
