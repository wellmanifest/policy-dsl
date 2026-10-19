# Ticket 028: Compact reference policy profiles and refine compaction audit

- **ID**: ticket-028
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-19

## Goal and scope

Refactor the four reference policy profiles (`subactor-production-server.policy`, `subactor-rpi5.policy`, `subactor-sales.policy`, `subactor-llm-credential.policy`) to use Policy DSL v1 compact constructs (`STATES`, `SCOPE WHEN`, `TEMPLATE` / `DO APPLY_TEMPLATE`) and update `audit_compaction` in `tests/policy_dsl_check.py` to track uncompacted inline AST nodes so compacted files report `0` compaction findings.

## Acceptance criteria

- [x] AC-01: Compact all four reference `.policy` profiles while preserving closed Policy IR v1 equivalence and passing all profile conformance suites.
- [x] AC-02: Verify `policy_dsl_check.py audit` reports `findings=0` on all four compacted profiles and pass `pytest -q` and `./project/governance-check.sh`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
