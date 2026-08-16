# Ticket 004: Re-adopt new-project v0.18.1 immutable locks

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-16

## Goal and scope

Replace the stale `wellmanifest/new-project` **0.18.0** managed governance
package with the final published **v0.18.1** package at commit
`16f7aea148a7f979e5c5abdfd4bc112224904d36`. That upgrade refreshes managed digests and live-host schema ids via Goal's
atomic adoption lock. Closed `domainContracts` lands only in a later published
new-project release (post ticket-085); do not invent it under 0.18.1.

Also close integrated **ticket-003** housekeeping (`DONE` / `DONE`) and keep
the `dsl-manifest.json` `standardsLock` revision for `wellmanifest.dsl` aligned
with the contract digest already pinned. Do **not** invent a `wellm` pin: there
is no final published wellm release and no Policy DSL runtime dependency on it
yet.

## Acceptance criteria

- [x] AC-01: Source commit is the peeled commit of final GitHub release
      `v0.18.1`, and Goal accepts it as a published adoption source.
- [x] AC-02: `goal governance adopt --check` reports the reviewed managed
      upgrade before writes; `--upgrade` installs the same atomic set.
- [x] AC-03: `.governance/manifest.lock.json` verifies every managed digest and
      records `wellmanifest/new-project` version `0.18.1` at the exact source
      SHA; local extendable manifest retains `domainContracts.mode=none`.
- [x] AC-04: `./project.sh` / governance gate and unit tests pass on the exact
      implementation head.
- [x] AC-05: ticket-003 is closed `DONE` / `DONE`; `TODO.md` marks the
      new-project immutable-lock item done and records wellm as deferred.
- [x] AC-06: Document that `dsl-manifest.json` digest/revision repair stays
      deferred to an integration ticket (pre-existing main drift after PR #6).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-composer.md](ai-composer.md)

## SESSION_EXECUTION_AUTHORIZATION

User request to continue remaining policy-dsl work (immutable locks /
housekeeping) authorizes this ticket within `intent.json` allowedPaths.
Trusted merge remains independent evidence; this agent must not self-approve.
