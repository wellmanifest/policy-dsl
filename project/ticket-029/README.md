# Ticket 029: Compact sales policy profile with TEMPLATE and verify zero compaction findings

- **ID**: ticket-029
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-19

## Goal and scope

Compact `profiles/sales/subactor-sales.policy` by extracting the shared `EFFECTIVE_PROMO ""` + `PROMOTION_PRESENTATION "HIDDEN"` directive bundle into `TEMPLATE HIDE_INELIGIBLE_PROMO`, sync `dsl-manifest.json`, and add a regression test in `tests/test_sales_profile.py` verifying that all 4 reference `.policy` profiles report `0` compaction findings.

## Acceptance criteria

- [x] AC-01: Extract `TEMPLATE HIDE_INELIGIBLE_PROMO` in `profiles/sales/subactor-sales.policy` while preserving 100% `subactor.sales/decision-matrix/v2` equivalence.
- [x] AC-02: Verify `findings == 0` across all 4 reference `.policy` profiles in `tests/test_sales_profile.py`, sync `dsl-manifest.json`, and pass `pytest -q` and `./project/governance-check.sh`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
