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

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
