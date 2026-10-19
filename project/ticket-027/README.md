# Ticket 027: Add compact policy constructs and compaction analyzer

- **ID**: ticket-027
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-19

## Goal and scope

Extend Policy DSL v1 (`wellmanifest.policy/v1`) with deterministic compact desugaring constructs (`STATES [...]`, `TRANSITION [...] -> TARGET`, `SCOPE WHEN ... END`, `TEMPLATE <NAME> ... END` + `DO APPLY_TEMPLATE <NAME>`) that compile without loss into closed Policy IR v1 (`wellmanifest.policy/ir/v1`), add a static compaction analyzer (`audit_compaction` / CLI `audit`), and document the cross-standard policy compaction architecture (`docs/POLICY_COMPACTION_ARCHITECTURE.md`).

## Acceptance criteria

- [x] AC-01: Implement `STATES [...]`, `TRANSITION [...] -> TARGET`, `SCOPE WHEN ... END`, and `TEMPLATE ... END` / `DO APPLY_TEMPLATE` in `tests/policy_dsl_check.py` and `spec/policy-dsl.ebnf` with 100% closed `wellmanifest.policy/ir/v1` equivalence.
- [x] AC-02: Add `audit_compaction` and CLI `audit` command to detect `POLICY-COMPACT-001..004` anti-patterns and pass `pytest -q`, `./project/governance-check.sh`, and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
