# Ticket 025: Configure dsl-manifest decisionProtocol to none per DSL-LLM-001

- **ID**: ticket-025
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-06

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: On 2026-10-06 user requested continuous governance resolution and standard alignment across all repositories.
Align `dsl-manifest.json` LLM boundaries with `DSL-LLM-001` specification:
- Set `mode: "none"`, `decisionProtocol: "none"`, `modelAuthority: "none"`, `requestSchemas: []`, `responseSchemas: []`.
- Reconcile historical ticket statuses (`ticket-019`, `ticket-023`) to `DONE`.

## Acceptance criteria

- [ ] AC-01: Update `dsl-manifest.json` to include valid `decisionProtocol: "none"` and `mode: "none"` passing `dsl_check.py`.
- [ ] AC-02: Reconcile historical merged ticket statuses to DONE.
- [ ] AC-03: Governance and validation checks pass cleanly with 0 errors and 0 warnings.

## Participants

- Human participant: user via chat authorization.
- Agent participant: Antigravity
