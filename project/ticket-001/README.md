# Ticket 001: Define the Policy DSL v1 standard

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
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
- [x] AC-02: The governance package is pinned to published revision
  `769183ca27593af1d166acee11bc9e37decf9870`.
- [x] AC-03: Exactly one local seed commit contains governance carriers,
  root project metadata and this ticket, with no implementation files.
- [x] AC-04: The resulting commit becomes the accepted base for later,
  ordinary integration implementation.
- [x] AC-05: Normative EBNF defines metadata, rules, typed conditions/actions,
  assertions, states and transitions without shell execution.
- [x] AC-06: A request/candidate-only GBNF constrains LLM generation and cannot
  generate authority, execution envelopes or arbitrary shell commands.
- [x] AC-07: A closed JSON Schema defines canonical Policy IR v1.
- [x] AC-08: A deterministic reference parser produces typed condition/action
  AST and shared positive/negative conformance fixtures.
- [x] AC-09: A `wellmanifest.dsl/manifest/v1` binds grammar, schema, parser,
  fixtures and documentation by SHA-256 and pins composed standards.
- [x] AC-10: The deterministic runtime validates standalone policy files and
  canonical Policy DSL fences embedded in `CONTRIBUTING.md` without executing
  actions or interpreting unrelated Markdown and shell examples.
- [x] AC-11: Governance, unit, invalid-fixture, manifest, standards-lock,
  secret and exact-diff checks pass with recorded evidence.
- [ ] AC-12: The reviewed standard can be published at an immutable revision
  for adoption by `new-project` and target-owned repositories.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Non-goals

- No effectful policy executor, daemon or generic shell adapter.
- No unreviewed merge, mutable dependency reference or publication bypass.
- No implementation changes in sibling repositories from this ticket; adopter
  work remains isolated in each target repository.

## Authorized delivery boundary

- Seed baseline: `main@f2008575ca1b2d45cd898cc2aa1c50e4e4a54f14`.
- Implementation branch: `ticket/001-policy-dsl-standard`.
- Complexity: L; at most 15 implementation files, 5 components, 3 public
  interfaces and no runtime dependencies.
- Implementation commits: `1f3ed97`, `adad427` and `09b5500`; exactly 15
  implementation files and zero runtime dependencies.
