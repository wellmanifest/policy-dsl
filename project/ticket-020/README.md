# Ticket 020: Publish sales catalog, request and decision v2 JSON Schemas

- **ID**: ticket-020
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Session execution authorization**: user requested implementation of wellmanifest/policy-dsl#23 follow-ups and autonomous execution (2026-09-14)
- **Created**: 2026-09-14
- **Depends on**: ticket-018 (PR #25, merged as `5551a57`)

## Goal and scope

After ticket-018 the evaluator emits `subactor.sales/decision/v2` and reads
`subactor.sales/catalog/v2`, but `schemas/sales-*.schema.json` still describe v1
(twin fields, `label_pl`, Twin Plus report). This ticket publishes the v2
schemas under versioned `$id` values and adds a dependency-free test that
validates the catalog, all accepted request identifiers and every decision in
the matrix against them.

The branch also carries the ticket-018 closure record, because a closure-only
PR is rejected with `GOV-MATERIAL-001`.

## Acceptance criteria

- [ ] AC-01: full unit suite passes, including schema conformance.
- [ ] AC-02: `./project/governance-check.sh` passes on the published head.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-claude.md](ai-claude.md)
