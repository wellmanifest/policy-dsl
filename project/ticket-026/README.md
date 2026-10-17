# Ticket 026: Pass explicit nullable keyword to _require_string in sales reference engine

- **ID**: ticket-026
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-17

## Goal and scope

Pass explicit nullable keyword to _require_string in sales reference engine so the repository passes AST performance audit and standard pack conformance checks with zero findings.

## Acceptance criteria

- [x] AC-01: Remediate all `PERF-AUDIT-*` findings in `policy-dsl` (`audit_repository` returns `0` findings).
- [x] AC-02: Align `.governance/standard-adoption.json` (`standard_pack_check.py` returns `findings=0`) and pass `pytest -q`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
