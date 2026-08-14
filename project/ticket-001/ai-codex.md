---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-001
---
# Participant: codex (AI agent)

## Understanding

The requested result is a new standards-only repository named `policy-dsl`.
The repository is placed at `home=wellmanifest`, has `shape=domain_pack`, uses
`runtimeOwner=wellmanifest`, and adopts `wellmanifest/dsl`,
`wellmanifest/env-dsl` and `wellmanifest/poa` as separately versioned standards.

The request explicitly says to execute the extraction and audit. It therefore
creates `SESSION_EXECUTION_AUTHORIZATION` and authorizes exactly one local
governance seed-baseline commit. It does not authorize remote effects. After
that baseline, this integration ticket owns the standard contracts and
dependency-free conformance parser; production `wellm` integration remains a
separate sibling-repository ticket.

## Execution plan

1. Adopt exact published `wellmanifest/new-project` v0.18.0 through Goal.
2. Create required root carriers and this governance ticket.
3. Verify placement, manifest ownership, absence of implementation and secrets.
4. Commit the exact seed allowlist once and record the resulting HEAD.
5. Define EBNF, GBNF, closed Policy IR Schema and compatibility semantics.
6. Implement a dependency-free typed conformance parser under `tests/`.
7. Bind artifacts in the DSL manifest and run conformance/governance checks.
8. Publish through exact-head review, then let each adopter pin the immutable
   Policy DSL revision in its own governance ticket.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to execute this work.
- Adopted the published governance package at exact revision
  `769183ca27593af1d166acee11bc9e37decf9870`.
- Created only root/governance carriers and customized workstream ownership for
  the future standard-contract and parser tickets.
- Created the one local seed commit
  `f2008575ca1b2d45cd898cc2aa1c50e4e4a54f14` with no implementation paths or
  remote effects, then created `ticket/001-policy-dsl-standard` from that base.
- The follow-up request explicitly requires `policy-dsl` to become an immutable
  dependency of `new-project` and to validate repositories containing
  `CONTRIBUTING.md`. This ticket now owns the Markdown conformance surface;
  sibling adoption remains isolated in target-owned tickets after publication.
- Defined Policy DSL v1 EBNF, the safe proposal-only GBNF and the closed Policy
  IR Schema while keeping `policy-sh@1` as a compatibility alias and document
  `VERSION 13` as an independent profile revision.
- Implemented the dependency-free conformance parser. Conditions, actions,
  assertions, next guards and action guards are recursive typed nodes; no
  clause is retained as opaque source text and no execution adapter exists.
- Added a deterministic Markdown selector and verified the complete current
  `wellmanifest/new-project/CONTRIBUTING.md` carrier while ignoring unrelated
  Markdown, Bash examples and embedded independent DSL documents.
- Added shared valid/invalid fixtures, unit/self tests, architecture/flow
  documentation and an artifact-digest manifest pinned to exact DSL, Env DSL
  and POA revisions.
- Added direct help pages for every declared syntax, semantic and critical
  security diagnostic and bound the Markdown fixture into conformance.
- Verified the pinned Env DSL contract and digest from its public exact Git
  revision before Policy DSL publication.
- Created the public repository and pull request, enabled fail-closed `main`
  protection, and left merge blocked on independent exact-head review.
- Hardened dependency-free candidate validation to enforce document,
  environment, collection, rule, state and transition types across the entire
  closed Policy IR contract.

## Blockers

- No implementation blocker. AC-12 remains a publication-boundary task until
  an immutable remote revision and exact-head trusted review exist.
- Protected publication is in scope under the continuation request, but its
  exact-head trusted approval remains independent evidence. Destructive action
  and secret access remain outside authority.
- Pull request #1 has a green remote lifecycle check and no approval yet; the
  agent cannot manufacture or self-issue trusted review evidence.
