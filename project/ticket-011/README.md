# Ticket 011: Align dsl standardsLock revision and digest guard

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-16

## Goal and scope

Align `dsl-manifest.json` `standardsLock` revision for `wellmanifest.dsl` to
the current published dsl HEAD. Keep the existing contract digest. Extend
manifest tests so artifact and lock-contract digests fail closed. Do not invent
a `wellm` pin.

## Acceptance criteria

- [x] AC-01: `wellmanifest.dsl` lock revision is `0e088f9efa06a903d1674f42b8ac6afaa0fdf071`.
- [x] AC-02: Contract digest stays `sha256:34d356b76bbd483372df84bb986e15bb84e9c1f8b11b7dc9e3a6c7276c85ed13`.
- [x] AC-03: Tests reject artifact digest drift and require the dsl lock entry; no wellm entry.
- [x] AC-04: No `CHANGELOG.md` / `TODO.md` edits in this ticket.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to continue sequential TODO and publish via subactor validator
authorizes this ticket.
