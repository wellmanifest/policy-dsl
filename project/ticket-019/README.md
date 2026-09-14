# Ticket 019: Adopt external ticket completion receipts and published governance

- **ID**: ticket-019
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: owner approved closing PR #24 without merge and adopting external ticket completion on 2026-09-14. Publication through independent Validator is authorized; this note is not merge evidence.

Adopt published wellmanifest/new-project 0.20.28 through Goal. Preserve DSL source, sales work in #25, required checks and unmerged #24 history. Completion uses independently verified external merge receipts rather than carrier-only commits.

## Acceptance criteria

- [x] AC-01: Immutable published adoption reports no drift.
- [ ] AC-02: Governance and conformance pass; baseline test failures are distinguished.
- [ ] AC-03: Protected publication and external completion are verified without rewriting historical ticket Markdown.

## Validation and boundary

Goal check: no drift against published 0.20.28. Policy conformance: PASS. Unit suite: 44/45, with the identical main sales-profile error tracked in #23 and separately addressed by #25. This adoption does not migrate application data: historical Markdown stays unchanged, and the managed runtime adds support for externally recorded merge receipts. Exact-head publication is pending.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
