# Ticket 001: Define the Policy DSL v1 standard

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Create the standalone `wellmanifest/policy-dsl` domain pack and define Policy
DSL v1 as the canonical language behind `policy-sh@1` and
`wellmanifest.new-project.contributing`. The contract includes a normative
grammar, constrained LLM grammar, closed Policy IR, manifest, valid/invalid
fixtures and a dependency-free conformance parser. The one unborn-HEAD seed
commit remains governance-only; ordinary implementation begins from that base.

## Acceptance criteria

- [x] AC-01: The user's request to create and implement the repository records
  `SESSION_EXECUTION_AUTHORIZATION` and the narrow unborn-HEAD seed exception.
- [ ] AC-02: The governance package is pinned to published revision
  `769183ca27593af1d166acee11bc9e37decf9870`.
- [ ] AC-03: Exactly one local seed commit contains governance carriers,
  root project metadata and this ticket, with no implementation files.
- [ ] AC-04: The resulting commit becomes the accepted base for later,
  ordinary integration implementation.
- [ ] AC-05: Normative EBNF defines metadata, rules, typed conditions/actions,
  assertions, states and transitions without shell execution.
- [ ] AC-06: A request/candidate-only GBNF constrains LLM generation and cannot
  generate authority, execution envelopes or arbitrary shell commands.
- [ ] AC-07: A closed JSON Schema defines canonical Policy IR v1.
- [ ] AC-08: A deterministic reference parser produces typed condition/action
  AST and shared positive/negative conformance fixtures.
- [ ] AC-09: A `wellmanifest.dsl/manifest/v1` binds grammar, schema, parser,
  fixtures and documentation by SHA-256 and pins composed standards.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Non-goals

- No effectful policy executor, daemon or generic shell adapter.
- No remote repository creation, push, pull request, merge, tag or release.
- No modification of sibling repositories.
