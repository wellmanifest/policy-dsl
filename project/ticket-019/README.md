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
- [x] AC-02: Governance and conformance pass; baseline test failures are distinguished.
- [ ] AC-03: Protected publication and external completion are verified without rewriting historical ticket Markdown.

## Validation and boundary

Goal check: no drift against published 0.20.28. Policy conformance: PASS. Initial unit suite: 44/45, matching main. After independent PR #25 merged, the branch was refreshed to base 5551a57b6ef1ff7ce9a33798262e8e9af6aae4c1 and all 51 tests pass. The published managed base owns WIP and timing defaults (4 active tickets per workstream, 30-minute checkpoint interval, 120-minute active budget); the validator rejects overriding those standard-owned fields. No application data is migrated; historical changes from #25 are inherited, not authored by this adoption. Fresh exact-head publication remains pending.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
