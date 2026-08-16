# Ticket 013: Announce compatibility end and freeze legacy catalog writes

- **ID**: ticket-013
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-16

## Goal and scope

Announce the sales compatibility end date (`2026-08-16`) and fail closed if
catalog plans write `actions_included` or display name `Actions Plus`. Keep
read aliases and `legacy_display_names`. Close ticket-012 as DONE.

www-sub-actor observational adapter is deferred (active tickets 019/045/046).

## Acceptance criteria

- [x] AC-01: `compatibility.write_freeze_date` is `2026-08-16`.
- [x] AC-02: `load_catalog()` rejects written `actions_included` / `Actions Plus`.
- [x] AC-03: Read aliases and `legacy_display_names` remain required.
- [x] AC-04: ticket-012 is `DONE`/`DONE`.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to continue sequential TODO and publish via subactor validator
authorizes this ticket.
