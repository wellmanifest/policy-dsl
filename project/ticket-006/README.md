# Ticket 006: Add profiles path ownership to integration workstream

- **ID**: ticket-006
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-16

## Goal and scope

Add `profiles/**` to the extendable governance manifest `coordination.workstreams.integration.ownedPaths`
so sales profile work can pass workstream ownership checks. Close integrated
ticket-004 as `DONE`/`DONE` on the default branch.

## Acceptance criteria

- [x] AC-01: `.governance/manifest.json` integration ownedPaths includes `profiles/**`.
- [x] AC-02: ticket-004 is `DONE`/`DONE`.
- [x] AC-03: `./project.sh` GOV-PASS on the ticket head.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to continue, test and fix authorizes this governance slice.
