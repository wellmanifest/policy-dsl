# Ticket 012: Export golden subactor.sales/decision/v1 consumer fixtures

- **ID**: ticket-012
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-16

## Goal and scope

Publish a frozen consumer fixture of `subactor.sales/decision/v1` from the
reference `decide()` matrix so backend/frontend/PHP can compare observationally
without a second evaluator. Close ticket-011 as DONE. No runtime adapter wiring.

## Acceptance criteria

- [x] AC-01: `examples/sales/decisions/matrix.v1.json` equals `matrix()`.
- [x] AC-02: `export-decisions --check` fails closed on fixture drift.
- [x] AC-03: Unit tests pass; each case is `subactor.sales/decision/v1`.
- [x] AC-04: Docs point consumers at the fixture and `decide` CLI.
- [x] AC-05: ticket-011 is `DONE`/`DONE`.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to continue sequential TODO and publish via subactor validator
authorizes this ticket.
