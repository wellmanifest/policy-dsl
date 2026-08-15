# Ticket 003: Harden Policy IR validate_ir uniqueness and state refs

- **ID**: ticket-003
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Domknąć `validate_ir` tak, aby hand-crafted / candidate IR nie omijał kontroli
unikalności i referencji stanów, które `semantic_checks` robi tylko na ścieżce
parse. Poprawić fixture `CONTRIBUTING.md` (NEXT bez STATE). Użyć remediation
DSL + todo2code do wykrycia kolejnych luk poza tym ticketem.

## Acceptance criteria

- [x] AC-01: Unit testy przechodzą, w tym przypadki duplicate binding/env/
      transition oraz undeclared NEXT/transition state.
- [x] AC-02: `self-test` i `validate-markdown` dla CONTRIBUTING.md przechodzą
      po dodaniu deklaracji STATE.
- [x] AC-03: Nowe fixture invalid odrzucają się z `POLICY-SEMANTIC-001`.
- [x] AC-04: Remediation intent + todo2code projections są zwalidowane; lista
      dalszych luk zapisana w ticket evidence.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to execute Policy IR harden and use todo2code/other DSLs to
discover further fixes authorizes this ticket within `intent.json` allowedPaths.
